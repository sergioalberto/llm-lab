from langchain_openai import ChatOpenAI
from browser_use import Agent
from pydantic import SecretStr
from dotenv import load_dotenv

import os
import asyncio

load_dotenv()

# Initialize the model
llm=ChatOpenAI(base_url='https://api.deepseek.com/v1', model='deepseek-reasoner')

async def main():
    # Create agent with the model
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=llm,
        use_vision=False
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
