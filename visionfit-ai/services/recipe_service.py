"""
Recipe Generation Service for VisionFit AI
Handles parameter collection, Gemini multimodal invocation, response parsing,
and intelligent demo simulation fallback.
"""

from typing import Dict, Any, Tuple
from PIL import Image
from services.gemini_service import GeminiService
from utils.prompts import build_recipe_prompt
from utils.formatting import extract_json_from_response


# Pre-crafted realistic demo recipes when in Demo Mode
DEMO_RECIPES = {
    "Vegetarian": {
        "title": "Rustic Mediterranean Bell Pepper & Tomato Skillet",
        "description": "A vibrant, nutrient-dense skillet dish celebrating sweet sautéed bell peppers, blistered tomatoes, garlic, and fresh herbs in rich extra virgin olive oil.",
        "cuisine": "Mediterranean",
        "meal_type": "Dinner",
        "prep_time_minutes": 10,
        "cook_time_minutes": 18,
        "total_time_minutes": 28,
        "servings": 2,
        "difficulty": "Easy",
        "visually_identified_ingredients": [
            "Red Bell Pepper",
            "Green Bell Pepper",
            "Ripe Tomatoes",
            "Garlic",
            "Olive Oil"
        ],
        "uncertain_items": [
            "Unlabeled spice container on counter (verify before using)"
        ],
        "ingredients": [
            {"name": "Red Bell Pepper, sliced into strips", "quantity": "1", "unit": "large", "is_optional": False, "need_to_buy": False},
            {"name": "Green Bell Pepper, sliced into strips", "quantity": "1", "unit": "medium", "is_optional": False, "need_to_buy": False},
            {"name": "Ripe Tomatoes, diced", "quantity": "3", "unit": "medium", "is_optional": False, "need_to_buy": False},
            {"name": "Garlic Cloves, thinly sliced", "quantity": "4", "unit": "cloves", "is_optional": False, "need_to_buy": False},
            {"name": "Extra Virgin Olive Oil", "quantity": "2", "unit": "tablespoons", "is_optional": False, "need_to_buy": False},
            {"name": "Crumbled Feta or Firm Tofu", "quantity": "100", "unit": "grams", "is_optional": True, "need_to_buy": True},
            {"name": "Fresh Basil or Oregano", "quantity": "1", "unit": "handful", "is_optional": True, "need_to_buy": True},
            {"name": "Sea Salt & Freshly Ground Black Pepper", "quantity": "1/2", "unit": "tsp each", "is_optional": False, "need_to_buy": False}
        ],
        "steps": [
            {"step_number": 1, "instruction": "Wash and core the bell peppers; slice into uniform 1/4-inch lengthwise ribbons. Dice tomatoes and slice garlic.", "time_or_temp": "Preparation, 5 mins"},
            {"step_number": 2, "instruction": "Warm the olive oil in a wide heavy-bottomed skillet over medium heat. Add garlic and cook until fragrant (do not let it brown).", "time_or_temp": "Medium heat, 1-2 mins"},
            {"step_number": 3, "instruction": "Add the sliced bell peppers to the skillet. Sauté until they start to soften and char slightly at the edges.", "time_or_temp": "Medium-high heat, 6-7 mins"},
            {"step_number": 4, "instruction": "Toss in the diced tomatoes along with salt and black pepper. Stir well, cover with lid, and let tomatoes break down into a glossy, sweet sauce.", "time_or_temp": "Medium heat, 8 mins"},
            {"step_number": 5, "instruction": "Remove lid, stir in fresh herbs, and top with optional crumbled feta or tofu. Serve immediately with warm crusty bread or brown rice.", "time_or_temp": "Simmer, 2 mins"}
        ],
        "nutrition_estimates": {
            "calories": 240,
            "protein_g": 7,
            "carbs_g": 22,
            "fats_g": 14,
            "fiber_g": 6
        },
        "substitutions": [
            "Swap bell peppers for zucchini or yellow squash if preferred.",
            "Use nutritional yeast or silken tofu instead of feta for a 100% vegan protein boost."
        ],
        "storage_tips": "Store cooled skillet leftovers in an airtight glass container in the refrigerator for up to 4 days. Reheat gently on stove."
    },
    "High Protein": {
        "title": "Protein-Packed Garden Shakshuka with Golden Yolks",
        "description": "A high-protein savory brunch or dinner featuring gently poached eggs nestled in a simmered sauce of bell peppers, crushed tomatoes, cumin, and garlic.",
        "cuisine": "Middle Eastern / Mediterranean",
        "meal_type": "Breakfast / Post-Workout",
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "total_time_minutes": 25,
        "servings": 2,
        "difficulty": "Easy",
        "visually_identified_ingredients": [
            "Fresh Eggs",
            "Red Bell Pepper",
            "Tomatoes",
            "Garlic",
            "Olive Oil"
        ],
        "uncertain_items": [
            "Check egg freshness using the water bowl test if uncartoned"
        ],
        "ingredients": [
            {"name": "Whole Fresh Eggs", "quantity": "4", "unit": "large", "is_optional": False, "need_to_buy": False},
            {"name": "Red Bell Pepper, finely diced", "quantity": "1", "unit": "medium", "is_optional": False, "need_to_buy": False},
            {"name": "Crushed Ripe Tomatoes", "quantity": "4", "unit": "medium", "is_optional": False, "need_to_buy": False},
            {"name": "Garlic, minced", "quantity": "3", "unit": "cloves", "is_optional": False, "need_to_buy": False},
            {"name": "Olive Oil", "quantity": "1.5", "unit": "tablespoons", "is_optional": False, "need_to_buy": False},
            {"name": "Ground Cumin & Smoked Paprika", "quantity": "1/2", "unit": "tsp each", "is_optional": True, "need_to_buy": True},
            {"name": "Fresh Cilantro or Parsley", "quantity": "2", "unit": "tablespoons", "is_optional": True, "need_to_buy": True}
        ],
        "steps": [
            {"step_number": 1, "instruction": "Heat olive oil in a medium oven-safe skillet over medium heat. Sauté garlic and bell peppers until tender.", "time_or_temp": "Medium heat, 4 mins"},
            {"step_number": 2, "instruction": "Add crushed tomatoes, cumin, paprika, salt, and pepper. Simmer until the sauce thickens slightly.", "time_or_temp": "Medium-low heat, 6 mins"},
            {"step_number": 3, "instruction": "Using the back of a large spoon, create 4 shallow wells in the bubbling tomato mixture.", "time_or_temp": "1 min"},
            {"step_number": 4, "instruction": "Crack one egg gently into each indentation. Cover pan with a snug lid.", "time_or_temp": "Low heat, 5-7 mins"},
            {"step_number": 5, "instruction": "Cook until egg whites are set but yolks remain delightfully runny. Garnish with chopped fresh cilantro.", "time_or_temp": "Serve warm"}
        ],
        "nutrition_estimates": {
            "calories": 310,
            "protein_g": 21,
            "carbs_g": 14,
            "fats_g": 19,
            "fiber_g": 4
        },
        "substitutions": [
            "Eggetarian / High Protein option: Add canned chickpeas or black beans to the sauce for extra plant protein.",
            "Dairy boost: Sprinkle 20g of goat cheese or cottage cheese before covering."
        ],
        "storage_tips": "Best enjoyed fresh for runny yolks. Leftover sauce can be saved for up to 3 days and topped with fresh eggs when reheated."
    }
}


