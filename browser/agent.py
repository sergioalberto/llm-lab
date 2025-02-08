from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from pydantic import SecretStr
from dotenv import load_dotenv

import os
import asyncio

load_dotenv()

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=os.getenv("GEMINI_API_KEY"))

async def main():
    # Create agent with the model
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=llm
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
