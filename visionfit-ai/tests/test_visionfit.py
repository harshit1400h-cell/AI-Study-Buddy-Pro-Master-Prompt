"""
Unit and Integration Test Suite for VisionFit AI
Verifies image validation, preprocessing, prompt contracts, formatting,
storage service, and demo mode fallbacks.
"""

import sys
import io
import json
import pytest
from pathlib import Path
from PIL import Image

# Ensure visionfit-ai is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.validators import validate_uploaded_image, sanitize_text_input
from utils.formatting import (
    extract_json_from_response,
    format_recipe_markdown,
    format_workout_markdown
)
from utils.prompts import build_recipe_prompt, build_workout_prompt
from services.image_service import (
    preprocess_image,
    image_to_bytes,
    generate_sample_ingredients_image,
    generate_sample_gym_image
)
from services.storage_service import (
    init_db,
    save_favorite,
    get_favorites,
    delete_favorite,
    clear_all_favorites,
    get_favorites_counts
)
from services.gemini_service import GeminiService
from services.recipe_service import generate_recipe
from services.workout_service import generate_workout


class MockFile:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._io = io.BytesIO(data)
        self.size = len(data)

    def read(self, *args):
        return self._io.read(*args)

    def seek(self, offset, whence=0):
        return self._io.seek(offset, whence)

    def tell(self):
        return self._io.tell()


def test_image_validation_valid():
    img = Image.new("RGB", (400, 300), color=(16, 185, 129))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    mock_file = MockFile("test_groceries.jpg", buf.getvalue())

    is_valid, err_msg, pil_img = validate_uploaded_image(mock_file)
    assert is_valid is True
    assert err_msg == ""
    assert pil_img is not None
    assert pil_img.size == (400, 300)


def test_image_validation_invalid_extension():
    mock_file = MockFile("malicious.exe", b"binarycontent")
    is_valid, err_msg, pil_img = validate_uploaded_image(mock_file)
    assert is_valid is False
    assert "Unsupported file format" in err_msg


def test_image_validation_empty_file():
    mock_file = MockFile("empty.png", b"")
    is_valid, err_msg, pil_img = validate_uploaded_image(mock_file)
    assert is_valid is False
    assert "empty" in err_msg.lower()


def test_image_preprocessing_resizing():
    large_img = Image.new("RGB", (3200, 2400), color=(255, 0, 0))
    processed = preprocess_image(large_img, max_dimension=1600)
    assert max(processed.size) <= 1600
    assert processed.mode == "RGB"


def test_sample_image_generators():
    ing_img = generate_sample_ingredients_image()
    assert ing_img.size == (800, 600)
    assert ing_img.mode == "RGB"

    gym_img = generate_sample_gym_image()
    assert gym_img.size == (800, 600)
    assert gym_img.mode == "RGB"


def test_json_extraction():
    raw_markdown = """
    Here is your recipe:
    ```json
    {
      "title": "Healthy Vegetable Stir-Fry",
      "prep_time_minutes": 10,
      "cook_time_minutes": 15
    }
    ```
    Enjoy your cooking!
    """
    parsed = extract_json_from_response(raw_markdown)
    assert parsed is not None
    assert parsed["title"] == "Healthy Vegetable Stir-Fry"
    assert parsed["cook_time_minutes"] == 15


def test_prompt_contracts():
    rec_prompt = build_recipe_prompt({
        "meal_type": "Dinner",
        "dietary_pref": "Vegetarian",
        "cuisine": "Indian",
        "cooking_time": 20,
        "servings": 4,
        "allergies": "Peanuts",
        "goal": "High Protein"
    })
    assert "Vegetarian" in rec_prompt
    assert "Peanuts" in rec_prompt
    assert "visually_identified_ingredients" in rec_prompt
    assert "uncertain_items" in rec_prompt

    wrk_prompt = build_workout_prompt({
        "goal": "Strength",
        "experience_level": "Beginner",
        "available_time": 20,
        "location": "Home",
        "equipment_pref": "Use Visible Equipment",
        "focus": "Full Body"
    })
    assert "Strength" in wrk_prompt
    assert "Beginner" in wrk_prompt
    assert "visually_identified_equipment" in wrk_prompt
    assert "easier_alternative" in wrk_prompt


def test_storage_favorites(tmp_path):
    test_db = tmp_path / "test_visionfit.db"
    init_db(test_db)

    # Save recipe
    rec_id = save_favorite(
        item_type="recipe",
        title="Test Shakshuka",
        summary="A tasty breakfast skillet",
        data={"title": "Test Shakshuka", "servings": 2},
        db_path=test_db
    )
    assert rec_id > 0

    # Save workout
    wrk_id = save_favorite(
        item_type="workout",
        title="Dumbbell Blast",
        summary="Quick 20 min session",
        data={"title": "Dumbbell Blast", "duration": 20},
        db_path=test_db
    )
    assert wrk_id > 0

    # Verify counts
    counts = get_favorites_counts(test_db)
    assert counts["recipe"] == 1
    assert counts["workout"] == 1
    assert counts["total"] == 2

    # Query all
    all_favs = get_favorites(db_path=test_db)
    assert len(all_favs) == 2

    # Query recipe only
    recipe_favs = get_favorites("recipe", db_path=test_db)
    assert len(recipe_favs) == 1
    assert recipe_favs[0]["title"] == "Test Shakshuka"

    # Delete one
    deleted = delete_favorite(rec_id, db_path=test_db)
    assert deleted is True

    counts_after = get_favorites_counts(test_db)
    assert counts_after["recipe"] == 0
    assert counts_after["workout"] == 1


def test_recipe_service_demo_fallback():
    # Service with no key should safely return Demo simulation with clear label
    service = GeminiService(api_key="")
    sample_img = generate_sample_ingredients_image()

    success, recipe_data, notice = generate_recipe(
        sample_img,
        {"goal": "High Protein", "servings": 2, "meal_type": "Breakfast"},
        service
    )
    assert success is True
    assert recipe_data["is_demo"] is True
    assert "title" in recipe_data
    assert "DEMO MODE" in notice


def test_workout_service_demo_fallback():
    service = GeminiService(api_key="")
    sample_img = generate_sample_gym_image()

    success, workout_data, notice = generate_workout(
        sample_img,
        {"goal": "Strength", "available_time": 30, "experience_level": "Intermediate"},
        service
    )
    assert success is True
    assert workout_data["is_demo"] is True
    assert "title" in workout_data
    assert "main_exercises" in workout_data
    assert len(workout_data["main_exercises"]) > 0

