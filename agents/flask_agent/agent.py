import asyncio

from flask import Flask, request, jsonify
from google.adk.agents import Agent, LlmAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService, BaseSessionService
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, SafetySetting, Tool, ChatSession
from vertexai.preview.prompts import Prompt
from google.genai import types
from google.adk.tools import google_search 

APP_NAME = "agents_app"

app = Flask(__name__)

cv_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="cv_agent",
    description="Answers any user question about resumes",
    instruction="You are a helpful agent who can answer user questions about curriculum vitaes.",
    tools=[google_search]
)

# Define a simple agent
class MyAgent():
    def __init__(self):
        super().__init__()

    async def talk_with_agent(self, user_query: str, user_id: str, session_id: str = None):
        """Sends a query to the agent and prints the final response."""
        session_service = InMemorySessionService()

        # Get or create session
        if session_id:
            current_session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
            if not current_session:
                current_session = session_service.create_session(app_name=APP_NAME, user_id=user_id)
        else:
            current_session = session_service.create_session(app_name=APP_NAME, user_id=user_id)

        print(f"Session created: App='{APP_NAME}', User='{user_id}', Session='{current_session.id}'")

        # --- Runner ---
        # Key Concept: Runner orchestrates the agent execution loop.
        runner = Runner(
            agent=cv_agent,  # The agent we want to run
            app_name=APP_NAME,   # Associates runs with our app
            session_service=session_service  # Uses our session manager
        )

        print(f"\n>>> User Query: {user_query}")

        # Prepare the user's message in ADK format
        content = types.Content(role='user', parts=[types.Part(text=user_query)])

        final_response_text = "Agent did not produce a final response."  # Default

        # Key Concept: run_async executes the agent logic and yields Events.
        # We iterate through events to find the final answer.
        async for event in runner.run_async(user_id=user_id, session_id=current_session.id, new_message=content):
            # You can uncomment the line below to see *all* events during execution
            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # Key Concept: is_final_response() marks the concluding message for the turn.
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks here if needed (e.g., specific error codes)
                break  # Stop processing events once the final response is found

        return {
            "response": final_response_text,
            "session_id": current_session.id
        }


# Create an instance of the agent
my_agent = MyAgent()

# Define a route to handle agent requests
@app.route('/agent', methods=['POST'])
def agent_endpoint():
    try:
        data = request.get_json()
        user_query = data.get('query')
        session_id = data.get('session_id')
        user_id = str(request.get_json()["user_id"])

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        if not user_id:
            return jsonify({"error": "User_id is required"}), 400

        # Since runner.run_async is async, we need to run it in an event loop.
        # Flask route handlers are synchronous by default.
        # For production, consider using an async Flask framework (like Quart)
        # or manage the asyncio event loop carefully.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(my_agent.talk_with_agent(user_query, user_id, session_id))
        loop.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
