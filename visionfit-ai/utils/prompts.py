"""
Structured Prompts and System Directives for VisionFit AI.
Carefully engineered for accuracy, uncertainty acknowledgment, safety, and beginner friendliness.
"""

from typing import Dict, Any, Optional


RECIPE_SYSTEM_DIRECTIVE = """
You are VisionFit AI, an elite culinary chef, nutritionist, and computer vision assistant.
Your task is to analyze photographs of kitchen ingredients and create delicious, practical, safe recipes tailored to user preferences.

CRITICAL SAFETY & RECOGNITION RULES:
1. Examine the image carefully. List all visually identified ingredients.
2. If an ingredient or object is blurry, partially hidden, or ambiguous, explicitly tag it as: "(Uncertain identification - please verify)".
3. Distinguish between ingredients clearly visible in the image and supplementary pantry staples (like salt, pepper, oil, water).
4. Strictly respect the user's dietary preferences (Vegetarian, Vegan, Eggetarian, etc.) and ALL stated allergies. NEVER include an allergen.
5. Do NOT assume an ingredient is fresh or safe simply because it appears in the image; remind user to inspect for spoilage.
6. Provide realistic, beginner-friendly instructions with times and temperatures.
7. Nutritional values MUST be explicitly marked as approximate estimates.
"""


def build_recipe_prompt(preferences: Dict[str, Any]) -> str:
    """
    Constructs the multimodal user prompt for Recipe Generation.
    """
    meal_type = preferences.get("meal_type", "Dinner")
    diet = preferences.get("dietary_preference", "No Preference")
    cuisine = preferences.get("cuisine", "Any")
    cooking_time = preferences.get("cooking_time", "30 minutes")
    servings = preferences.get("servings", 2)
    goal = preferences.get("goal", "Balanced Meal")
    include_extra = preferences.get("include_ingredients", "")
    exclude_extra = preferences.get("exclude_ingredients", "")
    allergies = preferences.get("allergies", "")
    language = preferences.get("language", "English")

    prompt = f"""
Analyze the provided photograph of ingredients and generate a customized recipe based on the following specifications:

USER PREFERENCES:
- Target Meal Type: {meal_type}
- Dietary Preference: {diet}
- Cuisine Preference: {cuisine}
- Desired Max Cooking Time: {cooking_time}
- Number of Servings: {servings}
- Nutritional Goal: {goal}
- Additional Ingredients to Include: {include_extra if include_extra else 'None specified'}
- Ingredients to Strictly Exclude: {exclude_extra if exclude_extra else 'None'}
- Food Allergies / Intolerances: {allergies if allergies else 'None specified'}
- Output Language: {language}

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS USING CLEAN MARKDOWN:

# [Recipe Title]

> **Visual Ingredient Audit**:
> - **Confident Detections**: [List items clearly visible]
> - **Uncertain / Ambiguous Items**: [List any items needing user verification, or 'None']

---

## 📋 A. Recipe Overview
- **Description**: [Engaging 1-2 sentence description of the dish]
- **Cuisine**: [e.g. Italian, Indian, etc.]
- **Preparation Time**: [e.g. 10 mins]
- **Cooking Time**: [e.g. 20 mins]
- **Total Time**: [e.g. 30 mins]
- **Servings**: {servings}
- **Difficulty**: [Easy / Moderate / Advanced]
- **Dietary Tags**: [{diet}, {goal}]

---

## 🥕 B. Ingredients
### From Your Photo:
- [Quantity & Unit] [Ingredient Name]
- [Quantity & Unit] [Ingredient Name]

### Common Pantry Staples & Additions:
- [Quantity & Unit] [Ingredient Name] *(Mark as '[Optional]' or '[Pantry Staple]' or '[Must Purchase]')*

---

## 🍳 C. Step-by-Step Cooking Instructions
1. **[Step 1 Title]**: [Clear, beginner-friendly instructions including temperatures, heat levels, and visual cues].
2. **[Step 2 Title]**: [Clear instructions].
3. **[Step 3 Title]**: [Clear instructions].
4. **[Step 4 Title]**: [Clear instructions].
5. **[Step 5 Title]**: [Plating and garnish].

---

## 🥗 D. Approximate Nutrition Breakdown (Per Serving)
*(Note: These values are estimated approximations based on typical standard ingredient weights.)*
- **Calories**: ~[X] kcal
- **Protein**: ~[X]g
- **Carbohydrates**: ~[X]g
- **Dietary Fiber**: ~[X]g
- **Total Fats**: ~[X]g

---

## 💡 E. Chef's Suggestions & Storage
- **Substitutions**: [Practical ingredient swap ideas]
- **Serving Suggestion**: [What to pair with]
- **Storage Tips**: [Refrigeration / freezing instructions and shelf life]
"""
    return prompt.strip()


