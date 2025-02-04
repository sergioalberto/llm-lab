FROM ollama/ollama:0.5.7

# Listen on all interfaces, port 8080
ENV OLLAMA_HOST 0.0.0.0:8080

# Store model weight files in /models
ENV OLLAMA_MODELS /models

# Reduce logging verbosity
ENV OLLAMA_DEBUG false

# Never unload model weights from the GPU (if using GPU)
ENV OLLAMA_KEEP_ALIVE -1

# Start Ollama
ENTRYPOINT ["ollama", "serve"]
