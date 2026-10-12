# VisionFit AI — Multimodal Recipe & Workout Generator ⚡

> *"See What You Have. Discover What You Can Do."*

**VisionFit AI** is an intelligent lifestyle web application that combines food discovery and fitness planning in one platform. By utilizing multimodal Generative AI powered by Google's vision-capable Gemini models, users can upload photos of raw kitchen ingredients or home gym equipment and receive tailored recipes and workout routines.

---

## 🌟 Key Features

### 1. 🍲 AI Recipe Generator Mode
- **Visual Ingredient Audit**: Examines uploaded photographs of pantry staples, produce, and refrigerator contents.
- **Uncertainty Acknowledgment**: Explicitly flags ambiguous or blurry ingredients for user verification rather than hallucinating false certainty.
- **Personalized Cooking Criteria**:
  - Meal Type: Breakfast, Lunch, Dinner, Snack, Post-Workout
  - Dietary Tag: No Preference, Vegetarian, Vegan, Eggetarian
  - Cuisine: Indian, Italian, Asian, Mediterranean, Any
  - Max Cook Time: 10, 20, 30, 45+ minutes
  - Servings: 1 to 8 people
  - Custom inclusions, exclusions, and allergy constraints
- **Structured Output**:
  - Detailed recipe title & description
  - Preparation, cooking, and total time
  - Ingredients from photo vs. common pantry staples vs. items to purchase
  - Clear, numbered step-by-step cooking instructions
  - Estimated caloric and macronutrient breakdown (calories, protein, carbs, fats, fiber)
  - Chef substitutions, pairing suggestions, and food storage guidance
- **Interactive Tools**: 1-click **Save to Favorites**, **Copy Markdown**, and **Download (.md)**.

### 2. 🏋️ AI Workout Generator Mode
- **Visual Equipment Detection**: Detects dumbbells, kettlebells, barbells, resistance bands, pull-up bars, benches, and open floor space.
- **Environment & Gear Safety Check**: Reminds users to verify surface grip and equipment stability before loading weight.
- **Customizable Training Preferences**:
  - Primary Goal: Strength, General Fitness, Endurance, Mobility, Weight Management
  - Experience Level: Beginner, Intermediate, Advanced
  - Session Duration: 15, 20, 30, 45, 60 minutes
  - Location: Home, Gym, Outdoor
  - Equipment Preference: Use Visible Equipment, Bodyweight Only
  - Focus Area: Full Body, Upper Body, Lower Body, Core, Cardio
  - Injury & Movement Limitations: e.g., "no jumping", "lower back pain"
- **Structured Routine**:
  - Overview with target muscle groups and gear needed
  - Dynamic Warm-up (5–8 minutes) with mobilization cues
  - Main Workout: Sets, repetitions, rest intervals, execution technique, common mistakes, and easier regressions
  - Cool-down & Mobility stretches
  - Stop cues for pain or dizziness
- **Interactive Tools**: **Save to Favorites**, **Copy Plan**, and **Download (.md)**.

### 3. ⭐ My Favorites & Export Dashboard
- Organized tabs for saved recipes and workout routines.
- Expandable cards with dates, metrics, and full plan details.
- Clean Markdown (`.md`) export generator with export timestamp headers.
- Individual deletion or session management.

### 4. 🎨 Premium SaaS Dark UI/UX
- Custom dark navy and charcoal background (`#080d1a`, `#0f172a`, `#1e293b`).
- Electric lime / emerald green accent (`#10b981`, `#34d399`).
- Metric cards, stat grids, pill tags, and smooth hover transitions.
- Responsive layout across desktop, tablet, and mobile browsers.

---

## 🏗️ Project Architecture

```
visionfit-ai/
├── app.py                      # Main Streamlit application and page router
├── requirements.txt            # Python package dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions for secrets and bytecode
├── README.md                   # Comprehensive documentation
├── test_visionfit.py           # Automated unit and integration test suite
├── create_sample_images.py     # Test image generator utility
├── services/
│   ├── __init__.py             # Service exports
│   ├── gemini_service.py       # Official google-genai client & multimodal calls
│   ├── image_service.py        # PIL preprocessing, resizing, EXIF rotation
│   ├── recipe_service.py       # Recipe generation, parsing, favorites
│   └── workout_service.py      # Workout generation, parsing, favorites
├── utils/
│   ├── __init__.py             # Utility exports
│   ├── prompts.py              # Structured system instructions & user prompts
│   ├── validators.py           # File size, mime type, corruption validation
│   └── formatting.py           # Markdown card generators and demo templates
├── assets/
│   └── custom.css              # Dark SaaS Navy & Emerald/Lime styles
└── sample_images/              # Pre-packaged test images for instant testing
    ├── sample_ingredients.jpg  # Bell peppers, chickpeas, garlic, olive oil
    └── sample_equipment.jpg    # Dumbbells, yoga mat, kettlebell, bands
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or compatible version installed.
- Free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 2. Installation
Navigate to the project directory and install the requirements:
```bash
cd visionfit-ai
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the `visionfit-ai` folder (or copy from `.env.example`):
```bash
cp .env.example .env
```
Add your API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MAX_IMAGE_SIZE_MB=10
```
*(Alternatively, you can paste your API key directly into the application's sidebar input at runtime.)*

### 4. Run the Application
Launch with Streamlit:
```bash
streamlit run app.py
```
Or double-click `run_visionfit.bat` from the root directory on Windows.

Open your browser to:
```
http://localhost:8501
```

---

## 🧪 Automated Testing
Run the 10-point verification test suite:
```bash
python test_visionfit.py
```
**Tests Covered:**
1. Valid image acceptance and dimension checks.
2. Rejection of empty, non-image, and corrupted files.
3. Image preprocessing (RGBA conversion, Lanczos downsampling, JPEG encoding).
4. User text input sanitization.
5. Recipe prompt construction with dietary and allergy constraints.
6. Workout prompt construction with experience and injury limitations.
7. Recipe markdown parsing and session state favorites management.
8. Workout markdown parsing and session state favorites management.
9. Standalone Markdown export formatting.
10. Gemini service connection handling and informative error mapping.

---

## 🛡️ Safety & Medical Disclaimers
1. **Visual Recognition**: Image analysis is an AI-assisted estimate. Users must inspect food items for spoilage and verify potential allergens.
2. **Exercise Guidance**: Physical activity carries inherent risks. Users should stop immediately if experiencing pain, dizziness, or shortness of breath.
3. **Equipment Stability**: A photograph cannot determine bolt tightness or floor stability. Inspect all exercise equipment before putting it into use.
4. **Nutrition Approximations**: Calorie and macronutrient estimates depend on actual portions, brands, and cooking oils used.

---

## 📄 License
MIT License. Built for students, home cooks, and fitness enthusiasts worldwide.

