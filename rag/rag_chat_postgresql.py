import os
import argparse
import requests
from urllib.parse import urlparse, parse_qs
from typing import Any, List, Mapping, Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM

# --- Configuration ---
# Load from environment variables for Cloud Run compatibility
# Example: postgresql+psycopg2://user:password@host:port/dbname
CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING")
GEMMA_URL = os.getenv("GEMMA_URL")
COLLECTION_NAME = "rag_documents"
DATA_DIR = "docs"

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
            pass  # Stop sequences not handled in this simple implementation

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        full_url = f"{self.endpoint_url}?key={self.api_key}"

        try:
            response = requests.post(full_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"API request error: {e}")
        except (KeyError, IndexError) as e:
            raise HTTPException(status_code=500, detail=f"API response parsing error: {e}")

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"endpoint_url": self.endpoint_url, "api_key": self.api_key}

# --- FastAPI Application ---

app = FastAPI(
    title="RAG Chat API with PostgreSQL",
    description="An API to chat with your documents, using a PostgreSQL vector store."
)

# --- Pydantic Models for API ---

class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class IngestResponse(BaseModel):
    message: str
    documents_added: int
    text_chunks_created: int

# --- Global Objects ---
# These are initialized on startup
llm = None
vector_store = None
qa_chain = None

@app.on_event("startup")
def startup_event():
    """
    Initializes the LLM, vector store, and QA chain when the application starts.
    """
    global llm, vector_store, qa_chain

    if not CONNECTION_STRING or not GEMMA_URL:
        raise RuntimeError("Required environment variables POSTGRES_CONNECTION_STRING or GEMMA_URL are not set.")

    # 1. Initialize LLM
    try:
        parsed_url = urlparse(GEMMA_URL)
        query_params = parse_qs(parsed_url.query)
        endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        api_key = query_params.get('key', [None])[0]
        if not api_key:
            raise ValueError("API key not found in GEMMA_URL.")
        llm = CustomGemmaLLM(endpoint_url=endpoint, api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Failed to parse GEMMA_URL and initialize LLM: {e}")

    # 2. Initialize Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # 3. Initialize Vector Store
    vector_store = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    # 4. Create QA Chain
    retriever = vector_store.as_retriever(search_kwargs={'k': 4})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    print("Application startup complete. Ready to serve requests.")


@app.post("/ingest", response_model=IngestResponse)
def ingest_documents():
    """
    Loads, splits, and embeds documents from the DATA_DIR, storing them in PostgreSQL.
    This is an idempotent operation.
    """
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized.")

    print(f"Starting document ingestion from: {DATA_DIR}")
    documents = []
    loaders = {
        "pdf": (PyPDFLoader, "**/*.pdf"),
        "word": (UnstructuredWordDocumentLoader, "**/*.doc*"),
        "text": (TextLoader, "**/*.txt"),
    }

    for doc_type, (loader_cls, glob_pattern) in loaders.items():
        print(f"Loading {doc_type} files...")
        loader = DirectoryLoader(
            DATA_DIR,
            glob=glob_pattern,
            loader_cls=loader_cls,
            use_multithreading=True,
            show_progress=True,
            silent_errors=True,
        )
        loaded_docs = loader.load()
        if loaded_docs:
            documents.extend(loaded_docs)
        print(f"Found {len(loaded_docs)} {doc_type} documents.")

    if not documents:
        raise HTTPException(status_code=404, detail=f"No documents found in directory '{DATA_DIR}'.")

    print(f"Loaded a total of {len(documents)} documents.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} text chunks.")

    # Add documents to the vector store
    vector_store.add_documents(texts)
    print("Successfully added documents to the PostgreSQL vector store.")

    return IngestResponse(
        message=f"Successfully ingested documents from '{DATA_DIR}'.",
        documents_added=len(documents),
        text_chunks_created=len(texts)
    )


@app.post("/chat", response_model=ChatResponse)
def chat_with_documents(query: ChatQuery):
    """
    Receives a query and returns an answer based on the documents in the vector store.
    """
    if not qa_chain:
        raise HTTPException(status_code=503, detail="QA chain is not initialized. Please wait for startup to complete.")
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        result = qa_chain({"query": query.query})
        sources = [doc.metadata.get('source', 'Unknown') for doc in result["source_documents"]]
        
        return ChatResponse(
            answer=result["result"],
            sources=list(set(sources)) # Return unique source documents
        )
    except Exception as e:
        print(f"An error occurred during chat: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the query.")


@app.get("/")
def root():
    return {"status": "ok", "message": "RAG Chat API is running. See /docs for details."}


# To run this application:
# 1. Set environment variables:
#    export POSTGRES_CONNECTION_STRING="postgresql+psycopg2://user:pass@host:port/db"
#    export GEMMA_URL="YOUR_GEMMA_URL_WITH_KEY"
# 2. Install dependencies:
#    pip install "fastapi[all]" uvicorn psycopg2-binary langchain-postgres
# 3. Run with uvicorn:
#    uvicorn rag_chat_postgresql:app --reload
