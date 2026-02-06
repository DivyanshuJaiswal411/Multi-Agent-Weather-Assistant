import logging
from typing import Any, Dict
from google.genai import types

logger = logging.getLogger(__name__)

async def log_before_model(callback_context, llm_request):
    """Logs the model request."""
    logger.info(f"--- Before Model Call ---")
    # logger.info(f"Model: {llm_request.model}")
    return None

async def log_after_model(callback_context, llm_response):
    """Logs the model response."""
    logger.info(f"--- After Model Call ---")
    # Log the response safely without accessing attributes that might not exist
    logger.info(f"Response received from model.")
    return None

async def log_before_tool(tool, args, tool_context):
    logger.info(f"--- Tool Call: {tool.name} ---")
    logger.info(f"Args: {args}")
    
    # Experimental: Try to save city to session state
    if 'city' in args:
        logger.info(f"User is asking about {args['city']}. We could save this to preferences.")
    
    return None