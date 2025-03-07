# Browser Use

## Setup
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11
source .venv/bin/activate

uv pip install browser-use
sudo apt-get install libgtk-3-0
npx playwright install-deps
playwright install

# To use Gemini
gcloud services enable generativelanguage.googleapis.com
```

## Run
```sh
# Note: Create a .env file and add GEMINI_API_KEY value

# Run with Gemini
python agent.py
```

## Run with UI

```sh
git clone https://github.com/browser-use/web-ui.git
cd web-ui
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
playwright install

python webui.py --ip 127.0.0.1 --port 7788
```
### References
- https://github.com/browser-use/browser-use?tab=readme-ov-file
- https://docs.browser-use.com/customize/supported-models
- https://github.com/convergence-ai/proxy-lite
