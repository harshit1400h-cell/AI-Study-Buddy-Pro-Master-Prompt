"""
Gemini Multimodal Service for VisionFit AI.
Encapsulates Google Gen AI SDK client, multimodal request dispatching,
model configuration, and defensive error handling.
"""

import os
from typing import Tuple, Optional, Dict, Any
from dotenv import load_dotenv

# Load local environment if present
load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class GeminiService:
    @staticmethod
    def get_api_key(runtime_key: Optional[str] = None) -> Optional[str]:
        """
        Retrieves API key: checks runtime parameter first, then environment variable.
        """
        if runtime_key and runtime_key.strip():
            return runtime_key.strip()
        env_key = os.getenv("GEMINI_API_KEY", "").strip()
        return env_key if env_key else None

    @staticmethod
    def get_model_name(runtime_model: Optional[str] = None) -> str:
        """
        Retrieves model name: checks runtime parameter first, then environment, then default.
        """
        if runtime_model and runtime_model.strip():
            return runtime_model.strip()
        return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    @classmethod
    def test_connection(cls, api_key: Optional[str] = None, model_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Tests API key and model connectivity with a lightweight text probe.
        """
        key = cls.get_api_key(api_key)
        if not key:
            return False, "No Gemini API Key provided. Set GEMINI_API_KEY in .env or enter it in the sidebar."

        model = cls.get_model_name(model_name)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=model,
                contents="Ping. Respond with 'PONG' only.",
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=10)
            )
            if response and response.text:
                return True, f"Connected successfully to Google Gemini ({model})!"
            return False, "Received empty response from Gemini API."
        except Exception as e:
            return False, cls._format_error_message(e)

    @classmethod
    def generate_multimodal(
        cls,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        system_instruction: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Executes a multimodal vision request to Gemini: sends image bytes + structured prompt.

        Returns:
            (success: bool, content_or_error_message: str, metadata: dict)
        """
        key = cls.get_api_key(api_key)
        if not key:
            return (
                False,
                "Gemini API Key missing. Please provide your API key in the sidebar or set GEMINI_API_KEY in .env.",
                None
            )

        model = cls.get_model_name(model_name)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)

            # Create multimodal parts: Image part + User prompt text part
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            contents = [image_part, prompt]

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.35,
                top_p=0.9,
            )

            # Execute vision analysis
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

            if not response or not response.text:
                return False, "The AI model returned an empty response. Please retry with a clearer photo.", None

            meta = {
                "model": model,
                "image_size_kb": len(image_bytes) / 1024,
                "mime_type": mime_type,
            }

            return True, response.text, meta

        except Exception as e:
            error_msg = cls._format_error_message(e)
            return False, error_msg, None

    @staticmethod
    def _format_error_message(exc: Exception) -> str:
        """
        Translates raw API exceptions into actionable, user-friendly guidance.
        """
        err_str = str(exc)
        err_lower = err_str.lower()

        if "api_key" in err_lower or "api key not valid" in err_lower or "403" in err_lower or "unauthenticated" in err_lower:
            return "Invalid or unauthorized Gemini API Key. Please verify your key at https://aistudio.google.com/ and update it in settings."
        elif "quota" in err_lower or "resource_exhausted" in err_lower or "429" in err_lower:
            return "Gemini API rate limit or free quota exceeded. Please wait 30 seconds and try again, or switch to a paid quota."
        elif "not_found" in err_lower or "model" in err_lower and "not found" in err_lower:
            return f"Selected model was not recognized by the API. Try switching to 'gemini-2.5-flash' or 'gemini-2.0-flash'. Details: {err_str}"
        elif "timeout" in err_lower or "timed out" in err_lower:
            return "Connection to Gemini timed out. Please check your internet connection and try again."
        elif "connection" in err_lower or "network" in err_lower:
            return "Network error connecting to Google GenAI servers. Please ensure you are connected to the internet."
        else:
            return f"Gemini API Error: {err_str}"

