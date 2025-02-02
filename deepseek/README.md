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

# In Google Cloud
gcloud beta run deploy --gpu 1 --image ollama/ollama --port 114434
OLLAMA_HOST=https://ollama-[PROJECT].us-central1.run.app ollama run deepseek-r1:8b
```

### References
- https://github.com/deepseek-ai/DeepSeek-V3
- https://github.com/khanfar/DeepSeek-V3-Windows-Installation-Guide
- https://ollama.com/library/deepseek-r1
- https://www.analyticsvidhya.com/blog/2025/01/run-deepseek-models-locally/
