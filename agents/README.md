# Multi agent tool

## Setup
```
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python -m certifi
set SSL_CERT_FILE=YOUR_PATH\agents\.venv\lib\site-packages\certifi\cacert.pem
```

## Run
```
adk web

uvicorn main:app --reload
```


### References
- https://google.github.io/adk-docs/get-started/
