# VisionFit AI – Multimodal Recipe & Workout Generator

> **Tagline:** *"See What You Have. Discover What You Can Do."*

VisionFit AI is an intelligent lifestyle web application that bridges food discovery and fitness planning in one modern platform. Utilizing Google Gemini's multimodal vision capabilities, VisionFit AI allows users to take a photo of ingredients available on their kitchen counter or fitness equipment in their home gym to instantly generate personalized, practical recipes and structured workout routines.

---

## 🌟 Key Features

### 🥗 1. AI Recipe Generator (Culinary Vision)
- **Visual Food Recognition:** Detects fresh produce, pantry staples, spices, and refrigerated items from uploaded photographs.
- **Uncertainty Transparency:** Explicitly tags ambiguous or partially visible items so users can verify before cooking.
- **Dietary Precision:** Strict guardrails for Vegetarian, Vegan, Eggetarian, and allergen safety (Peanuts, Gluten, Dairy, etc.).
- **Chef-Crafted Steps:** Clear, beginner-friendly instructions with timing and temperatures.
- **Approximate Nutritional Profiles:** Estimated calories, protein, carbohydrates, fats, and dietary fiber per serving.
- **Substitutions & Storage Advice:** Alternative ingredients and practical leftover storage tips.

### 🏋️‍♂️ 2. AI Workout Generator (Biomechanics Vision)
- **Equipment & Space Understanding:** Identifies dumbbells, kettlebells, resistance bands, pull-up bars, or open mat space.
- **Adaptive Structuring:** Tailored to user's fitness goal (Strength, General Fitness, Endurance, Mobility, Weight Management) and experience level (Beginner, Intermediate, Advanced).
- **Comprehensive Routine:**
  - **Dynamic Warm-Up:** Joint lubrication and mobility activation.
  - **Main Workout:** Sets, repetitions, rest periods, target muscles, proper form cues, common mistakes, and **easier alternatives** for scaling.
  - **Cool-Down:** Decompression stretches with hold durations.
- **Safety First:** Prompts users to inspect gear stability and stop if acute joint pain or dizziness occurs.

### ⚡ 3. Multimodal Gemini Integration
- Powered by Google's official **`google-genai`** SDK.
- Configurable model (defaults to `gemini-2.5-flash` with support for `gemini-2.0-flash` and `gemini-1.5-flash`).
- **Interactive In-Browser Configuration:** Set or change your API key directly in the sidebar or via `.env`.
- **Offline Demo Simulation Mode:** If no API key is provided, the application runs transparently in Demo Mode with realistic simulated responses so users can test immediately.

### ⭐ 4. Personal Favorites & Library
- Save custom recipes and workouts with one click.
- Persistent SQLite storage (`visionfit.db`) paired with Streamlit session state.
- Filter by category, view full details in an expander, and export to Markdown files (`.md`).
- Bulk clear and individual deletion controls.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **User Interface** | [Streamlit](https://streamlit.io/) (v1.35+) | Modern, responsive reactive web UI |
| **Multimodal Vision AI** | [Google Gen AI SDK](https://github.com/google-gemini/google-genai) (`google-genai`) | Official Python client for Gemini 2.5 / 1.5 |
| **Computer Vision / Preprocessing** | [Pillow (PIL)](https://pillow.readthedocs.io/) | Image validation, aspect-ratio resizing, format normalization |
| **Styling & Theme** | Custom Modern CSS | Dark Navy (`#0B0F19`), Charcoal, Emerald (`#10B981`), and Lime accents |
| **Database** | SQLite3 | Local persistence for favorites and history |
| **Language** | Python 3.11+ | Clean, modular, beginner-friendly architecture |

---

## 📁 Project Architecture

```
visionfit-ai/
├── app.py                     # Main Streamlit dashboard and page router
├── requirements.txt           # Python package dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules for secrets and caches
├── README.md                  # Complete documentation and setup guide
├── visionfit.db               # SQLite database for saved favorites
├── assets/
│   └── custom.css             # Premium SaaS dark stylesheet
├── services/
│   ├── __init__.py
│   ├── gemini_service.py      # Google Gen AI SDK integration & error handling
│   ├── image_service.py       # Pillow preprocessing & sample image generators
│   ├── recipe_service.py      # Recipe multimodal orchestration & demo recipes
│   ├── workout_service.py     # Workout multimodal orchestration & demo routines
│   └── storage_service.py     # SQLite persistence for favorites & metrics
├── utils/
│   ├── __init__.py
│   ├── prompts.py             # Multimodal prompt contracts for Gemini
│   ├── validators.py          # Image type, size, and dimension validators
│   └── formatting.py          # Markdown export and JSON extractors
└── tests/
    └── test_visionfit.py      # Automated pytest unit and integration test suite
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or higher installed (`python --version`)
- A modern web browser (Chrome, Edge, Firefox, Safari)
- *(Optional)* A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation

1. Open your terminal or PowerShell and navigate to the project folder:
   ```bash
   cd "path/to/visionfit-ai"
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. API Key Setup

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and paste your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   GEMINI_MODEL=gemini-2.5-flash
   ```
   *Tip: You can also enter or update your API key at runtime directly in the web app's sidebar!*

### 4. Running the Application

Launch the Streamlit web server:
```bash
streamlit run app.py
```
Or from the project root workspace:
```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite using `pytest`:
```bash
python -m pytest tests/ -v
```

All 10 unit and integration tests cover:
- Valid and invalid image formats (.jpg, .png, .webp, corrupted/empty files).
- Image downsampling and RGB normalization.
- Programmatic sample kitchen and gym visual generation.
- Structured JSON extraction from markdown responses.
- Prompt contract verification (dietary constraints, allergen safety, exercise scaling).
- SQLite storage CRUD operations (save, list, filter, count, delete).
- Offline Demo Mode fallback behavior.

---

## 🔍 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **"Gemini API key is not configured"** | No key in `.env` or sidebar | Expand the "🔑 Configure API Key" section in the sidebar and paste your key, or run in Demo Mode. |
| **"File size exceeds maximum limit of 10 MB"** | Uploaded image is too large | Compress your image or take a standard photo below 10 MB. |
| **"API rate limit or quota exceeded (429)"** | Free tier requests per minute limit reached | Wait 60 seconds before generating again, or switch to a different Gemini project. |
| **"Model not found"** | Older or retired model specified | Choose `gemini-2.5-flash` or `gemini-1.5-flash` in the sidebar model dropdown. |

---

## 🛡️ Medical & Safety Disclaimers

1. **Nutrition Estimates:** Nutritional values (calories, protein, carbohydrates, fats, fiber) are algorithmic approximations calculated from standard food databases. Actual numbers vary based on cooking oils, portion sizes, and specific brands.
2. **Allergen Alert:** While the AI is strictly instructed to avoid stated allergens, users must verify food labels and ingredients independently.
3. **Exercise Safety:** Inspect all exercise equipment for structural stability, secure bolts, and proper anchoring before use. An AI vision model cannot inspect hardware wear or tensile strength from an image.
4. **Physician Consultation:** Discontinue exercise immediately if you experience dizziness, chest pain, or acute joint distress. Consult a qualified medical practitioner before undertaking any new fitness regimen.

---

## 📜 License & Credits

Built with ❤️ for culinary creativity and functional fitness. Powered by **Google Gemini** and **Streamlit**.

