import os
import requests
from functools import cached_property
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import Client, types

from tools import get_weather, get_forecast
from callbacks import log_before_model, log_after_model, log_before_tool

# Custom Gemini class to force Vertex AI usage
class VertexGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        return Client(
            vertexai=True,
            project="lunar-prism-486120-n0",
            location="us-central1",
            http_options=types.HttpOptions(
                headers=self._tracking_headers(),
                retry_options=self.retry_options,
            )
        )

# Define Model
# Use gemini-2.5-flash since user confirmed it works.
MODEL_NAME = "gemini-2.5-flash"

# --- Sub-Agents ---

weather_agent = LlmAgent(
    name="weather_agent",
    model=VertexGemini(model=MODEL_NAME),
    description="Provides current weather information for a specific location.",
    instruction="""
    You are a specialized weather agent.
    Your task is to provide the current weather for a given city using the `get_weather` tool.
    If the tool returns weather data, summarize it clearly for the user.
    If the tool fails, explain the error.
    """,
    tools=[get_weather]
)

forecast_agent = LlmAgent(
    name="forecast_agent",
    model=VertexGemini(model=MODEL_NAME),
    description="Provides 3-day weather forecasts for a specific location.",
    instruction="""
    You are a specialized forecast agent.
    Your task is to provide a 3-day weather forecast for a given city using the `get_forecast` tool.
    Present the forecast in a readable format.
    """,
    tools=[get_forecast]
)

# --- Root Agent ---

root_agent = LlmAgent(
    name="root_agent",
    model=VertexGemini(model=MODEL_NAME),
    instruction="""
    You are a friendly and helpful Multi-Agent Weather Assistant.
    
    Your responsibilities:
    1.  **Greet the user** warmly if they say "Hi", "Hello", or similar. Introduce yourself as the "Multi-Agent Weather Bot".
    2.  **Route queries** to the appropriate sub-agent:
        *   If the user asks for *current* weather (e.g., "What's the weather in London?"), delegate to the `weather_agent`.
        *   If the user asks for a *forecast* or *future* weather (e.g., "Forecast for Paris", "Will it rain tomorrow?"), delegate to the `forecast_agent`.
    3.  If the user's request is unclear, ask for clarification.
    
    Always be polite and professional.
    """,
    sub_agents=[weather_agent, forecast_agent],
    before_model_callback=[log_before_model],
    after_model_callback=[log_after_model],
    before_tool_callback=[log_before_tool]
)