from langchain_ollama import ChatOllama
from browser_use import Agent
from pydantic import SecretStr
from dotenv import load_dotenv

import os
import asyncio

load_dotenv()

# Initialize the model
llm=ChatOllama(base_url="https://ollama-570351480416.us-central1.run.app", model="deepseek-r1:8b", num_ctx=32000)

async def main():
    # Create agent with the model
    agent = Agent(
        task="go to google.com, accept all cookies and type 'OpenAI' click search and give me the first url",
        llm=llm,
        use_vision=True
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
