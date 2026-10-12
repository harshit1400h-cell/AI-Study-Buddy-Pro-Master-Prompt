"""
Formatting and Export Utilities for VisionFit AI.
Provides downloadable Markdown/text generators and demo fallback templates.
"""

from typing import Dict, Any


def format_export_file(item_data: Dict[str, Any]) -> str:
    """
    Creates an exportable, standalone Markdown document with metadata and timestamps.
    """
    item_type = item_data.get("type", "Plan").capitalize()
    title = item_data.get("title", f"VisionFit {item_type}")
    created_at = item_data.get("created_at", "N/A")
    raw_md = item_data.get("raw_markdown", "")

    header = f"""<!--
  ==============================================================
  VisionFit AI — Generated {item_type} Plan
  Export Date: {created_at}
  Platform: VisionFit AI (Multimodal Food & Fitness Assistant)
  Tagline: See What You Have. Discover What You Can Do.
  ==============================================================
-->

"""
    return header + raw_md


def generate_sample_recipe_markdown(preferences: Dict[str, Any]) -> str:
    """
    High-fidelity sample recipe markdown for demonstration and inspection testing.
    """
    meal = preferences.get("meal_type", "Dinner")
    diet = preferences.get("dietary_preference", "Vegetarian")
    servings = preferences.get("servings", 2)
    time = preferences.get("cooking_time", "25 minutes")

    return f"""# 🥗 Mediterranean Charred Bell Pepper & Chickpea Protein Bowl

> **Visual Ingredient Audit**:
> - **Confident Detections**: Red & Yellow Bell Peppers, Canned Chickpeas, Garlic cloves, Fresh Basil leaves, Olive oil bottle.
> - **Uncertain / Ambiguous Items**: Small green leafy sprigs in background (Uncertain identification - please verify as parsley or cilantro).

---

## 📋 A. Recipe Overview
- **Description**: A nutrient-packed, vibrant Mediterranean skillet bowl pairing caramelized sweet peppers with crispy garlic-toasted chickpeas and fragrant herbs.
- **Cuisine**: Mediterranean
- **Preparation Time**: 10 mins
- **Cooking Time**: 15 mins
- **Total Time**: {time}
- **Servings**: {servings}
- **Difficulty**: Easy
- **Dietary Tags**: [{diet}, High Protein, Balanced Meal]

---

## 🥕 B. Ingredients
### From Your Photo:
- 2 Medium Bell Peppers (sliced into 1/2-inch strips)
- 1 Can (400g) Chickpeas (rinsed and thoroughly dried)
- 3 Cloves Fresh Garlic (minced)
- 1 Handful Fresh Basil (coarsely torn)
- 2 Tbsp Extra Virgin Olive Oil

### Common Pantry Staples & Additions:
- 1/2 Tsp Ground Cumin *(Pantry Staple)*
- 1/2 Tsp Smoked Paprika *(Pantry Staple)*
- 1/2 Tsp Sea Salt & Fresh Cracked Black Pepper *(Pantry Staple)*
- 1 Tbsp Lemon Juice *(Optional - for finishing brightness)*
- 50g Crumbled Feta Cheese or Hemp Seeds *(Optional - additional protein boost)*

---

## 🍳 C. Step-by-Step Cooking Instructions
1. **Prep & Dry**: Thoroughly pat chickpeas dry with a clean paper towel. Moisture is the enemy of crispiness.
2. **Sear Peppers**: Heat 1 tablespoon of olive oil in a wide stainless steel or cast-iron skillet over medium-high heat. Add sliced bell peppers. Sear undisturbed for 3-4 minutes until blistered edges appear. Transfer peppers to a side plate.
3. **Crisp Chickpeas**: Add the remaining tablespoon of oil to the same skillet. Add dried chickpeas, cumin, smoked paprika, salt, and black pepper. Sauté over medium heat, tossing frequently, for 6-8 minutes until golden and crunchy.
4. **Infuse Aromatics**: Lower heat to medium-low. Stir in minced garlic and cook for 60 seconds until fragrant without burning.
5. **Combine & Garnish**: Return charred bell peppers to skillet. Toss together for 1 minute to harmonize temperatures. Remove from heat, stir in fresh lemon juice and torn basil. Top with feta or hemp seeds if desired.

---

## 🥗 D. Approximate Nutrition Breakdown (Per Serving)
*(Note: These values are estimated approximations based on standard ingredient proportions.)*
- **Calories**: ~420 kcal
- **Protein**: ~18g
- **Carbohydrates**: ~52g
- **Dietary Fiber**: ~14g
- **Total Fats**: ~16g (primarily heart-healthy monounsaturated fats)

---

## 💡 E. Chef's Suggestions & Storage
- **Substitutions**: Swap chickpeas for canned white cannellini beans or firm cubed tofu.
- **Serving Suggestion**: Serve warm over a bed of quinoa, brown rice, or alongside warm pita bread.
- **Storage Tips**: Store in an airtight glass container in the refrigerator for up to 4 days. Reheat in a hot skillet for 2 minutes to restore crunch.
"""


