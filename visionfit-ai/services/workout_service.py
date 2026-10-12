"""
Workout Generation and Lifecycle Management Service for VisionFit AI.
Orchestrates equipment vision prompts, biomechanics cues, response parsing, and session persistence.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from services.gemini_service import GeminiService
from utils.prompts import build_workout_prompt, WORKOUT_SYSTEM_DIRECTIVE


class WorkoutService:
    @classmethod
    def generate_workout(
        cls,
        image_bytes: bytes,
        mime_type: str,
        preferences: Dict[str, Any],
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Coordinates workout plan generation using image and user criteria.
        """
        prompt = build_workout_prompt(preferences)

        success, content, meta = GeminiService.generate_multimodal(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            system_instruction=WORKOUT_SYSTEM_DIRECTIVE,
            api_key=api_key,
            model_name=model_name
        )

        if not success:
            return False, content, None

        parsed_data = cls.parse_workout_output(content, preferences)
        return True, content, parsed_data

    @staticmethod
    def parse_workout_output(markdown_text: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts key highlights from the generated workout markdown for display cards & session state.
        """
        # Extract title from first H1 header
        title_match = re.search(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Custom VisionFit Workout Routine"

        # Count exercises
        exercise_matches = re.findall(r"###\s+Exercise\s+\d+:\s*(.+)", markdown_text, re.IGNORECASE)
        exercise_count = len(exercise_matches) if exercise_matches else 4

        # Target duration
        duration_match = re.search(r"Total Duration\*?\*?:\s*([^\n\r]+)", markdown_text, re.IGNORECASE)
        duration = duration_match.group(1).strip() if duration_match else preferences.get("duration", "30 mins")

        # Target muscles
        muscles_match = re.search(r"Target Muscle Groups\*?\*?:\s*([^\n\r]+)", markdown_text, re.IGNORECASE)
        muscles = muscles_match.group(1).strip() if muscles_match else preferences.get("focus", "Full Body")

        return {
            "id": str(uuid.uuid4()),
            "type": "workout",
            "title": title,
            "raw_markdown": markdown_text,
            "preferences": preferences,
            "exercise_count": exercise_count,
            "duration": duration,
            "muscles": muscles,
            "experience": preferences.get("experience", "Beginner"),
            "goal": preferences.get("goal", "General Fitness"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # ================= FAVORITES STORAGE HELPERS =================
    @staticmethod
    def save_to_favorites(session_state, item_data: Dict[str, Any]):
        """
        Saves a workout item to Streamlit session state favorites list.
        """
        if "favorites" not in session_state:
            session_state["favorites"] = []

        existing_ids = [f.get("id") for f in session_state["favorites"]]
        if item_data.get("id") not in existing_ids:
            session_state["favorites"].append(item_data)
            return True
        return False

    @staticmethod
    def remove_from_favorites(session_state, item_id: str):
        """
        Removes a workout item from favorites.
        """
        if "favorites" in session_state:
            session_state["favorites"] = [
                f for f in session_state["favorites"] if f.get("id") != item_id
            ]

    @staticmethod
    def get_favorites(session_state) -> List[Dict[str, Any]]:
        """
        Returns all saved workout favorites.
        """
        all_favs = session_state.get("favorites", [])
        return [f for f in all_favs if f.get("type") == "workout"]

