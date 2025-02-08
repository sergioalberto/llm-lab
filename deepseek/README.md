# DeepSeek lab

```sh
python -m venv venv
source venv/bin/activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

python download_model.py
```


### Run DeepSeek with Ollama in Local
```sh
curl -fsSL https://ollama.com/install.sh | sh
ollama run deepseek-r1:8b

python ollama_app.py
```

### Run DeepSeek with Ollama in Cloud
```sh
# Build and publish image
gcloud builds submit --tag us-east1-docker.pkg.dev/project-1-test-ai/cloud-run-source-deploy/ollama --machine-type e2-highcpu-32

# Deploy the service
gcloud run services replace ollama-deploy.yaml

# Load the Deepseek model
curl --location 'https://ollama-570351480416.us-central1.run.app/api/pull' \
--header 'Content-Type: application/json' \
--data '{
    "name": "deepseek-r1:8b",
    "stream": true
}'

# Let's test it
curl --location 'https://ollama-570351480416.us-central1.run.app/api/chat' --header 'Content-Type: application/json' --data '{
    "model": "deepseek-r1:8b",
    "messages": [
        {
            "role": "system",
            "content": "You are an assistant that helps people"
        },
        {
            "role": "user",
            "content": "What are the advantages of deploying my own LLM?"                                                          }
    ],
    "stream": false
}'
```

### References
- https://github.com/deepseek-ai/DeepSeek-V3
- https://github.com/khanfar/DeepSeek-V3-Windows-Installation-Guide
- https://ollama.com/library/deepseek-r1
- https://www.analyticsvidhya.com/blog/2025/01/run-deepseek-models-locally/
- Ollama API: https://www.postman.com/postman-student-programs/ollama-api/collection/suc47x8/ollama-rest-api?action=share&source=copy-link&creator=41346167

