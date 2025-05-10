# Multi agent tool

## Setup
```
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python -m certifi
set SSL_CERT_FILE=YOUR_PATH\agents\.venv\lib\site-packages\certifi\cacert.pem

# Copy .env.sample, paste it as .env and update it accordingly
```

## Run
```
# Go to http://localhost:8000
adk web

uvicorn main:app --reload
```

## Create a new agent project
```
agent-starter-pack create simple-agent -a adk_base

# Create with specific agent, deployment target, region, and include data ingestion with Vertex AI Search
agent-starter-pack create rag-agent -a agentic_rag -d cloud_run --region us-central1 -i -ds vertex_ai_search
```

### References
- https://google.github.io/adk-docs/get-started/
- https://google.github.io/adk-docs/agents/multi-agents/
- https://github.com/GoogleCloudPlatform/agent-starter-pack

