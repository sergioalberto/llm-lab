import os
import argparse
import requests
from urllib.parse import urlparse, parse_qs
from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM

PERSIST_DIRECTORY = "chroma_db"

# --- Custom LLM Class for Gemma Endpoint ---

class CustomGemmaLLM(LLM):
    """Custom LLM class to interact with a Gemma model via a specific REST API endpoint."""
    endpoint_url: str
    api_key: str

    @property
    def _llm_type(self) -> str:
        return "custom_gemma"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            # This is a simple implementation, stop sequences are not handled.
            pass

        # Construct the payload for the Gemini/Gemma API
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        # Construct the full URL with the API key
        full_url = f"{self.endpoint_url}?key={self.api_key}"

        try:
            # Make the POST request
            response = requests.post(full_url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the response to get the generated text
            result = response.json()
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            return text_response

        except requests.exceptions.RequestException as e:
            return f"Error calling the API: {e}"
        except (KeyError, IndexError) as e:
            return f"Error parsing the API response: {e}. Full response: {response.text}"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"endpoint_url": self.endpoint_url, "api_key": self.api_key}


def create_vector_store(data_dir):
    """
    Loads documents from the specified directory, splits them, creates embeddings,
    and builds a FAISS vector store.
    """
    print(f"Loading documents from: {data_dir}")

    documents = []

    # Load PDF files
    print("Loading PDF files...")
    pdf_loader = DirectoryLoader(
        data_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        use_multithreading=True,
        show_progress=True
    )
    documents.extend(pdf_loader.load())

    # Load Word documents (.doc and .docx)
    print("Loading Word documents...")
    doc_loader = DirectoryLoader(
        data_dir,
        glob="**/*.doc*",
        loader_cls=UnstructuredWordDocumentLoader,
        use_multithreading=True,
        show_progress=True
    )
    documents.extend(doc_loader.load())

    # Load Text files
    print("Loading text files...")
    txt_loader = DirectoryLoader(
        data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        use_multithreading=True,
        show_progress=True
    )
    documents.extend(txt_loader.load())

    if not documents:
        print("No documents found. Exiting.")
        return None

    print(f"Loaded {len(documents)} documents.")

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} text chunks.")

    # Create embeddings
    print("Creating embeddings... (This may take a while for the first run)")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # Create FAISS vector store
    print("Creating FAISS vector store...")
    db = FAISS.from_documents(texts, embeddings)

    vectordb = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=PERSIST_DIRECTORY)
    vectordb.persist()

    print("Vector store created successfully.")
    return vectordb


def main():
    """
    Main function to set up and run the RAG chat application.
    """
    parser = argparse.ArgumentParser(description="Chat with your documents using a custom Gemma endpoint.")
    parser.add_argument("--data_dir", type=str, default="docs", help="Directory containing your documents (.pdf, .doc, .txt).")
    parser.add_argument("--gemma_url", type=str, required=True, help="Full URL of your Gemma service endpoint, including the API key.")
    args = parser.parse_args()

    # Create the vector store from your documents
    db = create_vector_store(args.data_dir)
    if not db:
        return

    # Parse the provided URL to extract the endpoint and API key
    try:
        parsed_url = urlparse(args.gemma_url)
        query_params = parse_qs(parsed_url.query)
        endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        api_key = query_params.get('key', [None])[0]

        if not api_key:
            print("Error: API key not found in the provided URL. Please include '?key=YOUR_API_KEY'.")
            return
    except Exception as e:
        print(f"Error parsing the provided URL: {e}")
        return

    # Set up the custom LLM
    llm = CustomGemmaLLM(endpoint_url=endpoint, api_key=api_key)

    # Create the RetrievalQA chain
    retriever = db.as_retriever(search_kwargs={'k': 4})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    print("\n--- Chat with your documents (type 'exit' to quit) ---")
    while True:
        query = input("\n> ")
        if query.lower() == 'exit':
            break
        if not query.strip():
            continue

        try:
            # Get the answer from the chain
            result = qa_chain({"query": query})
            print("\nAnswer:", result["result"])
            print("\nSources:")
            for doc in result["source_documents"]:
                print(f"- {doc.metadata['source']}")

        except Exception as e:
            print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
