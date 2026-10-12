"""
Automated Unit and Integration Tests for VisionFit AI.
Tests image validation, preprocessing, prompt builders, parsing, and favorites state.
"""

import sys
import io
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add visionfit-ai directory to path
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from utils.validators import validate_image_file, sanitize_text_input
from utils.prompts import build_recipe_prompt, build_workout_prompt
from utils.formatting import (
    format_export_file,
    generate_sample_recipe_markdown,
    generate_sample_workout_markdown,
)
from services.image_service import ImageService
from services.recipe_service import RecipeService
from services.workout_service import WorkoutService
from services.gemini_service import GeminiService


def run_all_tests():
    print("==================================================")
    print("🧪 RUNNING VISIONFIT AI VERIFICATION SUITE")
    print("==================================================")

    # 1. Test Image Validation - Valid Image
    print("\n--- 1. Testing Image Validation (Valid Image) ---")
    valid_img = Image.new("RGB", (400, 300), color="#10b981")
    buf = io.BytesIO()
    valid_img.save(buf, format="JPEG")
    valid_bytes = buf.getvalue()

    is_valid, err, loaded = validate_image_file(valid_bytes, "test.jpg")
    assert is_valid is True, f"Expected valid image: {err}"
    assert loaded is not None
    assert loaded.size == (400, 300)
    print("[OK] Valid image accepted successfully.")

    # 2. Test Image Validation - Empty / Invalid Extension
    print("\n--- 2. Testing Image Validation (Invalid Formats) ---")
    is_valid, err, _ = validate_image_file(b"", "empty.jpg")
    assert is_valid is False
    print("[OK] Empty file rejected with error:", err)

    is_valid, err, _ = validate_image_file(valid_bytes, "document.pdf")
    assert is_valid is False
    print("[OK] Non-image extension rejected with error:", err)

    is_valid, err, _ = validate_image_file(b"NOT_AN_IMAGE_CONTENT_HERE", "corrupted.jpg")
    assert is_valid is False
    print("[OK] Corrupted bytes rejected with error:", err)

    # 3. Test Image Preprocessing Service
    print("\n--- 3. Testing Image Preprocessing Service ---")
    # Test RGBA conversion and downsampling
    rgba_img = Image.new("RGBA", (2000, 1500), color=(255, 100, 50, 200))
    proc_bytes, mime, final_pil = ImageService.preprocess_image_for_gemini(rgba_img)
    assert mime == "image/jpeg"
    assert final_pil.mode == "RGB"
    # Verify dimensions are constrained to <= 1600
    assert final_pil.size[0] <= 1600 and final_pil.size[1] <= 1600
    print(f"[OK] Preprocessed 2000x1500 RGBA -> {final_pil.size} RGB JPEG ({len(proc_bytes)/1024:.1f} KB).")

    metadata = ImageService.get_image_metadata(final_pil, proc_bytes)
    assert "resolution" in metadata
    print("[OK] Metadata extracted successfully:", metadata)

    # 4. Test Text Sanitization
    print("\n--- 4. Testing Input Sanitization ---")
    dirty_text = "  Peanuts\x00\x08, shellfish, tree nuts!   "
    clean_text = sanitize_text_input(dirty_text)
    assert clean_text == "Peanuts, shellfish, tree nuts!"
    print("[OK] Sanitization OK:", clean_text)

    # 5. Test Recipe Prompt Builder
    print("\n--- 5. Testing Recipe Prompt Construction ---")
    recipe_prefs = {
        "meal_type": "Lunch",
        "dietary_preference": "Vegetarian",
        "cuisine": "Mediterranean",
        "cooking_time": "20 minutes",
        "servings": 2,
        "goal": "High Protein",
        "allergies": "Gluten",
        "language": "English",
    }
    recipe_prompt = build_recipe_prompt(recipe_prefs)
    assert "Target Meal Type: Lunch" in recipe_prompt
    assert "Vegetarian" in recipe_prompt
    assert "Gluten" in recipe_prompt
    print("[OK] Recipe prompt contains all preference constraints.")

    # 6. Test Workout Prompt Builder
    print("\n--- 6. Testing Workout Prompt Construction ---")
    workout_prefs = {
        "goal": "Strength",
        "experience": "Beginner",
        "duration": "30 minutes",
        "location": "Home",
        "equipment_preference": "Use Visible Equipment",
        "focus": "Full Body",
        "limitations": "Bad knee",
        "language": "English",
    }
    workout_prompt = build_workout_prompt(workout_prefs)
    assert "Primary Fitness Goal: Strength" in workout_prompt
    assert "Beginner" in workout_prompt
    assert "Bad knee" in workout_prompt
    print("[OK] Workout prompt contains all training constraints.")

    # 7. Test Recipe Parsing & Session State Persistence
    print("\n--- 7. Testing Recipe Output Parser & Favorites ---")
    sample_rec_md = generate_sample_recipe_markdown(recipe_prefs)
    parsed_rec = RecipeService.parse_recipe_output(sample_rec_md, recipe_prefs)
    assert parsed_rec["title"] is not None
    assert "Mediterranean" in parsed_rec["title"]
    assert parsed_rec["calories"] is not None
    print(f"[OK] Parsed Recipe: '{parsed_rec['title']}' (~{parsed_rec['calories']} kcal, {parsed_rec['total_time']}).")

    # Favorites state
    mock_session = {"favorites": []}
    added = RecipeService.save_to_favorites(mock_session, parsed_rec)
    assert added is True
    assert len(RecipeService.get_favorites(mock_session)) == 1
    print("[OK] Saved recipe to favorites list.")

    # Remove
    RecipeService.remove_from_favorites(mock_session, parsed_rec["id"])
    assert len(RecipeService.get_favorites(mock_session)) == 0
    print("[OK] Removed recipe from favorites.")

    # 8. Test Workout Parsing & Session State Persistence
    print("\n--- 8. Testing Workout Output Parser & Favorites ---")
    sample_work_md = generate_sample_workout_markdown(workout_prefs)
    parsed_work = WorkoutService.parse_workout_output(sample_work_md, workout_prefs)
    assert parsed_work["title"] is not None
    assert parsed_work["exercise_count"] >= 3
    print(f"[OK] Parsed Workout: '{parsed_work['title']}' ({parsed_work['exercise_count']} exercises, {parsed_work['duration']}).")

    WorkoutService.save_to_favorites(mock_session, parsed_work)
    assert len(WorkoutService.get_favorites(mock_session)) == 1
    print("[OK] Saved workout to favorites list.")

    # 9. Test Standalone Export File Formatter
    print("\n--- 9. Testing Standalone Markdown Export ---")
    export_content = format_export_file(parsed_rec)
    assert "VisionFit AI" in export_content
    assert "# 🥗 Mediterranean" in export_content
    print("[OK] Export file formatted with metadata and timestamp.")

    # 10. Test Gemini Service Key & Model Handlers
    print("\n--- 10. Testing Gemini Service Configuration ---")
    # Verify behavior when no key is supplied
    ok, msg = GeminiService.test_connection(api_key="", model_name="gemini-2.5-flash")
    assert ok is False
    assert "No Gemini API Key" in msg
    print("[OK] Correctly caught missing API key with helpful user message.")

    print("\n==================================================")
    print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