def generate_sample_workout_markdown(preferences: Dict[str, Any]) -> str:
    """
    High-fidelity sample workout markdown for demonstration and inspection testing.
    """
    goal = preferences.get("goal", "Strength & Conditioning")
    exp = preferences.get("experience", "Beginner")
    duration = preferences.get("duration", "30 minutes")
    focus = preferences.get("focus", "Full Body")

    return f"""# ⚡ Full-Body Dumbbell & Functional Conditioning Circuit

> **Visual Equipment Audit**:
> - **Identified Equipment**: Pair of Hex Dumbbells (approx 7.5kg - 10kg), High-density Yoga Mat, Open floor space (~2m x 2m).
> - **Uncertain / Makeshift Objects**: Foam roller near wall (Optional for cool-down).
> - **Environment Safety Note**: Surface is flat and non-slip; ensure clear 360-degree perimeter around dumbbells.

---

## ⏱️ A. Workout Overview
- **Goal Focus**: {goal}
- **Experience Level**: {exp}
- **Total Duration**: {duration}
- **Target Muscle Groups**: Quadriceps, Hamstrings, Upper Back, Chest, Core stabilizers
- **Required Gear**: Dumbbells & Yoga Mat

---

## 🏃 B. Dynamic Warm-Up (6 Mins)
1. **Arm Circles & Torso Twists**: 60 seconds — Mobilize shoulder capsules and thoracic spine.
2. **Bodyweight Hip Openers & Glute Bridges**: 90 seconds — Activate posterior chain.
3. **Cat-Cow & Inchworms**: 2 minutes — Dynamic spinal decompression and hamstring prep.

---

## 💪 C. Main Workout Routine (3 Rounds • 45s Work / 30s Rest)

### Exercise 1: Dumbbell Goblet Squat
- **Sets & Reps / Duration**: 3 Sets × 10-12 Controlled Reps
- **Rest Interval**: 60 seconds between rounds
- **Target Muscles**: Quadriceps, Gluteus Maximus, Core
- **Form & Technique**: Hold one dumbbell vertically against upper chest. Stand feet shoulder-width apart. Inhale, hinge hips back and descend until thighs are parallel to ground. Drive through midfoot to stand.
- **Common Mistakes**: Knees caving inward or chest collapsing forward.
- **Easier Alternative (Regression)**: Bodyweight air squats targeting a chair or bench.

### Exercise 2: Neutral-Grip Dumbbell Floor Press
- **Sets & Reps / Duration**: 3 Sets × 10-12 Reps
- **Rest Interval**: 45 seconds
- **Target Muscles**: Pectoralis Major, Anterior Deltoids, Triceps
- **Form & Technique**: Lie flat on mat with knees bent. Hold dumbbells with palms facing each other. Lower elbows at a 45-degree angle until upper arms gently touch mat, then press up smoothly.
- **Common Mistakes**: Bouncing elbows off floor or flaring elbows out at 90 degrees.
- **Easier Alternative (Regression)**: Incline push-ups against a sturdy table or wall.

### Exercise 3: Supported Bent-Over Dumbbell Row
- **Sets & Reps / Duration**: 3 Sets × 10 Reps per side
- **Rest Interval**: 45 seconds
- **Target Muscles**: Latissimus Dorsi, Rhomboids, Biceps
- **Form & Technique**: Hinge forward at 45 degrees with flat spine. Pull elbow toward hip pocket, squeezing shoulder blade at peak contraction.
- **Common Mistakes**: Rounding lower spine or using momentum to jerk weight.
- **Easier Alternative (Regression)**: Resistance band seated rows or single dumbbell with hand braced on chair.

### Exercise 4: Dead Bug Core Stabilization
- **Sets & Reps / Duration**: 3 Sets × 12 Alternating Reps
- **Rest Interval**: 45 seconds
- **Target Muscles**: Transverse Abdominis, Deep Core
- **Form & Technique**: Lie on back with arms extended and knees at 90 degrees. Lower opposite arm and leg while pressing lower back firmly into the floor.
- **Common Mistakes**: Arching lower back off the floor.
- **Easier Alternative (Regression)**: Heel taps without extending the arm.

---

## 🧘 D. Cool-Down & Mobility (5 Mins)
1. **Child's Pose Breathing**: Hold 60 seconds — Lower back and lat relaxation.
2. **Kneeling Hip Flexor Stretch**: 45 seconds per side — Unwind anterior chain.
3. **Supine Figure-4 Glute Stretch**: 45 seconds per side — Relieve hip tension.

---

## 🛡️ E. Important Safety & Coaching Notes
- **Stop Cue**: Discontinue immediately if you experience sharp shooting pain, joint pinch, or dizziness.
- **Equipment Safety**: Place dumbbells on floor with handles aligned so they cannot roll underfoot.
- **Medical Disclaimer**: Listen to your body and adjust range of motion to your personal anatomy.
"""