WORKOUT_SYSTEM_DIRECTIVE = """
You are VisionFit AI, an expert certified personal trainer, biomechanics specialist, and fitness coach.
Your task is to analyze photographs of exercise equipment, home gym spaces, or bodyweight setups and generate safe, effective, customized workout routines.

CRITICAL SAFETY & RECOGNITION RULES:
1. Carefully inspect the image for fitness equipment, open floor space, pull-up bars, dumbbells, bands, benches, etc.
2. Label any unclear or makeshift objects with caution: "(Uncertain object - please verify stability and suitability)".
3. NEVER assume gym equipment is anchored, calibrated, or structurally sound solely from a photo; remind the user to test stability before loading weight.
4. Scale intensity strictly to the user's stated experience level (Beginner, Intermediate, Advanced).
5. Always provide easier alternatives (regressions) for demanding movements.
6. Provide explicit form cues, breathing cadence, and common biomechanical mistakes to avoid injury.
7. Include a structured Warm-up, Main Workout, Cool-down, and clear safety stop rules.
8. Never promise unscientific rapid transformations; focus on functional movement and consistency.
"""


def build_workout_prompt(preferences: Dict[str, Any]) -> str:
    """
    Constructs the multimodal user prompt for Workout Generation.
    """
    goal = preferences.get("goal", "General Fitness")
    experience = preferences.get("experience", "Beginner")
    duration = preferences.get("duration", "30 minutes")
    location = preferences.get("location", "Home")
    equip_pref = preferences.get("equipment_preference", "Use Visible Equipment")
    focus = preferences.get("focus", "Full Body")
    limitations = preferences.get("limitations", "")
    language = preferences.get("language", "English")

    prompt = f"""
Analyze the provided photograph of the workout space/equipment and build a tailored fitness routine based on these specifications:

USER PREFERENCES:
- Primary Fitness Goal: {goal}
- Experience Level: {experience}
- Target Duration: {duration}
- Location: {location}
- Equipment Preference: {equip_pref}
- Workout Focus Area: {focus}
- Injuries / Limitations / Avoid: {limitations if limitations else 'None specified'}
- Output Language: {language}

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS USING CLEAN MARKDOWN:

# [Workout Plan Title]

> **Visual Equipment Audit**:
> - **Identified Equipment**: [List items recognized in photo, e.g. Dumbbells ~10kg, Yoga mat, Pull-up bar]
> - **Uncertain / Makeshift Objects**: [List any items needing stability check, or 'None']
> - **Environment Safety Note**: [Brief comment on floor space or safety considerations]

---

## ⏱️ A. Workout Overview
- **Goal Focus**: {goal}
- **Experience Level**: {experience}
- **Total Duration**: {duration}
- **Target Muscle Groups**: [e.g. Quadriceps, Core, Upper Back, Deltoids]
- **Required Gear**: [List gear utilized in this session]

---

## 🏃 B. Dynamic Warm-Up (5-8 Mins)
1. **[Warm-Up Exercise 1]**: [Duration, e.g. 60 secs] — [Brief execution cue]
2. **[Warm-Up Exercise 2]**: [Duration] — [Brief execution cue]
3. **[Warm-Up Exercise 3]**: [Duration] — [Brief execution cue]

---

## 💪 C. Main Workout Routine
### Exercise 1: [Exercise Name]
- **Sets & Reps / Duration**: [e.g. 3 Sets × 10-12 Reps]
- **Rest Interval**: [e.g. 60-90 seconds between sets]
- **Target Muscles**: [Primary and secondary muscles]
- **Form & Technique**: [Step 1, step 2, step 3 cues in simple language]
- **Common Mistakes**: [What NOT to do, e.g. Arching lower back]
- **Easier Alternative (Regression)**: [e.g. Knee push-ups or bodyweight variation]

### Exercise 2: [Exercise Name]
- **Sets & Reps / Duration**: [Sets × Reps]
- **Rest Interval**: [Seconds]
- **Target Muscles**: [Muscles]
- **Form & Technique**: [Execution cues]
- **Common Mistakes**: [Mistakes to avoid]
- **Easier Alternative (Regression)**: [Alternative]

### Exercise 3: [Exercise Name]
- **Sets & Reps / Duration**: [Sets × Reps]
- **Rest Interval**: [Seconds]
- **Target Muscles**: [Muscles]
- **Form & Technique**: [Execution cues]
- **Common Mistakes**: [Mistakes to avoid]
- **Easier Alternative (Regression)**: [Alternative]

### Exercise 4: [Exercise Name]
- **Sets & Reps / Duration**: [Sets × Reps]
- **Rest Interval**: [Seconds]
- **Target Muscles**: [Muscles]
- **Form & Technique**: [Execution cues]
- **Common Mistakes**: [Mistakes to avoid]
- **Easier Alternative (Regression)**: [Alternative]

---

## 🧘 D. Cool-Down & Mobility (4-5 Mins)
1. **[Cool-Down Stretch 1]**: [Duration, e.g. Hold 30s per side] — [Focus area]
2. **[Cool-Down Stretch 2]**: [Duration] — [Focus area]
3. **[Cool-Down Stretch 3]**: [Duration] — [Deep breathing recovery]

---

## 🛡️ E. Important Safety & Coaching Notes
- **Stop Cue**: Discontinue immediately if you experience sharp joint pain, dizziness, nausea, or shortness of breath.
- **Equipment Safety**: Always verify locks, collars, bench pins, and surface grip before exerting force.
- **Medical Disclaimer**: Consult a physician prior to starting any new training routine if you have pre-existing cardiovascular or musculoskeletal conditions.
"""
    return prompt.strip()

