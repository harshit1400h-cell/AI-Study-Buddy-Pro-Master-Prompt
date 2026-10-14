"""
Formatting and Parsing Utilities for VisionFit AI
Handles Markdown export, JSON extraction from LLM outputs, and data rendering.
"""

import json
import re
from typing import Dict, Any, Optional


def extract_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts JSON object from AI model response.
    Tolerates markdown code fences (```json ... ``` or ``` ... ```).
    """
    if not text:
        return None

    text = text.strip()

    # Try 1: Direct JSON parsing
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try 2: Look for ```json ... ``` blocks
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except Exception:
            pass

    # Try 3: Look for outer curly braces { ... }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None


def format_recipe_markdown(recipe_data: Dict[str, Any]) -> str:
    """Formats structured recipe data into clean, exportable Markdown."""
    title = recipe_data.get("title", "Delicious Homemade Recipe")
    cuisine = recipe_data.get("cuisine", "General")
    meal_type = recipe_data.get("meal_type", "Meal")
    prep_time = recipe_data.get("prep_time_minutes", 15)
    cook_time = recipe_data.get("cook_time_minutes", 20)
    total_time = recipe_data.get("total_time_minutes", prep_time + cook_time)
    servings = recipe_data.get("servings", 2)
    difficulty = recipe_data.get("difficulty", "Medium")
    desc = recipe_data.get("description", "")
    
    vis_ing = recipe_data.get("visually_identified_ingredients", [])
    uncertain = recipe_data.get("uncertain_items", [])
    ingredients = recipe_data.get("ingredients", [])
    steps = recipe_data.get("steps", [])
    nutrition = recipe_data.get("nutrition_estimates", {})
    substitutions = recipe_data.get("substitutions", [])
    storage_tips = recipe_data.get("storage_tips", "")

    md = [
        f"# 🥗 {title}",
        f"**Cuisine:** {cuisine} | **Meal Type:** {meal_type} | **Difficulty:** {difficulty}",
        f"**Prep Time:** {prep_time} mins | **Cook Time:** {cook_time} mins | **Total Time:** {total_time} mins | **Servings:** {servings}",
        "",
        f"*{desc}*",
        "",
        "---",
        "## 🔍 Visual Item Analysis",
    ]

    if vis_ing:
        md.append(f"- **Confirmed Identified Ingredients:** {', '.join(vis_ing)}")
    if uncertain:
        md.append(f"- **Uncertain / Unclear Items:** {', '.join(uncertain)} *(please verify before cooking)*")
    
    md.extend([
        "",
        "## 🛒 Ingredients",
    ])

    for item in ingredients:
        name = item.get("name", "Ingredient")
        qty = item.get("quantity", "")
        unit = item.get("unit", "")
        is_optional = item.get("is_optional", False)
        need_to_buy = item.get("need_to_buy", False)
        
        tags = []
        if is_optional:
            tags.append("optional")
        if need_to_buy:
            tags.append("pantry / need to purchase")
        
        tag_str = f" *({', '.join(tags)})*" if tags else ""
        qty_str = f"{qty} {unit}".strip()
        if qty_str:
            md.append(f"- **{qty_str}** {name}{tag_str}")
        else:
            md.append(f"- {name}{tag_str}")

    md.extend([
        "",
        "## 👩‍🍳 Step-by-Step Cooking Instructions",
    ])

    for i, step in enumerate(steps, 1):
        if isinstance(step, dict):
            instruction = step.get("instruction", "")
            temp_or_time = step.get("time_or_temp", "")
            time_note = f" *({temp_or_time})*" if temp_or_time else ""
            md.append(f"{i}. {instruction}{time_note}")
        else:
            md.append(f"{i}. {step}")

    md.extend([
        "",
        "## 📊 Approximate Nutrition Estimates (Per Serving)",
        "> **Notice:** All nutritional values are algorithmic approximations based on standard ingredient tables. Actual values depend on specific brands, cooking oils, and precise portions.",
        "",
    ])

    cals = nutrition.get("calories", "N/A")
    protein = nutrition.get("protein_g", "N/A")
    carbs = nutrition.get("carbs_g", "N/A")
    fats = nutrition.get("fats_g", "N/A")
    fiber = nutrition.get("fiber_g", "N/A")

    md.append(f"- **Calories:** ~{cals} kcal")
    md.append(f"- **Protein:** ~{protein} g")
    md.append(f"- **Carbohydrates:** ~{carbs} g")
    md.append(f"- **Fats:** ~{fats} g")
    if fiber != "N/A":
        md.append(f"- **Dietary Fiber:** ~{fiber} g")

    if substitutions or storage_tips:
        md.extend(["", "## 💡 Chef's Suggestions & Storage"])
        if substitutions:
            md.append("**Substitutions:**")
            for sub in substitutions:
                md.append(f"- {sub}")
        if storage_tips:
            md.append(f"\n**Storage & Freshness:**\n- {storage_tips}")

    md.extend([
        "",
        "---",
        "*Generated by VisionFit AI — See What You Have. Discover What You Can Do.*"
    ])

    return "\n".join(md)


def format_workout_markdown(workout_data: Dict[str, Any]) -> str:
    """Formats structured workout data into clean, exportable Markdown."""
    title = workout_data.get("title", "Custom Fitness Session")
    goal = workout_data.get("goal", "General Fitness")
    experience = workout_data.get("experience_level", "All Levels")
    duration = workout_data.get("estimated_duration_minutes", 30)
    focus = workout_data.get("workout_focus", "Full Body")
    location = workout_data.get("location", "Home / Gym")
    desc = workout_data.get("description", "")
    
    vis_eq = workout_data.get("visually_identified_equipment", [])
    uncertain = workout_data.get("uncertain_equipment", [])
    target_muscles = workout_data.get("target_muscle_groups", [])
    
    warmup = workout_data.get("warmup", [])
    exercises = workout_data.get("main_exercises", [])
    cooldown = workout_data.get("cooldown", [])
    safety_notes = workout_data.get("safety_reminders", [])

    md = [
        f"# 🏋️‍♂️ {title}",
        f"**Goal:** {goal} | **Level:** {experience} | **Duration:** {duration} mins | **Focus:** {focus}",
        f"**Target Muscles:** {', '.join(target_muscles) if target_muscles else 'Full Body'}",
        "",
        f"*{desc}*",
        "",
        "---",
        "## 🔍 Equipment & Space Analysis",
    ]

    if vis_eq:
        md.append(f"- **Identified Equipment:** {', '.join(vis_eq)}")
    else:
        md.append("- **Equipment:** Bodyweight / Minimal space")
    if uncertain:
        md.append(f"- **Uncertain / Incomplete Items:** {', '.join(uncertain)} *(verify stability and safety before use)*")

    md.extend([
        "",
        "## 🔥 Warm-Up (5-8 Minutes)",
    ])

    for i, w in enumerate(warmup, 1):
        if isinstance(w, dict):
            name = w.get("name", "Dynamic Movement")
            dur = w.get("duration", "45s")
            cue = w.get("instructions", "")
            md.append(f"{i}. **{name}** ({dur}) — {cue}")
        else:
            md.append(f"{i}. {w}")

    md.extend([
        "",
        "## ⚡ Main Workout Routine",
    ])

    for i, ex in enumerate(exercises, 1):
        name = ex.get("name", f"Exercise {i}")
        sets = ex.get("sets", "3")
        reps = ex.get("reps_or_duration", "10-12 reps")
        rest = ex.get("rest_seconds", "60s")
        muscles = ex.get("target_muscles", "")
        technique = ex.get("technique_cues", "")
        mistake = ex.get("common_mistake", "")
        alt = ex.get("easier_alternative", "")

        md.append(f"### {i}. {name}")
        md.append(f"**Sets & Volume:** {sets} sets × {reps} | **Rest:** {rest} | **Muscles:** {muscles}")
        if technique:
            md.append(f"- **Proper Form:** {technique}")
        if mistake:
            md.append(f"- **Avoid This Mistake:** {mistake}")
        if alt:
            md.append(f"- **Easier Alternative:** {alt}")
        md.append("")

    md.extend([
        "## 🧘 Cool-Down & Mobility (3-5 Minutes)",
    ])

    for i, c in enumerate(cooldown, 1):
        if isinstance(c, dict):
            name = c.get("name", "Stretch")
            dur = c.get("duration", "30s each side")
            cue = c.get("instructions", "")
            md.append(f"- **{name}** ({dur}) — {cue}")
        else:
            md.append(f"- {c}")

    md.extend([
        "",
        "## 🛡️ Critical Safety Notice",
        "> **Important:** Inspect all equipment for stability and wear before starting. Stop immediately if you experience sharp pain, lightheadedness, or breathing distress. This plan is for general wellness; consult a physician before starting any new exercise routine if you have existing health conditions.",
    ])

    if safety_notes:
        for note in safety_notes:
            md.append(f"- {note}")

    md.extend([
        "",
        "---",
        "*Generated by VisionFit AI — See What You Have. Discover What You Can Do.*"
    ])

    return "\n".join(md)

