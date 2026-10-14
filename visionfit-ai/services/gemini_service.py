"""
Google Gemini Multimodal API Service for VisionFit AI
Integrates with official google-genai SDK for vision + text generation.
Provides robust error handling, key masking, and graceful demo mode fallback.
"""

import os
import logging
from typing import Tuple, Dict, Any, Optional
from PIL import Image
from dotenv import load_dotenv

# Load local environment
load_dotenv()

logger = logging.getLogger("visionfit_gemini")

# Default recommended multimodal model
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        # Allow passed key or env variable
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        self.model_name = (model_name or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)).strip()
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai Client: {e}")
                self._client = None

    @property
    def is_configured(self) -> bool:
        """Returns True if a non-empty API key is configured."""
        return bool(self.api_key and self._client)

    @property
    def masked_key(self) -> str:
        """Returns safe masked representation of the API key for UI display."""
        if not self.api_key:
            return "Not Configured"
        if len(self.api_key) <= 8:
            return "••••••••"
        return f"{self.api_key[:4]}••••••••{self.api_key[-4:]}"

    def generate_multimodal_content(
        self,
        image: Image.Image,
        prompt: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Sends preprocessed image and structured prompt to Gemini Vision model.
        
        Returns:
            (success: bool, raw_text: str, metadata: Dict[str, Any])
        """
        if not self.is_configured:
            return (
                False,
                "",
                {
                    "error_type": "MISSING_API_KEY",
                    "message": "Gemini API key is not configured. Please provide a GEMINI_API_KEY in the sidebar or in your .env file."
                }
            )

        try:
            # Using official google-genai client
            # The client accepts PIL images directly in contents alongside text strings
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=[image, prompt]
            )

            text_output = ""
            if hasattr(response, "text") and response.text:
                text_output = response.text
            elif hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    parts = getattr(candidate.content, "parts", [])
                    if parts and hasattr(parts[0], "text"):
                        text_output = parts[0].text

            if not text_output:
                return (
                    False,
                    "",
                    {
                        "error_type": "EMPTY_RESPONSE",
                        "message": "Gemini returned an empty response. Please try again with a clearer image or modified prompt."
                    }
                )

            return True, text_output, {
                "model_used": self.model_name,
                "is_demo": False
            }

        except Exception as exc:
            err_str = str(exc)
            logger.error(f"Gemini API call failed: {err_str}")
            
            # Categorize common errors for user-friendly guidance
            if "API_KEY_INVALID" in err_str or "400" in err_str and "key" in err_str.lower():
                err_type = "INVALID_API_KEY"
                msg = "The provided Gemini API key was rejected as invalid. Please check your key at Google AI Studio."
            elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                err_type = "QUOTA_EXCEEDED"
                msg = "Gemini API rate limit or quota exceeded. Please wait a minute or use a paid tier project key."
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                err_type = "SERVICE_UNAVAILABLE"
                msg = "Google Gemini service is temporarily busy. Please retry in a few moments."
            elif "model" in err_str.lower() and "not found" in err_str.lower():
                err_type = "MODEL_NOT_FOUND"
                msg = f"Configured model '{self.model_name}' was not found. Please try 'gemini-2.5-flash' or 'gemini-1.5-flash'."
            else:
                err_type = "API_ERROR"
                msg = f"AI Generation error: {err_str[:120]}... Please try again."

            return False, "", {
                "error_type": err_type,
                "message": msg
            }

