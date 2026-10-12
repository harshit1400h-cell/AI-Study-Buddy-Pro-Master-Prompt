"""
VisionFit AI — Multimodal Recipe & Workout Generator
Main Streamlit Application Entrypoint.
"""

import os
import io
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import streamlit as st

# Load services and utilities
from services.gemini_service import GeminiService
from services.image_service import ImageService
from services.recipe_service import RecipeService
from services.workout_service import WorkoutService
from utils.validators import validate_image_file, sanitize_text_input
from utils.formatting import (
    format_export_file,
    generate_sample_recipe_markdown,
    generate_sample_workout_markdown,
)

# App Directory
APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"
SAMPLES_DIR = APP_DIR / "sample_images"

# Page configuration
st.set_page_config(
    page_title="VisionFit AI — Multimodal Food & Fitness",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_custom_css():
    """Injects custom CSS from assets/custom.css."""
    css_path = ASSETS_DIR / "custom.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_session_state():
    """Initializes Streamlit session state keys."""
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    if "recent_activity" not in st.session_state:
        st.session_state.recent_activity = []
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home Dashboard"
    if "recipe_result" not in st.session_state:
        st.session_state.recipe_result = None
    if "workout_result" not in st.session_state:
        st.session_state.workout_result = None
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False


def render_sidebar():
    """Renders the sidebar navigation, API configuration, and model settings."""
    with st.sidebar:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg,#10b981,#059669); display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:bold; color:white;">⚡</div>
                <div>
                    <div style="font-size:18px; font-weight:800; color:white; line-height:1.2;">VisionFit AI</div>
                    <div style="font-size:11px; color:#10b981; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Multimodal Assistant</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='margin:8px 0; border-color:rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

        # Main Navigation
        pages = [
            "Home Dashboard",
            "Recipe Generator",
            "Workout Generator",
            "My Favorites",
            "About VisionFit AI",
        ]
        
        icons = {
            "Home Dashboard": "🏠",
            "Recipe Generator": "🍲",
            "Workout Generator": "🏋️",
            "My Favorites": "⭐",
            "About VisionFit AI": "ℹ️",
        }

        # Format display with icons
        current_index = pages.index(st.session_state.active_page) if st.session_state.active_page in pages else 0
        selected = st.radio(
            "Navigation",
            options=pages,
            index=current_index,
            format_func=lambda x: f"{icons.get(x, '•')} {x}",
            label_visibility="collapsed",
        )
        st.session_state.active_page = selected

        st.markdown("<hr style='margin:14px 0; border-color:rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

        # Settings Section
        st.markdown("### ⚙️ AI Engine Settings")

        env_key_present = bool(os.getenv("GEMINI_API_KEY"))
        user_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get("user_gemini_key", ""),
            placeholder="Loaded from .env" if env_key_present else "Paste AIzaSy... key",
            help="Get your free API key from https://aistudio.google.com/",
        )
        if user_key:
            st.session_state.user_gemini_key = user_key

        effective_key = GeminiService.get_api_key(st.session_state.get("user_gemini_key"))

        # Configurable Model
        default_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        model_options = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        if default_model not in model_options:
            model_options.insert(0, default_model)

        selected_model = st.selectbox(
            "Gemini Vision Model",
            options=model_options,
            index=model_options.index(default_model) if default_model in model_options else 0,
            help="High-speed vision-capable Gemini models.",
        )
        st.session_state.selected_model = selected_model

        # Test Connection Button
        if st.button("🔌 Test API Connection", use_container_width=True):
            if not effective_key:
                st.warning("Please provide an API key above or in .env.")
            else:
                with st.spinner("Connecting to Google Gemini..."):
                    ok, msg = GeminiService.test_connection(effective_key, selected_model)
                    if ok:
                        st.success(f"Connected: {msg}")
                    else:
                        st.error(f"Failed: {msg}")

        # Demo Mode Toggle
        st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)
        demo_toggle = st.toggle(
            "🧪 Demo / Offline Inspection Mode",
            value=st.session_state.demo_mode,
            help="Enables simulated instant analysis if you want to inspect UI cards without calling the external API.",
        )
        st.session_state.demo_mode = demo_toggle

        # Favorites Counter
        fav_count = len(st.session_state.favorites)
        st.markdown(
            f"""
            <div style="background:rgba(15,23,42,0.6); padding:10px; border-radius:10px; border:1px solid rgba(255,255,255,0.06); text-align:center; margin-top:12px;">
                <span style="font-size:12px; color:#94a3b8;">Saved Favorites:</span>
                <span style="font-weight:700; color:#10b981; margin-left:6px;">{fav_count}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_home():
    """Renders the Home Dashboard page."""
    st.markdown(
        """
        <div class="vf-hero-badge">⚡ Multimodal Generative AI • Vision & Lifestyle</div>
        <div class="vf-hero-title">Your World. <span>Your Ingredients.</span> Your Fitness.</div>
        <div class="vf-hero-sub">
            Upload a photo of whatever ingredients are in your fridge or workout gear in your room.
            VisionFit AI instantly recognizes your items, checks nutritional balance, and crafts a bespoke recipe or workout routine.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mode Selection Cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="vf-card">
                <div style="font-size:32px; margin-bottom:8px;">🍲</div>
                <h3 style="margin:0 0 8px 0; color:#f8fafc; font-size:1.35rem; font-weight:800;">AI Recipe Generator</h3>
                <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5; margin-bottom:14px;">
                    Turn raw ingredients, vegetable crisper contents, or pantry shelves into delicious chef-quality recipes with approximate calories and step-by-step instructions.
                </p>
                <div style="margin-bottom:16px;">
                    <span class="vf-pill vf-pill-green">Ingredient Audit</span>
                    <span class="vf-pill vf-pill-blue">Nutrition Estimates</span>
                    <span class="vf-pill vf-pill-amber">Allergy Aware</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Recipe Generator ➔", key="home_btn_recipe", use_container_width=True):
            st.session_state.active_page = "Recipe Generator"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="vf-card">
                <div style="font-size:32px; margin-bottom:8px;">🏋️</div>
                <h3 style="margin:0 0 8px 0; color:#f8fafc; font-size:1.35rem; font-weight:800;">AI Workout Generator</h3>
                <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5; margin-bottom:14px;">
                    Transform dumbbells, bands, pull-up bars, or open floor spaces into structured, biomechanically sound fitness routines complete with warm-ups, reps, and form cues.
                </p>
                <div style="margin-bottom:16px;">
                    <span class="vf-pill vf-pill-green">Equipment Detection</span>
                    <span class="vf-pill vf-pill-purple">Form Guidance</span>
                    <span class="vf-pill vf-pill-blue">Regressions</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Workout Generator ➔", key="home_btn_workout", use_container_width=True):
            st.session_state.active_page = "Workout Generator"
            st.rerun()

    # How it Works Section
    st.markdown("<h3 style='margin-top:2.5rem; color:#f8fafc;'>🚀 How VisionFit AI Works in 3 Steps</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="vf-card">
                <div style="color:#10b981; font-size:1.5rem; font-weight:800; font-family:'JetBrains Mono';">01</div>
                <h4 style="color:#f1f5f9; margin:6px 0;">Snap & Upload</h4>
                <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">Take a clear photo of your kitchen ingredients or available fitness gear.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="vf-card">
                <div style="color:#10b981; font-size:1.5rem; font-weight:800; font-family:'JetBrains Mono';">02</div>
                <h4 style="color:#f1f5f9; margin:6px 0;">Set Preferences</h4>
                <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">Customize dietary tags, target cook time, fitness goals, and limitations.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="vf-card">
                <div style="color:#10b981; font-size:1.5rem; font-weight:800; font-family:'JetBrains Mono';">03</div>
                <h4 style="color:#f1f5f9; margin:6px 0;">Cook or Train</h4>
                <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">Receive structured plans with ingredient checks, form cues, and nutrition.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Session Activity / Highlights
    st.markdown("<h3 style='margin-top:2rem; color:#f8fafc;'>📊 Session Overview</h3>", unsafe_allow_html=True)
    recipe_favs = len(RecipeService.get_favorites(st.session_state))
    workout_favs = len(WorkoutService.get_favorites(st.session_state))

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{recipe_favs}</div>
                <div class="vf-stat-lbl">Saved Recipes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{workout_favs}</div>
                <div class="vf-stat-lbl">Saved Workouts</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc3:
        api_status = "Online (Ready)" if GeminiService.get_api_key(st.session_state.get("user_gemini_key")) else "Requires Key / Demo"
        color = "#10b981" if "Online" in api_status else "#f59e0b"
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val" style="color:{color}; font-size:1.05rem;">{api_status}</div>
                <div class="vf-stat-lbl">AI Vision Status</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_recipe_generator():
    """Renders the AI Recipe Generator mode."""
    st.markdown(
        """
        <div style="margin-bottom:1.25rem;">
            <span class="vf-hero-badge">🍲 Mode 01 • Culinary Vision Assistant</span>
            <h2 style="margin:4px 0; color:#f8fafc; font-size:2rem; font-weight:800;">AI Recipe Generator</h2>
            <p style="color:#94a3b8; font-size:0.92rem;">Upload ingredient photos to generate delicious, balanced recipes based on what you have.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_upload, col_pref = st.columns([1, 1.1], gap="large")

    image_bytes = None
    mime_type = "image/jpeg"
    pil_image = None

    with col_upload:
        st.markdown("#### 1. Upload Ingredient Photo")
        uploaded_file = st.file_uploader(
            "Upload photo of ingredients, fridge contents, or vegetables",
            type=["jpg", "jpeg", "png", "webp"],
            help="Max size 10MB. Clear lighting and visible ingredients yield highest accuracy.",
            key="recipe_file_uploader",
        )

        # Quick Sample Image Button
        sample_path = SAMPLES_DIR / "sample_ingredients.jpg"
        if sample_path.exists():
            if st.button("🖼️ Or Load Sample Ingredients (Bell Peppers, Chickpeas, Garlic)", key="load_sample_recipe_img"):
                with open(sample_path, "rb") as sf:
                    st.session_state.recipe_sample_bytes = sf.read()
                    st.session_state.recipe_sample_name = "sample_ingredients.jpg"

        # Determine active image source
        active_raw = None
        active_name = ""

        if uploaded_file is not None:
            active_raw = uploaded_file.getvalue()
            active_name = uploaded_file.name
        elif "recipe_sample_bytes" in st.session_state:
            active_raw = st.session_state.recipe_sample_bytes
            active_name = st.session_state.recipe_sample_name

        if active_raw:
            is_valid, err_msg, loaded_img = validate_image_file(active_raw, active_name)
            if not is_valid:
                st.error(f"⚠️ Validation Error: {err_msg}")
            else:
                image_bytes, mime_type, pil_image = ImageService.preprocess_image_for_gemini(loaded_img)
                meta = ImageService.get_image_metadata(pil_image, image_bytes)

                st.image(pil_image, caption=f"📸 Preview: {active_name} ({meta['resolution']}, {meta['file_size']})", use_container_width=True)

                if st.button("❌ Remove Image", key="clear_recipe_img"):
                    if "recipe_sample_bytes" in st.session_state:
                        del st.session_state.recipe_sample_bytes
                    st.rerun()
        else:
            st.info("👆 Please upload an ingredient photo or click the sample button above.")

    with col_pref:
        st.markdown("#### 2. Recipe Preferences")
        c1, c2 = st.columns(2)
        with c1:
            meal_type = st.selectbox(
                "Meal Type",
                ["Dinner", "Lunch", "Breakfast", "Snack", "Post-Workout Meal"],
                index=0,
            )
            diet = st.selectbox(
                "Dietary Preference",
                ["No Preference", "Vegetarian", "Vegan", "Eggetarian"],
                index=1,
            )
            cuisine = st.selectbox(
                "Cuisine Preference",
                ["Any", "Indian", "Italian", "Asian", "Mediterranean"],
                index=4,
            )
            servings = st.slider("Servings", min_value=1, max_value=8, value=2)

        with c2:
            cooking_time = st.selectbox(
                "Max Cooking Time",
                ["10 minutes (Speed)", "20 minutes", "30 minutes (Standard)", "45+ minutes (Deep Flavor)"],
                index=2,
            )
            goal = st.selectbox(
                "Nutritional Goal",
                ["Balanced Meal", "High Protein", "General Healthy Eating", "Low Calorie / Light"],
                index=1,
            )
            language = st.selectbox("Output Language", ["English", "Hindi"], index=0)

        include_extra = st.text_input("Optional items to include", placeholder="e.g. olive oil, chili flakes, feta")
        exclude_extra = st.text_input("Strict exclusions", placeholder="e.g. mushrooms, cilantro, dairy")
        allergies = st.text_input("Food allergies", placeholder="e.g. peanuts, tree nuts, shellfish, gluten")

    preferences = {
        "meal_type": meal_type,
        "dietary_preference": diet,
        "cuisine": cuisine,
        "cooking_time": cooking_time,
        "servings": servings,
        "goal": goal,
        "include_ingredients": sanitize_text_input(include_extra),
        "exclude_ingredients": sanitize_text_input(exclude_extra),
        "allergies": sanitize_text_input(allergies),
        "language": language,
    }

    st.markdown("<hr style='margin:1.5rem 0; border-color:rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

    # Action Button
    can_generate = (image_bytes is not None)
    btn_label = "✨ Analyze Image & Generate Recipe" if can_generate else "Upload an Image Above to Generate"

    if st.button(btn_label, type="primary", disabled=not can_generate, use_container_width=True):
        api_key = GeminiService.get_api_key(st.session_state.get("user_gemini_key"))
        model_name = st.session_state.get("selected_model", "gemini-2.5-flash")

        # Check Demo Mode vs Real API
        if st.session_state.demo_mode or not api_key:
            if not api_key:
                st.info("💡 Note: No Gemini API Key configured. Generating high-fidelity inspection demo recipe based on your selected criteria.")
            with st.spinner("Analyzing ingredient textures, colors, and building recipe..."):
                sample_md = generate_sample_recipe_markdown(preferences)
                parsed = RecipeService.parse_recipe_output(sample_md, preferences)
                st.session_state.recipe_result = parsed
        else:
            with st.spinner(f"Analyzing photograph with {model_name} and generating customized recipe..."):
                success, content, parsed = RecipeService.generate_recipe(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    preferences=preferences,
                    api_key=api_key,
                    model_name=model_name
                )
                if not success:
                    st.error(f"❌ {content}")
                else:
                    st.session_state.recipe_result = parsed
                    st.success("🎉 Recipe generated successfully!")

    # Display Recipe Result if available
    result = st.session_state.recipe_result
    if result:
        render_recipe_result(result)


def render_recipe_result(result: Dict[str, Any]):
    """Renders the generated recipe output, cards, metrics, and actions."""
    st.markdown("<h3 style='margin-top:1.5rem; color:#f8fafc;'>🍽️ Generated Recipe</h3>", unsafe_allow_html=True)

    # Highlight Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">~{result.get('calories', '420')}</div>
                <div class="vf-stat-lbl">Calories (Est)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('protein', '18g')}</div>
                <div class="vf-stat-lbl">Est. Protein</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('total_time', '25m')}</div>
                <div class="vf-stat-lbl">Total Time</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('difficulty', 'Easy')}</div>
                <div class="vf-stat-lbl">Difficulty</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Action Toolbar
    act1, act2, act3 = st.columns([1, 1, 1])
    with act1:
        is_saved = any(f.get("id") == result.get("id") for f in st.session_state.favorites)
        fav_btn_label = "⭐ In Favorites" if is_saved else "⭐ Save to Favorites"
        if st.button(fav_btn_label, key="save_recipe_fav_btn", use_container_width=True):
            if not is_saved:
                RecipeService.save_to_favorites(st.session_state, result)
                st.toast("Saved recipe to favorites! ⭐")
                st.rerun()

    with act2:
        export_text = format_export_file(result)
        st.download_button(
            "📥 Download Recipe (.md)",
            data=export_text,
            file_name=f"{result.get('title', 'Recipe').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_recipe_btn",
        )

    with act3:
        if st.button("🔄 Generate Another Recipe", key="regen_recipe_btn", use_container_width=True):
            st.session_state.recipe_result = None
            st.rerun()

    # Markdown Content Card
    st.markdown(
        f"""
        <div class="vf-card vf-card-glow" style="margin-top:1rem;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(result.get("raw_markdown", ""))
    st.markdown("</div>", unsafe_allow_html=True)


def page_workout_generator():
    """Renders the AI Workout Generator mode."""
    st.markdown(
        """
        <div style="margin-bottom:1.25rem;">
            <span class="vf-hero-badge">🏋️ Mode 02 • Biomechanics & Training Assistant</span>
            <h2 style="margin:4px 0; color:#f8fafc; font-size:2rem; font-weight:800;">AI Workout Generator</h2>
            <p style="color:#94a3b8; font-size:0.92rem;">Upload photos of your gym equipment or home workout space to generate a structured, safe fitness routine.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_upload, col_pref = st.columns([1, 1.1], gap="large")

    image_bytes = None
    mime_type = "image/jpeg"
    pil_image = None

    with col_upload:
        st.markdown("#### 1. Upload Equipment / Space Photo")
        uploaded_file = st.file_uploader(
            "Upload photo of dumbbells, resistance bands, pull-up bar, mat, or floor space",
            type=["jpg", "jpeg", "png", "webp"],
            help="Max size 10MB. Ensure lighting shows available gear and floor area clearly.",
            key="workout_file_uploader",
        )

        sample_path = SAMPLES_DIR / "sample_equipment.jpg"
        if sample_path.exists():
            if st.button("🖼️ Or Load Sample Gear (Dumbbells, Mat, Kettlebell, Bands)", key="load_sample_workout_img"):
                with open(sample_path, "rb") as sf:
                    st.session_state.workout_sample_bytes = sf.read()
                    st.session_state.workout_sample_name = "sample_equipment.jpg"

        active_raw = None
        active_name = ""

        if uploaded_file is not None:
            active_raw = uploaded_file.getvalue()
            active_name = uploaded_file.name
        elif "workout_sample_bytes" in st.session_state:
            active_raw = st.session_state.workout_sample_bytes
            active_name = st.session_state.workout_sample_name

        if active_raw:
            is_valid, err_msg, loaded_img = validate_image_file(active_raw, active_name)
            if not is_valid:
                st.error(f"⚠️ Validation Error: {err_msg}")
            else:
                image_bytes, mime_type, pil_image = ImageService.preprocess_image_for_gemini(loaded_img)
                meta = ImageService.get_image_metadata(pil_image, image_bytes)

                st.image(pil_image, caption=f"📸 Preview: {active_name} ({meta['resolution']}, {meta['file_size']})", use_container_width=True)

                if st.button("❌ Remove Image", key="clear_workout_img"):
                    if "workout_sample_bytes" in st.session_state:
                        del st.session_state.workout_sample_bytes
                    st.rerun()
        else:
            st.info("👆 Please upload an equipment photo or click the sample button above.")

    with col_pref:
        st.markdown("#### 2. Workout Preferences")
        c1, c2 = st.columns(2)
        with c1:
            goal = st.selectbox(
                "Primary Fitness Goal",
                ["Strength", "General Fitness", "Endurance", "Mobility & Recovery", "Weight Management"],
                index=0,
            )
            experience = st.selectbox(
                "Experience Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=0,
            )
            duration = st.selectbox(
                "Session Duration",
                ["15 minutes (Quick)", "20 minutes", "30 minutes (Standard)", "45 minutes", "60 minutes"],
                index=2,
            )
            location = st.selectbox("Location", ["Home", "Gym", "Outdoor"], index=0)

        with c2:
            equip_pref = st.selectbox(
                "Equipment Preference",
                ["Use Visible Equipment", "Bodyweight Only (Floor Space)", "Minimal Gear Focus"],
                index=0,
            )
            focus = st.selectbox(
                "Workout Focus Area",
                ["Full Body", "Upper Body", "Lower Body", "Core & Abs", "Cardio & Conditioning"],
                index=0,
            )
            language = st.selectbox("Output Language", ["English", "Hindi"], index=0, key="workout_lang")

        limitations = st.text_input(
            "Injuries / Limitations / Movements to Avoid",
            placeholder="e.g. Lower back pain, bad left knee, no jumping",
        )

    preferences = {
        "goal": goal,
        "experience": experience,
        "duration": duration,
        "location": location,
        "equipment_preference": equip_pref,
        "focus": focus,
        "limitations": sanitize_text_input(limitations),
        "language": language,
    }

    st.markdown("<hr style='margin:1.5rem 0; border-color:rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

    can_generate = (image_bytes is not None)
    btn_label = "⚡ Analyze Gear & Generate Workout Routine" if can_generate else "Upload an Image Above to Generate"

    if st.button(btn_label, type="primary", disabled=not can_generate, use_container_width=True):
        api_key = GeminiService.get_api_key(st.session_state.get("user_gemini_key"))
        model_name = st.session_state.get("selected_model", "gemini-2.5-flash")

        if st.session_state.demo_mode or not api_key:
            if not api_key:
                st.info("💡 Note: No Gemini API Key configured. Generating high-fidelity inspection demo workout based on your selected criteria.")
            with st.spinner("Analyzing equipment, space boundaries, and formulating workout routine..."):
                sample_md = generate_sample_workout_markdown(preferences)
                parsed = WorkoutService.parse_workout_output(sample_md, preferences)
                st.session_state.workout_result = parsed
        else:
            with st.spinner(f"Analyzing workout space with {model_name} and generating customized routine..."):
                success, content, parsed = WorkoutService.generate_workout(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    preferences=preferences,
                    api_key=api_key,
                    model_name=model_name
                )
                if not success:
                    st.error(f"❌ {content}")
                else:
                    st.session_state.workout_result = parsed
                    st.success("🎉 Workout routine generated successfully!")

    result = st.session_state.workout_result
    if result:
        render_workout_result(result)


def render_workout_result(result: Dict[str, Any]):
    """Renders the generated workout routine, cards, and export actions."""
    st.markdown("<h3 style='margin-top:1.5rem; color:#f8fafc;'>💪 Generated Workout Routine</h3>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('duration', '30m')}</div>
                <div class="vf-stat-lbl">Duration</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('exercise_count', 4)}</div>
                <div class="vf-stat-lbl">Key Exercises</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('experience', 'Beginner')}</div>
                <div class="vf-stat-lbl">Level</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="vf-stat-box">
                <div class="vf-stat-val">{result.get('goal', 'Fitness')}</div>
                <div class="vf-stat-lbl">Focus Goal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    act1, act2, act3 = st.columns([1, 1, 1])
    with act1:
        is_saved = any(f.get("id") == result.get("id") for f in st.session_state.favorites)
        fav_btn_label = "⭐ In Favorites" if is_saved else "⭐ Save to Favorites"
        if st.button(fav_btn_label, key="save_workout_fav_btn", use_container_width=True):
            if not is_saved:
                WorkoutService.save_to_favorites(st.session_state, result)
                st.toast("Saved workout to favorites! ⭐")
                st.rerun()

    with act2:
        export_text = format_export_file(result)
        st.download_button(
            "📥 Download Workout (.md)",
            data=export_text,
            file_name=f"{result.get('title', 'Workout').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_workout_btn",
        )

    with act3:
        if st.button("🔄 Generate Another Workout", key="regen_workout_btn", use_container_width=True):
            st.session_state.workout_result = None
            st.rerun()

    st.markdown(
        f"""
        <div class="vf-card vf-card-glow" style="margin-top:1rem;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(result.get("raw_markdown", ""))
    st.markdown("</div>", unsafe_allow_html=True)


def page_favorites():
    """Renders the My Favorites saved recipes and workouts."""
    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
            <h2 style="margin:4px 0; color:#f8fafc; font-size:2rem; font-weight:800;">⭐ My Saved Favorites</h2>
            <p style="color:#94a3b8; font-size:0.92rem;">Review, download, or manage all saved recipes and workout routines from this session.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    favs = st.session_state.favorites
    if not favs:
        st.markdown(
            """
            <div class="vf-card" style="text-align:center; padding:3rem 1.5rem;">
                <div style="font-size:48px; margin-bottom:12px;">📂</div>
                <h3 style="color:#f1f5f9; margin-bottom:6px;">No Saved Items Yet</h3>
                <p style="color:#94a3b8; max-width:400px; margin:0 auto 1.5rem auto; font-size:0.9rem;">
                    When you generate recipes or workouts you like, click "Save to Favorites" to keep them organized here.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create a Recipe ➔", use_container_width=True):
                st.session_state.active_page = "Recipe Generator"
                st.rerun()
        with c2:
            if st.button("Build a Workout ➔", use_container_width=True):
                st.session_state.active_page = "Workout Generator"
                st.rerun()
        return

    tab_recipes, tab_workouts = st.tabs(["🍲 Saved Recipes", "🏋️ Saved Workouts"])

    recipe_items = [f for f in favs if f.get("type") == "recipe"]
    workout_items = [f for f in favs if f.get("type") == "workout"]

    with tab_recipes:
        if not recipe_items:
            st.info("No recipes saved yet in this session.")
        else:
            for item in recipe_items:
                with st.expander(f"🍲 {item.get('title')} ({item.get('created_at')})", expanded=False):
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"**Estimated Calories**: ~{item.get('calories')} kcal • **Total Time**: {item.get('total_time')}")
                    with col_del:
                        if st.button("🗑️ Delete", key=f"del_rec_{item['id']}"):
                            RecipeService.remove_from_favorites(st.session_state, item["id"])
                            st.toast("Removed from favorites")
                            st.rerun()

                    st.markdown("---")
                    st.markdown(item.get("raw_markdown", ""))

                    # Download button
                    st.download_button(
                        "📥 Download (.md)",
                        data=format_export_file(item),
                        file_name=f"{item.get('title', 'Recipe').replace(' ', '_')}.md",
                        mime="text/markdown",
                        key=f"dl_rec_{item['id']}",
                    )

    with tab_workouts:
        if not workout_items:
            st.info("No workouts saved yet in this session.")
        else:
            for item in workout_items:
                with st.expander(f"🏋️ {item.get('title')} ({item.get('created_at')})", expanded=False):
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"**Duration**: {item.get('duration')} • **Level**: {item.get('experience')} • **Goal**: {item.get('goal')}")
                    with col_del:
                        if st.button("🗑️ Delete", key=f"del_work_{item['id']}"):
                            WorkoutService.remove_from_favorites(st.session_state, item["id"])
                            st.toast("Removed from favorites")
                            st.rerun()

                    st.markdown("---")
                    st.markdown(item.get("raw_markdown", ""))

                    st.download_button(
                        "📥 Download (.md)",
                        data=format_export_file(item),
                        file_name=f"{item.get('title', 'Workout').replace(' ', '_')}.md",
                        mime="text/markdown",
                        key=f"dl_work_{item['id']}",
                    )


def page_about():
    """Renders the About VisionFit AI page."""
    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
            <span class="vf-hero-badge">ℹ️ Architecture & Vision</span>
            <h2 style="margin:4px 0; color:#f8fafc; font-size:2rem; font-weight:800;">About VisionFit AI</h2>
            <p style="color:#94a3b8; font-size:0.92rem;">Empowering home cooks, fitness enthusiasts, and students with multimodal computer vision.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="vf-card">
            <h3 style="color:#f8fafc; margin-top:0;">🌟 The VisionFit AI Philosophy</h3>
            <p style="color:#cbd5e1; line-height:1.6;">
                Most fitness and food apps demand exhaustive manual logging, barcodes, and tedious database searches.
                <strong>VisionFit AI</strong> approaches the problem with a human-centric paradigm:
                <em>"See What You Have. Discover What You Can Do."</em>
            </p>
            <p style="color:#cbd5e1; line-height:1.6;">
                By utilizing Google's state-of-the-art multimodal Gemini models via the official <code>google-genai</code> SDK,
                the application parses visual tokens representing vegetables, proteins, weights, dumbbells, and floor dimensions,
                synthesizing custom plans in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="vf-card">
                <h4 style="color:#10b981;">🛡️ Safety & Honesty Protocol</h4>
                <ul style="color:#94a3b8; font-size:0.88rem; line-height:1.6;">
                    <li><strong>Uncertainty Tagging:</strong> The model explicitly labels ambiguous objects rather than hallucinating false certainty.</li>
                    <li><strong>Nutritional Estimates:</strong> Caloric and macronutrient breakdowns are approximate and marked as such.</li>
                    <li><strong>Biomechanics & Form:</strong> Every exercise includes execution cues, common pitfalls, and easier regressions.</li>
                    <li><strong>Equipment Stability:</strong> Photos cannot verify floor grip or screw tightness; users are reminded to inspect gear.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="vf-card">
                <h4 style="color:#38bdf8;">🛠️ Modern Tech Stack</h4>
                <ul style="color:#94a3b8; font-size:0.88rem; line-height:1.6;">
                    <li><strong>Frontend:</strong> Streamlit 1.65+ with custom SaaS Navy/Lime CSS design system.</li>
                    <li><strong>Multimodal Engine:</strong> Google Gemini API via official <code>google-genai</code> SDK.</li>
                    <li><strong>Image Pipeline:</strong> Pillow (PIL) for EXIF re-orientation, validation, and Lanczos downsampling.</li>
                    <li><strong>Architecture:</strong> Fully decoupled modular services (Gemini, Image, Recipe, Workout).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="vf-card">
            <h4 style="color:#f8fafc;">💡 Frequently Asked Questions</h4>
            <details style="margin-bottom:10px; color:#cbd5e1;">
                <summary style="cursor:pointer; font-weight:600; color:#34d399;">Where do I get a Gemini API Key?</summary>
                <p style="margin-top:6px; color:#94a3b8; font-size:0.9rem;">
                    Visit <a href="https://aistudio.google.com/" target="_blank" style="color:#10b981;">Google AI Studio</a>, sign in with your Google account, and click <em>Create API Key</em>. It provides a generous free tier for developers.
                </p>
            </details>
            <details style="margin-bottom:10px; color:#cbd5e1;">
                <summary style="cursor:pointer; font-weight:600; color:#34d399;">Can I test the app without an API Key?</summary>
                <p style="margin-top:6px; color:#94a3b8; font-size:0.9rem;">
                    Yes! Toggle <strong>Demo / Offline Inspection Mode</strong> in the sidebar. This allows full inspection of all UI cards, metrics, and markdown export features without calling the external API.
                </p>
            </details>
            <details style="color:#cbd5e1;">
                <summary style="cursor:pointer; font-weight:600; color:#34d399;">Are API keys stored or exposed?</summary>
                <p style="margin-top:6px; color:#94a3b8; font-size:0.9rem;">
                    No. Keys are read securely from your local <code>.env</code> file or ephemeral session state and are never transmitted to any third party other than Google's official API endpoint.
                </p>
            </details>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    """Application runner."""
    init_session_state()
    load_custom_css()
    render_sidebar()

    # Router
    active_page = st.session_state.active_page
    if active_page == "Home Dashboard":
        page_home()
    elif active_page == "Recipe Generator":
        page_recipe_generator()
    elif active_page == "Workout Generator":
        page_workout_generator()
    elif active_page == "My Favorites":
        page_favorites()
    elif active_page == "About VisionFit AI":
        page_about()


if __name__ == "__main__":
    main()

