import asyncio
from typing import Dict, Any
from google.adk.agents import LlmAgent

# --- Tool Definitions ---
# These are mock tools. In a real scenario, they would interact with actual APIs or databases.

def get_weather(city: str) -> Dict[str, Any]:
    """
    Retrieves the current weather report for a specified city.

    Args:
        city: The name of the city for which to retrieve the weather report.

    Returns:
        A dictionary containing the weather report.
    """
    print(f"[Tool Executing] get_weather(city='{city}')")
    # Mock weather data
    if city.lower() == "paris":
        return {"status": "success", "report": f"The weather in {city} is sunny with a temperature of 22°C."}
    elif city.lower() == "london":
        return {"status": "success", "report": f"The weather in {city} is cloudy with a chance of rain, 18°C."}
    else:
        return {"status": "success", "report": f"The weather in {city} is pleasant, 20°C."} # Generic fallback


def get_country_info(country_name: str, info_type: str) -> Dict[str, Any]:
    """
    Retrieves specific information about a country, such as its capital.

    Args:
        country_name: The name of the country.
        info_type: The type of information requested (e.g., "capital", "population").

    Returns:
        A dictionary containing the requested country information.
    """
    print(f"[Tool Executing] get_country_info(country_name='{country_name}', info_type='{info_type}')")
    # Mock country data
    if country_name.lower() == "france" and info_type.lower() == "capital":
        return {"status": "success", "capital": "Paris"}
    elif country_name.lower() == "uk" and info_type.lower() == "capital":
        return {"status": "success", "capital": "London"}
    else:
        return {"status": "error", "message": f"Information '{info_type}' for country '{country_name}' not found."}

# --- Agent Definitions ---

# 1. Weather Agent
# This agent is specialized in providing weather information using the get_weather tool.
weather_agent = LlmAgent(
    name="WeatherExpert",
    model="gemini-2.0-flash",  # Replace with your desired model
    instruction="You are a weather expert. Your role is to provide current weather conditions for a given city. Use the get_weather tool.",
    description="Provides weather information for cities.",
    tools=[get_weather]
)

# 2. Country Info Agent
# This agent is specialized in providing country-specific information using the get_country_info tool.
country_info_agent = LlmAgent(
    name="CountryExpert",
    model="gemini-2.0-flash", # Replace with your desired model
    instruction="You are a country knowledge expert. Your role is to provide specific information about countries, such as their capital city. Use the get_country_info tool.",
    description="Provides information about countries (e.g., capital city).",
    tools=[get_country_info]
)

# 3. Master Coordinator Agent
# This agent coordinates tasks between the WeatherAgent and CountryInfoAgent.
# It has no tools of its own but delegates tasks to its sub-agents.
root_agent = LlmAgent(
    name="MasterCoordinator",
    model="gemini-2.0-flash", # A more capable model for coordination
    instruction=(
        "You are a master coordinator agent. Your goal is to answer user queries that may require combining information from different experts. "
        "You have a WeatherExpert and a CountryExpert available as sub-agents. "
        "If a question is about the weather in a country's capital, first use the CountryExpert to find the capital, "
        "then use the WeatherExpert to find the weather in that capital city. "
        "Clearly state the information found by each expert."
    ),
    description="Coordinates tasks between weather and country information experts.",
    sub_agents=[weather_agent, country_info_agent]
    # Note: The ADK handles how the coordinator uses its LLM to understand
    # the sub-agents' capabilities (based on their descriptions and names) and delegate tasks.
)
