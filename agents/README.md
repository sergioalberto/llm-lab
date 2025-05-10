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


### References
- https://google.github.io/adk-docs/get-started/
- https://google.github.io/adk-docs/agents/multi-agents/
