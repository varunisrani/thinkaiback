"""
Utility functions for interacting with Google Gemini 2.5 Flash API.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional, Union

from google import genai
from google.genai import types
from dotenv import load_dotenv
import logging

# Import logging utilities
from .logging_utils import log_api_call

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Gen AI client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

async def call_gemini_25_flash(
    prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    top_p: float = 0.95,
    top_k: int = 20
) -> Dict[str, Any]:
    """
    Call Google Gemini 2.5 Flash model with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the model
        model (str): The model to use (default: gemini-2.5-flash)
        temperature (float): Temperature setting (default: 0.7)
        max_tokens (int): Maximum tokens in response (default: 2000)
        top_p (float): Nucleus sampling parameter (default: 0.95)
        top_k (int): Top-k sampling parameter (default: 20)
        
    Returns:
        Dict[str, Any]: The model's response
    """
    start_time = time.time()
    response_text = ""
    error = None
    status = "success"
    
    try:
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found in environment")
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                response_mime_type="application/json"
            )
        )
        
        # Safe content extraction
        def extract_content_safely(response):
            if not hasattr(response, 'candidates') or not response.candidates:
                raise ValueError("No candidates in Gemini response")
            
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                raise ValueError("Empty content in Gemini response")
            
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                raise ValueError("No content parts in Gemini response")
            
            text_content = candidate.content.parts[0].text
            if not text_content:
                raise ValueError("Empty text content in Gemini response")
            
            return text_content

        response_text = extract_content_safely(response)
        return {
            "success": True,
            "content": response_text,
            "usage": {
                "prompt_tokens": len(prompt.split()),  # Approximate token count
                "completion_tokens": len(response_text.split()),  # Approximate token count
                "total_tokens": len(prompt.split()) + len(response_text.split())
            }
        }
        
    except Exception as e:
        error = str(e)
        status = "error"
        logger.error(f"Error calling Gemini API: {error}")
        return {
            "success": False,
            "error": error
        }
    finally:
        duration = time.time() - start_time
        log_api_call(
            provider="gemini",
            model=model,
            prompt_length=len(prompt),
            response_length=len(response_text),
            duration=duration,
            status=status,
            error=error,
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k
            }
        )

async def call_gemini_with_system_message(
    prompt: str,
    system_message: str = "You are a helpful assistant.",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    json_mode: bool = False
) -> str:
    """Call Google Gemini 2.5 Flash with system message support.
    
    Args:
        prompt: The user prompt to send to the API
        system_message: The system message to set the context
        temperature: The temperature parameter for generation
        max_tokens: The maximum number of tokens to generate
        json_mode: Whether to request structured JSON output
        
    Returns:
        The generated text response
    """
    model_name = "gemini-2.5-flash"
    
    # Combine system message and prompt
    full_prompt = f"{system_message}\n\n{prompt}"
    
    if json_mode:
        full_prompt += "\n\nPlease format your response as a valid JSON object."
    
    start_time = time.time()
    error = None
    response_text = ""
    status = "success"
    
    try:
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found in environment")
        
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=20,
                response_mime_type="application/json" if json_mode else None
            )
        )
        
        # Safe content extraction
        def extract_content_safely(response):
            if not hasattr(response, 'candidates') or not response.candidates:
                raise ValueError("No candidates in Gemini response")
            
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                raise ValueError("Empty content in Gemini response")
            
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                raise ValueError("No content parts in Gemini response")
            
            text_content = candidate.content.parts[0].text
            if not text_content:
                raise ValueError("Empty text content in Gemini response")
            
            return text_content

        response_text = extract_content_safely(response)
    except Exception as e:
        error = str(e)
        status = "error"
        raise
    finally:
        duration = time.time() - start_time
        
        # Log the API call
        log_api_call(
            provider="gemini",
            model=model_name,
            prompt_length=len(full_prompt),
            response_length=len(response_text),
            duration=duration,
            status=status,
            error=error,
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "json_mode": json_mode,
            }
        )
    
    return response_text

# Backward compatibility aliases
call_gemini_pro = call_gemini_with_system_message
call_openai_gpt = call_gemini_25_flash  # Redirect OpenAI calls to Gemini 2.5 Flash

def parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse a JSON string from the model response.
    
    Args:
        response (str): The response string containing JSON
        
    Returns:
        Dict[str, Any]: Parsed JSON data
    """
    try:
        # Find JSON content between triple backticks if present
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            json_str = response.strip()
            
        # Parse the JSON
        data = json.loads(json_str)
        return {
            "success": True,
            "data": data
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return {
            "success": False,
            "error": f"JSON parsing error: {str(e)}",
            "raw_response": response
        }
    except Exception as e:
        logger.error(f"Unexpected error parsing response: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "raw_response": response
        }