def generate_recipe(
    image: Image.Image,
    params: Dict[str, Any],
    gemini_service: GeminiService
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Main recipe generation coordinator.
    Returns: (success: bool, recipe_data: Dict[str, Any], notice_or_error: str)
    """
    # Check if real API key configured
    if gemini_service.is_configured:
        prompt = build_recipe_prompt(params)
        success, raw_text, meta = gemini_service.generate_multimodal_content(image, prompt)
        
        if not success:
            # Report actual error
            return False, {}, meta.get("message", "Failed to generate recipe from AI.")

        # Parse JSON
        parsed_recipe = extract_json_from_response(raw_text)
        if not parsed_recipe or not isinstance(parsed_recipe, dict) or "title" not in parsed_recipe:
            # Fallback parsing error
            return False, {}, "The AI generated text but the structured recipe could not be parsed. Please try again."

        parsed_recipe["is_demo"] = False
        parsed_recipe["model_used"] = meta.get("model_used", "Gemini Vision")
        return True, parsed_recipe, "Recipe generated successfully using Gemini Multimodal Vision!"

    else:
        # Offline Demo Mode Simulation
        goal = params.get("goal", "")
        if "Protein" in goal:
            demo_data = DEMO_RECIPES["High Protein"].copy()
        else:
            demo_data = DEMO_RECIPES["Vegetarian"].copy()

        # Adapt servings and meal type to user choice
        demo_data["servings"] = params.get("servings", 2)
        demo_data["meal_type"] = params.get("meal_type", "Dinner")
        demo_data["is_demo"] = True
        demo_data["provider"] = "Demo Mode (Mock Simulation - No API Key Set)"

        notice = (
            "DEMO MODE: Running with simulated visual analysis because no GEMINI_API_KEY was provided. "
            "To unlock real multimodal vision, paste your API key in the sidebar!"
        )
        return True, demo_data, notice
