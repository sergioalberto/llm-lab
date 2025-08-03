# Simple RAG

## Installation and setup
```sh
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

## Run
```sh
python rag_chat.py --gemma_url YOUR_BASE_URL/v1beta/models/YOUR_MODAL:generateContent?key=YOUR_KEY
```

```
sh
# On Windows (Command Prompt)
set POSTGRES_CONNECTION_STRING="postgresql+psycopg2://user:pass@host:port/db"
set GEMMA_URL="YOUR_GEMMA_URL_WITH_KEY"

# On Windows (PowerShell)
$env:POSTGRES_CONNECTION_STRING="postgresql+psycopg2://user:pass@host:port/db"
$env:GEMMA_URL="YOUR_GEMMA_URL_WITH_KEY"

# On Linux/macOS
export POSTGRES_CONNECTION_STRING="postgresql+psycopg2://user:pass@host:5432/db"
export GEMMA_URL="YOUR_GEMMA_URL_WITH_KEY"

uvicorn rag_chat_postgresql:app --reload
```
