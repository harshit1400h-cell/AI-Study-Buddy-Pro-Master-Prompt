"""
Recipe Generation and Lifecycle Management Service for VisionFit AI.
Orchestrates vision prompts, response parsing, nutrition extractions, and session persistence.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from services.gemini_service import GeminiService
from utils.prompts import build_recipe_prompt, RECIPE_SYSTEM_DIRECTIVE


class RecipeService:
    @classmethod
    def generate_recipe(
        cls,
        image_bytes: bytes,
        mime_type: str,
        preferences: Dict[str, Any],
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Coordinates recipe generation using image and user criteria.
        """
        prompt = build_recipe_prompt(preferences)

        success, content, meta = GeminiService.generate_multimodal(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            system_instruction=RECIPE_SYSTEM_DIRECTIVE,
            api_key=api_key,
            model_name=model_name
        )

        if not success:
            return False, content, None

        parsed_data = cls.parse_recipe_output(content, preferences)
        return True, content, parsed_data

    @staticmethod
    def parse_recipe_output(markdown_text: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts key highlights from the generated markdown for display cards & session state.
        """
        # Extract title from first H1 header
        title_match = re.search(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Custom VisionFit Recipe"

        # Extract approximate calories
        cal_match = re.search(r"Calories\*?\*?:\s*~?(\d+)", markdown_text, re.IGNORECASE)
        calories = cal_match.group(1) if cal_match else "380-450"

        # Extract protein
        protein_match = re.search(r"Protein\*?\*?:\s*~?(\d+g?)", markdown_text, re.IGNORECASE)
        protein = protein_match.group(1) if protein_match else "24g"

        # Extract prep / cook / total time
        total_time_match = re.search(r"Total Time\*?\*?:\s*([^-\n\r]+)", markdown_text, re.IGNORECASE)
        total_time = total_time_match.group(1).strip() if total_time_match else preferences.get("cooking_time", "25 mins")

        # Extract difficulty
        diff_match = re.search(r"Difficulty\*?\*?:\s*([A-Za-z]+)", markdown_text, re.IGNORECASE)
        difficulty = diff_match.group(1).strip() if diff_match else "Easy"

        return {
            "id": str(uuid.uuid4()),
            "type": "recipe",
            "title": title,
            "raw_markdown": markdown_text,
            "preferences": preferences,
            "calories": calories,
            "protein": protein,
            "total_time": total_time,
            "difficulty": difficulty,
            "servings": preferences.get("servings", 2),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # ================= FAVORITES STORAGE HELPERS =================
    @staticmethod
    def save_to_favorites(session_state, item_data: Dict[str, Any]):
        """
        Saves a recipe item to Streamlit session state favorites list.
        """
        if "favorites" not in session_state:
            session_state["favorites"] = []
        
        # Check if already saved
        existing_ids = [f.get("id") for f in session_state["favorites"]]
        if item_data.get("id") not in existing_ids:
            session_state["favorites"].append(item_data)
            return True
        return False

    @staticmethod
    def remove_from_favorites(session_state, item_id: str):
        """
        Removes an item from favorites.
        """
        if "favorites" in session_state:
            session_state["favorites"] = [
                f for f in session_state["favorites"] if f.get("id") != item_id
            ]

    @staticmethod
    def get_favorites(session_state) -> List[Dict[str, Any]]:
        """
        Returns all saved recipe favorites.
        """
        all_favs = session_state.get("favorites", [])
        return [f for f in all_favs if f.get("type") == "recipe"]

