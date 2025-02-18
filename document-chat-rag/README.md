# LLama3.3-RAG application

This project leverages a locally Llama 3.3 to build a RAG application to chat with your docs and Streamlit to build the UI.

## Installation and setup

```sh
# Setup ollama on linux 
curl -fsSL https://ollama.com/install.sh | sh
# Pull llama 3.3:70B (need more than 37.8 GiB memory)
ollama pull llama3.3

# Lite version
ollama pull llama3.2:1b

# Setup Qdrant VectorDB
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

## Run Web UI
```sh
streamlit run app.py
```
