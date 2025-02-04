# DeepSeek lab

```sh
python -m venv venv
source venv/bin/activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

python download_model.py
```


### Run DeepSeek with Ollama
```sh
curl -fsSL https://ollama.com/install.sh | sh
ollama run deepseek-r1:8b

python ollama_app.py

# In Google Cloud with GPU
gcloud beta run deploy --gpu 1 --image ollama/ollama --port 114434
OLLAMA_HOST=https://ollama-[PROJECT].us-central1.run.app ollama run deepseek-r1:8b

# In Google Cloud without GPU
gcloud builds submit --tag us-east1-docker.pkg.dev/project-1-test-ai/cloud-run-source-deploy/ollama --machine-type e2-highcpu-32

gcloud run deploy ollama --image us-east1-docker.pkg.dev/project-1-test-ai/cloud-run-source-deploy/ollama --region us-central1 --concurrency 4 --cpu 8 --set-env-vars OLLAMA_NUM_PARALLEL=4 --max-instances 7 --memory 32Gi --allow-unauthenticated --no-cpu-throttling --service-account 570351480416-compute@developer.gserviceaccount.com --timeout=600
```

### References
- https://github.com/deepseek-ai/DeepSeek-V3
- https://github.com/khanfar/DeepSeek-V3-Windows-Installation-Guide
- https://ollama.com/library/deepseek-r1
- https://www.analyticsvidhya.com/blog/2025/01/run-deepseek-models-locally/
- Ollama API: https://www.postman.com/postman-student-programs/ollama-api/collection/suc47x8/ollama-rest-api?action=share&source=copy-link&creator=41346167

