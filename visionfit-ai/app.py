"""
VisionFit AI – Multimodal Recipe & Workout Generator
====================================================
Tagline: "See What You Have. Discover What You Can Do."
A modern, responsive AI lifestyle assistant powered by Google Gemini Vision.
"""

import os
import streamlit as st
from PIL import Image
from pathlib import Path
from datetime import datetime

# Import custom services and utilities
from services.gemini_service import GeminiService, DEFAULT_GEMINI_MODEL
from services.image_service import (
    preprocess_image,
    image_to_bytes,
    generate_sample_ingredients_image,
    generate_sample_gym_image,
)
from services.recipe_service import generate_recipe
from services.workout_service import generate_workout
from services.storage_service import (
    init_db,
    save_favorite,
    get_favorites,
    delete_favorite,
    clear_all_favorites,
    get_favorites_counts,
)
from utils.validators import validate_uploaded_image, sanitize_text_input
from utils.formatting import format_recipe_markdown, format_workout_markdown

# Page configuration
st.set_page_config(
    page_title="VisionFit AI – Multimodal Recipe & Workout Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
init_db()

# Load Custom CSS
CSS_PATH = Path(__file__).resolve().parent / "assets" / "custom.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "navigation" not in st.session_state:
    st.session_state.navigation = "Home Dashboard"
if "recipe_image" not in st.session_state:
    st.session_state.recipe_image = None
if "workout_image" not in st.session_state:
    st.session_state.workout_image = None
if "current_recipe" not in st.session_state:
    st.session_state.current_recipe = None
if "current_workout" not in st.session_state:
    st.session_state.current_workout = None
if "custom_api_key" not in st.session_state:
    st.session_state.custom_api_key = os.getenv("GEMINI_API_KEY", "")
if "selected_model" not in st.session_state:
    st.session_state.selected_model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)


# -----------------------------------------------------------------------------
# SIDEBAR CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
            <div style="background: linear-gradient(135deg, #10B981 0%, #84CC16 100%); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: 800; color: #0B0F19;">
                VF
            </div>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; color: #F9FAFB;">VisionFit AI</div>
                <div style="font-size: 0.7rem; color: #10B981; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Multimodal Assistant</div>
            </div>
        </div>
        <p style="font-size: 0.8rem; color: #9CA3AF; margin-bottom: 1.2rem; line-height: 1.3;">
            <em>"See What You Have. Discover What You Can Do."</em>
        </p>
    """, unsafe_allow_html=True)

    # Navigation Radio
    nav_options = [
        "Home Dashboard",
        "Recipe Generator",
        "Workout Generator",
        "My Favorites",
        "About VisionFit AI"
    ]
    st.session_state.navigation = st.radio(
        "Navigation Menu",
        nav_options,
        index=nav_options.index(st.session_state.navigation) if st.session_state.navigation in nav_options else 0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.2rem 0;'>", unsafe_allow_html=True)

    # API Configuration Panel
    st.markdown("<h4 style='font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;'>⚡ Gemini AI Engine</h4>", unsafe_allow_html=True)
    
    # Active Service Instance
    gemini_service = GeminiService(
        api_key=st.session_state.custom_api_key,
        model_name=st.session_state.selected_model
    )

    if gemini_service.is_configured:
        st.markdown(f"""
            <div class="vf-info-box" style="padding: 0.6rem 0.8rem; margin: 0.5rem 0;">
                <span style="font-weight: 700; color: #10B981;">● Online</span> | Model: <code>{st.session_state.selected_model}</code><br>
                <small style="color: #9CA3AF;">Key: {gemini_service.masked_key}</small>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="vf-alert-box" style="padding: 0.6rem 0.8rem; margin: 0.5rem 0; color: #FCD34D; border-color: rgba(245, 158, 11, 0.3); background: rgba(245, 158, 11, 0.08);">
                <span style="font-weight: 700; color: #F59E0B;">● Demo Mode</span> (Simulated AI)<br>
                <small style="color: #D1D5DB;">Set your API key below for real vision analysis.</small>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("🔑 Configure API Key", expanded=not gemini_service.is_configured):
        entered_key = st.text_input(
            "Google Gemini API Key",
            value=st.session_state.custom_api_key,
            type="password",
            placeholder="AIzaSy...",
            help="Your secret key is held in memory and never stored or logged."
        )
        if entered_key != st.session_state.custom_api_key:
            st.session_state.custom_api_key = entered_key
            st.rerun()

        model_choice = st.selectbox(
            "Gemini Vision Model",
            ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )
        if model_choice != st.session_state.selected_model:
            st.session_state.selected_model = model_choice
            st.rerun()

        st.markdown("""
            <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 6px;">
                Get a free key from <a href="https://aistudio.google.com/" target="_blank" style="color: #10B981;">Google AI Studio</a>.
            </div>
        """, unsafe_allow_html=True)

    # Saved Counts
    counts = get_favorites_counts()
    st.markdown(f"""
        <div style="background: rgba(17, 24, 39, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.8rem; margin-top: 1rem;">
            <div style="font-size: 0.75rem; color: #9CA3AF; text-transform: uppercase;">Saved to Favorites</div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                <span style="font-size: 0.85rem; color: #F9FAFB;">🥗 Recipes: <strong>{counts['recipe']}</strong></span>
                <span style="font-size: 0.85rem; color: #F9FAFB;">🏋️‍♂️ Workouts: <strong>{counts['workout']}</strong></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; font-size: 0.75rem; color: #6B7280; margin-top: 2rem;">
            VisionFit AI v1.0 • Built with Gemini 2.5
        </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE 1: HOME DASHBOARD
# =============================================================================
if st.session_state.navigation == "Home Dashboard":
    # Hero Section
    st.markdown("""
        <div class="vf-hero-card">
            <div class="vf-badge">Multimodal Generative AI Lifestyle Platform</div>
            <h1 style="font-size: 2.6rem; font-weight: 800; letter-spacing: -0.03em; margin: 0 0 0.8rem 0; line-height: 1.15; color: #FFFFFF;">
                Your World. Your Ingredients.<br>
                <span style="background: linear-gradient(90deg, #10B981, #84CC16); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Your Fitness.
                </span>
            </h1>
            <p style="font-size: 1.05rem; color: #9CA3AF; max-width: 680px; margin-bottom: 1.5rem; line-height: 1.5;">
                Harness state-of-the-art vision models to transform everyday photos of kitchen counters, 
                refrigerators, and home gyms into delicious, macro-conscious recipes and progressive workout routines.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Two Main Mode Selection Cards
    col_rec, col_wrk = st.columns(2, gap="medium")

    with col_rec:
        st.markdown("""
            <div class="vf-mode-card">
                <div>
                    <div class="vf-mode-icon">🥗</div>
                    <div class="vf-badge vf-badge-neutral">Kitchen Vision AI</div>
                    <h3 style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF; margin: 0.4rem 0;">AI Recipe Generator</h3>
                    <p style="color: #9CA3AF; font-size: 0.92rem; line-height: 1.5; margin-bottom: 1.2rem;">
                        Snap a photo of your groceries, vegetables, or pantry shelves. Gemini identifies 
                        what you have, notes uncertain items, and crafts delicious chef-inspired recipes with approximate macro estimates.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Recipe Generator →", key="btn_home_recipe", use_container_width=True):
            st.session_state.navigation = "Recipe Generator"
            st.rerun()

    with col_wrk:
        st.markdown("""
            <div class="vf-mode-card">
                <div>
                    <div class="vf-mode-icon workout">🏋️‍♂️</div>
                    <div class="vf-badge vf-badge-lime">Biomechanics Vision AI</div>
                    <h3 style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF; margin: 0.4rem 0;">AI Workout Generator</h3>
                    <p style="color: #9CA3AF; font-size: 0.92rem; line-height: 1.5; margin-bottom: 1.2rem;">
                        Upload a photo of your dumbbells, resistance bands, pull-up bar, or open mat. 
                        Receive a customized routine with targeted muscle groups, exercise scaling, warm-up, and safety cues.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Workout Generator →", key="btn_home_workout", use_container_width=True):
            st.session_state.navigation = "Workout Generator"
            st.rerun()

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # 3-Step Process
    st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem;'>How VisionFit AI Works</h3>", unsafe_allow_html=True)
    step1, step2, step3 = st.columns(3, gap="medium")

    with step1:
        st.markdown("""
            <div class="vf-step-card">
                <div class="vf-step-num">01</div>
                <h4 style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin: 0 0 0.4rem 0;">Snap & Upload</h4>
                <p style="font-size: 0.85rem; color: #9CA3AF; margin: 0;">
                    Take a quick picture of your kitchen counter, fridge shelves, or available gym equipment.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with step2:
        st.markdown("""
            <div class="vf-step-card">
                <div class="vf-step-num">02</div>
                <h4 style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin: 0 0 0.4rem 0;">Set Preferences</h4>
                <p style="font-size: 0.85rem; color: #9CA3AF; margin: 0;">
                    Specify dietary goals, cooking time, fitness experience, target muscle groups, or physical limitations.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with step3:
        st.markdown("""
            <div class="vf-step-card">
                <div class="vf-step-num">03</div>
                <h4 style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin: 0 0 0.4rem 0;">Multimodal AI</h4>
                <p style="font-size: 0.85rem; color: #9CA3AF; margin: 0;">
                    Gemini 2.5 analyzes visible objects and synthesizes step-by-step instructions with verified safety guardrails.
                </p>
            </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE 2: RECIPE GENERATOR MODE
# =============================================================================
elif st.session_state.navigation == "Recipe Generator":
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem;">
            <div>
                <div class="vf-badge">Mode 1 • Culinary Vision</div>
                <h2 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0.2rem 0;">AI Recipe Generator</h2>
                <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">Upload an ingredient photo to generate customized, macro-friendly recipes.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_input_left, col_input_right = st.columns([1, 1.2], gap="large")

    with col_input_left:
        st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #F9FAFB;'>1. Ingredients Photo</h4>", unsafe_allow_html=True)
        
        # Image Upload or Sample Loader
        uploaded_file = st.file_uploader(
            "Upload Ingredients Image (JPG, PNG, WEBP, up to 10MB)",
            type=["jpg", "jpeg", "png", "webp"],
            key="recipe_file_uploader",
            help="Photograph your refrigerator, kitchen counter, or pantry items."
        )

        col_sample_btn, col_clear_btn = st.columns([1.5, 1])
        with col_sample_btn:
            if st.button("💡 Load Sample Kitchen Image", use_container_width=True):
                st.session_state.recipe_image = generate_sample_ingredients_image()
                st.toast("Loaded sample kitchen ingredients (Veggies, Eggs, Olive Oil, Garlic)!", icon="🥗")
        with col_clear_btn:
            if st.button("Remove Image", use_container_width=True):
                st.session_state.recipe_image = None
                st.rerun()

        # Handle uploaded file
        if uploaded_file is not None:
            is_valid, err_msg, pil_img = validate_uploaded_image(uploaded_file)
            if not is_valid:
                st.error(err_msg)
            else:
                st.session_state.recipe_image = preprocess_image(pil_img)

        # Image Preview Card
        if st.session_state.recipe_image is not None:
            img = st.session_state.recipe_image
            st.image(img, caption=f"Selected Image ({img.size[0]}×{img.size[1]}px)", use_container_width=True)
        else:
            st.info("Please upload a photo of your available food ingredients or click 'Load Sample Kitchen Image' to test immediately.")

    with col_input_right:
        st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #F9FAFB;'>2. Culinary Preferences & Constraints</h4>", unsafe_allow_html=True)
        
        pref_r1_c1, pref_r1_c2 = st.columns(2)
        with pref_r1_c1:
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack", "Post-Workout", "Any"],
                index=2
            )
        with pref_r1_c2:
            dietary_pref = st.selectbox(
                "Dietary Preference",
                ["No Preference", "Vegetarian", "Vegan", "Eggetarian"],
                index=1
            )

        pref_r2_c1, pref_r2_c2 = st.columns(2)
        with pref_r2_c1:
            cuisine = st.selectbox(
                "Cuisine Preference",
                ["Any", "Indian", "Italian", "Asian", "Mediterranean", "Mexican"],
                index=4
            )
        with pref_r2_c2:
            cooking_time = st.select_slider(
                "Max Cooking Time (Minutes)",
                options=[10, 15, 20, 30, 45, 60],
                value=30
            )

        pref_r3_c1, pref_r3_c2 = st.columns(2)
        with pref_r3_c1:
            servings = st.number_input("Servings", min_value=1, max_value=8, value=2, step=1)
        with pref_r3_c2:
            goal = st.selectbox(
                "Nutritional Goal",
                ["Balanced Meal", "High Protein", "General Healthy Eating", "Low Carb"],
                index=0
            )

        include_ing = st.text_input(
            "Optional: Must-Include Ingredients",
            placeholder="e.g. Garlic, olive oil, chili flakes",
            help="Add any pantry staples you definitely want to incorporate."
        )

        exclude_ing = st.text_input(
            "Optional: Ingredients to Exclude / Disliked",
            placeholder="e.g. Mushrooms, cilantro, dairy",
        )

        allergies = st.text_input(
            "⚠️ Known Allergies / Intolerances",
            placeholder="e.g. Peanuts, Gluten, Lactose, Shellfish",
            help="Crucial safety rule: The AI will strictly omit all matching allergens."
        )

        language = st.selectbox(
            "Output Language",
            ["English", "Hindi"],
            index=0
        )

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        
        generate_clicked = st.button(
            "✨ Generate Recipe with Vision AI",
            use_container_width=True,
            type="primary"
        )

    # Process Generation
    if generate_clicked:
        if st.session_state.recipe_image is None:
            st.error("Please provide an image of your ingredients before generating.")
        else:
            with st.spinner("Analyzing visible ingredients and crafting your tailored recipe..."):
                recipe_params = {
                    "meal_type": meal_type,
                    "dietary_pref": dietary_pref,
                    "cuisine": cuisine,
                    "cooking_time": cooking_time,
                    "servings": servings,
                    "include_ingredients": sanitize_text_input(include_ing),
                    "exclude_ingredients": sanitize_text_input(exclude_ing),
                    "allergies": sanitize_text_input(allergies),
                    "goal": goal,
                    "language": language
                }
                
                success, result_data, notice = generate_recipe(
                    st.session_state.recipe_image,
                    recipe_params,
                    gemini_service
                )

                if success:
                    st.session_state.current_recipe = result_data
                    if result_data.get("is_demo"):
                        st.warning(notice)
                    else:
                        st.success(notice)
                else:
                    st.error(f"Generation Failed: {notice}")

    # Display Recipe Result
    if st.session_state.current_recipe:
        recipe = st.session_state.current_recipe
        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 2rem 0;'>", unsafe_allow_html=True)

        # Overview Card Header
        st.markdown(f"""
            <div class="vf-result-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div class="vf-badge vf-badge-lime">{recipe.get('cuisine', 'Cuisine')} • {recipe.get('difficulty', 'Medium')}</div>
                        <h2 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0.3rem 0;">{recipe.get('title', 'Chef Recipe')}</h2>
                        <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0 0 1rem 0;">{recipe.get('description', '')}</p>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; margin-top: 0.5rem;">
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{recipe.get('prep_time_minutes', 15)}m</div>
                        <div class="vf-metric-lbl">Prep Time</div>
                    </div>
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{recipe.get('cook_time_minutes', 20)}m</div>
                        <div class="vf-metric-lbl">Cook Time</div>
                    </div>
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{recipe.get('total_time_minutes', 35)}m</div>
                        <div class="vf-metric-lbl">Total Time</div>
                    </div>
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{recipe.get('servings', 2)}</div>
                        <div class="vf-metric-lbl">Servings</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Visual Detection Analysis
        vis_col1, vis_col2 = st.columns(2)
        with vis_col1:
            st.markdown("<h4 style='font-size: 1rem; font-weight: 700; color: #10B981;'>🔍 Confirmed Visible Ingredients</h4>", unsafe_allow_html=True)
            vis_items = recipe.get("visually_identified_ingredients", [])
            if vis_items:
                pills = "".join([f"<span class='vf-pill'>{item}</span>" for item in vis_items])
                st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
            else:
                st.write("No distinct items identified with high confidence.")

        with vis_col2:
            st.markdown("<h4 style='font-size: 1rem; font-weight: 700; color: #F59E0B;'>⚠️ Uncertain / Unclear Items</h4>", unsafe_allow_html=True)
            uncert = recipe.get("uncertain_items", [])
            if uncert:
                pills = "".join([f"<span class='vf-pill' style='border-color: rgba(245,158,11,0.4); color: #FCD34D;'>{u}</span>" for u in uncert])
                st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<small style='color: #9CA3AF;'>No ambiguous items flagged.</small>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # Approximate Nutrition Box
        st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <div style="font-weight: 700; color: #10B981; font-size: 1rem;">📊 Approximate Nutrition Estimates (Per Serving)</div>
                    <small style="color: #9CA3AF;">*Calculated approximation; not certified laboratory data.</small>
                </div>
        """, unsafe_allow_html=True)
        
        nutr = recipe.get("nutrition_estimates", {})
        n1, n2, n3, n4, n5 = st.columns(5)
        n1.metric("Calories", f"~{nutr.get('calories', 'N/A')} kcal")
        n2.metric("Protein", f"~{nutr.get('protein_g', 'N/A')} g")
        n3.metric("Carbs", f"~{nutr.get('carbs_g', 'N/A')} g")
        n4.metric("Fats", f"~{nutr.get('fats_g', 'N/A')} g")
        n5.metric("Fiber", f"~{nutr.get('fiber_g', 'N/A')} g")
        st.markdown("</div>", unsafe_allow_html=True)

        # Ingredients & Steps Columns
        ing_col, steps_col = st.columns([1, 1.4], gap="medium")

        with ing_col:
            st.markdown("<h3 style='font-size: 1.2rem; font-weight: 700; color: #FFFFFF;'>🛒 Ingredients</h3>", unsafe_allow_html=True)
            for item in recipe.get("ingredients", []):
                name = item.get("name", "Ingredient")
                qty = item.get("quantity", "")
                unit = item.get("unit", "")
                is_opt = item.get("is_optional", False)
                need_buy = item.get("need_to_buy", False)
                
                badges = ""
                if is_opt:
                    badges += " <span style='font-size: 0.7rem; color: #9CA3AF;'>(optional)</span>"
                if need_buy:
                    badges += " <span style='font-size: 0.7rem; color: #F59E0B;'>[pantry / buy]</span>"

                st.markdown(f"- **{qty} {unit}** {name}{badges}", unsafe_allow_html=True)

            # Chef substitutions & storage
            subs = recipe.get("substitutions", [])
            if subs:
                st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
                st.markdown("<h4 style='font-size: 0.95rem; font-weight: 700; color: #10B981;'>💡 Chef's Substitutions</h4>", unsafe_allow_html=True)
                for s in subs:
                    st.markdown(f"<small style='color: #D1D5DB;'>• {s}</small><br>", unsafe_allow_html=True)

            storage = recipe.get("storage_tips", "")
            if storage:
                st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.8rem; margin-top: 1rem;">
                        <small style="color: #9CA3AF; font-weight: 600;">STORAGE & FRESHNESS:</small><br>
                        <small style="color: #D1D5DB;">{storage}</small>
                    </div>
                """, unsafe_allow_html=True)

        with steps_col:
            st.markdown("<h3 style='font-size: 1.2rem; font-weight: 700; color: #FFFFFF;'>👩‍🍳 Step-by-Step Instructions</h3>", unsafe_allow_html=True)
            for s in recipe.get("steps", []):
                s_num = s.get("step_number", "")
                inst = s.get("instruction", "")
                t_temp = s.get("time_or_temp", "")
                
                time_badge = f"<span class='vf-badge vf-badge-neutral' style='margin: 0;'>{t_temp}</span>" if t_temp else ""
                
                st.markdown(f"""
                    <div style="display: flex; gap: 12px; margin-bottom: 1rem; align-items: flex-start;">
                        <div style="background: rgba(16, 185, 129, 0.15); color: #10B981; font-weight: 700; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.85rem;">
                            {s_num}
                        </div>
                        <div style="flex-grow: 1;">
                            <div style="color: #F3F4F6; font-size: 0.95rem; line-height: 1.45;">{inst}</div>
                            {time_badge}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Action Bar (Save, Copy, Download)
        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        act_col1, act_col2, act_col3 = st.columns(3)

        with act_col1:
            if st.button("⭐ Save to Favorites", key="btn_save_recipe", use_container_width=True):
                new_id = save_favorite(
                    item_type="recipe",
                    title=recipe.get("title", "Recipe"),
                    summary=recipe.get("description", "")[:120],
                    data=recipe
                )
                st.toast(f"Saved '{recipe.get('title')}' to Favorites!", icon="⭐")

        recipe_md = format_recipe_markdown(recipe)

        with act_col2:
            st.download_button(
                label="⬇️ Download Markdown",
                data=recipe_md,
                file_name=f"recipe_{recipe.get('title', 'custom').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with act_col3:
            with st.popover("📋 View Copyable Text", use_container_width=True):
                st.text_area("Copyable Recipe Markdown", value=recipe_md, height=280)


# =============================================================================
# PAGE 3: WORKOUT GENERATOR MODE
# =============================================================================
elif st.session_state.navigation == "Workout Generator":
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem;">
            <div>
                <div class="vf-badge vf-badge-lime">Mode 2 • Biomechanics Vision</div>
                <h2 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0.2rem 0;">AI Workout Generator</h2>
                <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">Upload a photo of your gym equipment or home space to generate structured training.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_wrk_left, col_wrk_right = st.columns([1, 1.2], gap="large")

    with col_wrk_left:
        st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #F9FAFB;'>1. Equipment / Space Photo</h4>", unsafe_allow_html=True)
        
        uploaded_wrk_file = st.file_uploader(
            "Upload Gym Equipment Image (JPG, PNG, WEBP, up to 10MB)",
            type=["jpg", "jpeg", "png", "webp"],
            key="workout_file_uploader",
            help="Photograph dumbbells, kettlebells, bands, benches, or your floor workout area."
        )

        col_sample_gym, col_clear_gym = st.columns([1.5, 1])
        with col_sample_gym:
            if st.button("💡 Load Sample Gym Image", use_container_width=True):
                st.session_state.workout_image = generate_sample_gym_image()
                st.toast("Loaded sample home gym equipment (Dumbbells, Kettlebell, Bands, Mat)!", icon="🏋️‍♂️")
        with col_clear_gym:
            if st.button("Remove Equipment Image", use_container_width=True):
                st.session_state.workout_image = None
                st.rerun()

        if uploaded_wrk_file is not None:
            is_valid, err_msg, pil_img = validate_uploaded_image(uploaded_wrk_file)
            if not is_valid:
                st.error(err_msg)
            else:
                st.session_state.workout_image = preprocess_image(pil_img)

        # Image Preview Card
        if st.session_state.workout_image is not None:
            w_img = st.session_state.workout_image
            st.image(w_img, caption=f"Selected Equipment Image ({w_img.size[0]}×{w_img.size[1]}px)", use_container_width=True)
        else:
            st.info("Please upload a photo of your available workout equipment or click 'Load Sample Gym Image' to test immediately.")

    with col_wrk_right:
        st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #F9FAFB;'>2. Training Goals & Preferences</h4>", unsafe_allow_html=True)

        w_r1_c1, w_r1_c2 = st.columns(2)
        with w_r1_c1:
            w_goal = st.selectbox(
                "Primary Fitness Goal",
                ["Strength", "General Fitness", "Endurance", "Mobility", "Weight Management"],
                index=0
            )
        with w_r1_c2:
            w_experience = st.selectbox(
                "Experience Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=1
            )

        w_r2_c1, w_r2_c2 = st.columns(2)
        with w_r2_c1:
            w_time = st.select_slider(
                "Available Time (Minutes)",
                options=[10, 20, 30, 45, 60],
                value=30
            )
        with w_r2_c2:
            w_location = st.selectbox(
                "Training Location",
                ["Home", "Gym", "Outdoor"],
                index=0
            )

        w_r3_c1, w_r3_c2 = st.columns(2)
        with w_r3_c1:
            w_eq_pref = st.selectbox(
                "Equipment Preference",
                ["Use Visible Equipment", "Bodyweight Only"],
                index=0
            )
        with w_r3_c2:
            w_focus = st.selectbox(
                "Workout Focus Area",
                ["Full Body", "Upper Body", "Lower Body", "Core", "Cardio"],
                index=0
            )

        w_limitations = st.text_input(
            "⚠️ Injuries, Joint Limitations, or Exercises to Avoid",
            placeholder="e.g. Mild lower back sensitivity, avoid overhead presses",
            help="AI will automatically substitute high-impact movements with joint-friendly variations."
        )

        w_language = st.selectbox(
            "Output Language",
            ["English", "Hindi"],
            index=0,
            key="w_lang"
        )

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        generate_wrk_clicked = st.button(
            "⚡ Generate Workout with Vision AI",
            use_container_width=True,
            type="primary"
        )

    # Process Workout Generation
    if generate_wrk_clicked:
        if st.session_state.workout_image is None:
            st.error("Please provide an image of your workout space or equipment before generating.")
        else:
            with st.spinner("Analyzing equipment and constructing progressive training routine..."):
                workout_params = {
                    "goal": w_goal,
                    "experience_level": w_experience,
                    "available_time": w_time,
                    "location": w_location,
                    "equipment_pref": w_eq_pref,
                    "focus": w_focus,
                    "limitations": sanitize_text_input(w_limitations),
                    "language": w_language
                }

                success, result_data, notice = generate_workout(
                    st.session_state.workout_image,
                    workout_params,
                    gemini_service
                )

                if success:
                    st.session_state.current_workout = result_data
                    if result_data.get("is_demo"):
                        st.warning(notice)
                    else:
                        st.success(notice)
                else:
                    st.error(f"Workout Generation Failed: {notice}")

    # Display Workout Result
    if st.session_state.current_workout:
        workout = st.session_state.current_workout
        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 2rem 0;'>", unsafe_allow_html=True)

        # Overview Card Header
        st.markdown(f"""
            <div class="vf-result-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div class="vf-badge vf-badge-lime">{workout.get('goal', 'Fitness')} • {workout.get('experience_level', 'All Levels')}</div>
                        <h2 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0.3rem 0;">{workout.get('title', 'Custom Training')}</h2>
                        <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0 0 1rem 0;">{workout.get('description', '')}</p>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 0.5rem;">
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{workout.get('estimated_duration_minutes', 30)}m</div>
                        <div class="vf-metric-lbl">Target Duration</div>
                    </div>
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{workout.get('workout_focus', 'Full Body')}</div>
                        <div class="vf-metric-lbl">Focus Area</div>
                    </div>
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{len(workout.get('main_exercises', []))}</div>
                        <div class="vf-metric-lbl">Exercises</div>
                    </div>
                    <div class="vf-metric-box">
                        <div class="vf-metric-val">{workout.get('location', 'Home')}</div>
                        <div class="vf-metric-lbl">Location</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Equipment Analysis
        eq_col1, eq_col2 = st.columns(2)
        with eq_col1:
            st.markdown("<h4 style='font-size: 1rem; font-weight: 700; color: #10B981;'>🔍 Recognized Equipment</h4>", unsafe_allow_html=True)
            vis_eq = workout.get("visually_identified_equipment", [])
            if vis_eq:
                pills = "".join([f"<span class='vf-pill'>{e}</span>" for e in vis_eq])
                st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='vf-pill'>Bodyweight / Open Floor</span>", unsafe_allow_html=True)

        with eq_col2:
            st.markdown("<h4 style='font-size: 1rem; font-weight: 700; color: #F59E0B;'>⚠️ Uncertain / Incomplete Equipment</h4>", unsafe_allow_html=True)
            uncert_eq = workout.get("uncertain_equipment", [])
            if uncert_eq:
                pills = "".join([f"<span class='vf-pill' style='border-color: rgba(245,158,11,0.4); color: #FCD34D;'>{u}</span>" for u in uncert_eq])
                st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<small style='color: #9CA3AF;'>All items identified with high confidence.</small>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Warm-up Section
        st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; color: #F9FAFB;'>🔥 Warm-Up (Mobility & Muscle Activation)</h3>", unsafe_allow_html=True)
        warmups = workout.get("warmup", [])
        w_cols = st.columns(len(warmups) if warmups else 1)
        for idx, w in enumerate(warmups):
            with w_cols[idx]:
                name = w.get("name", "Warmup")
                dur = w.get("duration", "45s")
                cue = w.get("instructions", "")
                st.markdown(f"""
                    <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 1rem; height: 100%;">
                        <div class="vf-badge vf-badge-neutral" style="margin-bottom: 0.4rem;">{dur}</div>
                        <div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem; margin-bottom: 0.3rem;">{name}</div>
                        <small style="color: #9CA3AF; line-height: 1.4; display: block;">{cue}</small>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Main Workout Section
        st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; color: #F9FAFB;'>⚡ Main Workout Circuit</h3>", unsafe_allow_html=True)
        for i, ex in enumerate(workout.get("main_exercises", []), 1):
            name = ex.get("name", f"Exercise {i}")
            sets = ex.get("sets", "3")
            reps = ex.get("reps_or_duration", "10 reps")
            rest = ex.get("rest_seconds", "60s")
            muscles = ex.get("target_muscles", "")
            technique = ex.get("technique_cues", "")
            mistake = ex.get("common_mistake", "")
            alt = ex.get("easier_alternative", "")

            st.markdown(f"""
                <div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-weight: 800; color: #10B981; font-size: 1.1rem; margin-right: 6px;">#{i}</span>
                            <span style="font-weight: 700; color: #FFFFFF; font-size: 1.15rem;">{name}</span>
                            <span style="margin-left: 8px; font-size: 0.8rem; color: #9CA3AF;">🎯 {muscles}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <span class="vf-badge vf-badge-lime" style="margin: 0;">{sets} Sets</span>
                            <span class="vf-badge" style="margin: 0;">{reps}</span>
                            <span class="vf-badge vf-badge-neutral" style="margin: 0;">Rest: {rest}</span>
                        </div>
                    </div>
                    <div style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem;">
                        <div style="color: #E5E7EB; margin-bottom: 4px;"><strong>Proper Form:</strong> {technique}</div>
                        {f"<div style='color: #F87171; margin-bottom: 4px;'><strong>Common Mistake:</strong> {mistake}</div>" if mistake else ""}
                        {f"<div style='color: #38BDF8;'><strong>Easier Scaling Option:</strong> {alt}</div>" if alt else ""}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Cool-down Section
        st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; color: #F9FAFB;'>🧘 Cool-Down & Decompression</h3>", unsafe_allow_html=True)
        cd_items = workout.get("cooldown", [])
        for c in cd_items:
            name = c.get("name", "Stretch")
            dur = c.get("duration", "30s")
            cue = c.get("instructions", "")
            st.markdown(f"- **{name}** ({dur}) — <span style='color: #9CA3AF;'>{cue}</span>", unsafe_allow_html=True)

        # Safety Box
        st.markdown("""
            <div class="vf-alert-box" style="margin-top: 1.5rem;">
                <strong>🛡️ Safety & Medical Advisory:</strong> Inspect all equipment for structural integrity and secure grips before lifting. 
                Stop immediately if you experience sharp or stabbing joint discomfort, lightheadedness, or shortness of breath. 
                Consult a physician before undertaking vigorous exercise programs if you have pre-existing medical conditions.
            </div>
        """, unsafe_allow_html=True)

        # Action Bar
        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        w_act1, w_act2, w_act3 = st.columns(3)

        with w_act1:
            if st.button("⭐ Save Workout to Favorites", key="btn_save_workout", use_container_width=True):
                new_w_id = save_favorite(
                    item_type="workout",
                    title=workout.get("title", "Workout"),
                    summary=workout.get("description", "")[:120],
                    data=workout
                )
                st.toast(f"Saved '{workout.get('title')}' to Favorites!", icon="⭐")

        workout_md = format_workout_markdown(workout)

        with w_act2:
            st.download_button(
                label="⬇️ Download Workout Markdown",
                data=workout_md,
                file_name=f"workout_{workout.get('title', 'routine').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with w_act3:
            with st.popover("📋 View Copyable Routine", use_container_width=True):
                st.text_area("Copyable Workout Markdown", value=workout_md, height=280)


# =============================================================================
# PAGE 4: MY FAVORITES
# =============================================================================
elif st.session_state.navigation == "My Favorites":
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem;">
            <div>
                <div class="vf-badge">Saved Library</div>
                <h2 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin: 0.2rem 0;">My Favorites</h2>
                <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">Access your saved recipes and custom workouts anytime.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    filter_choice = st.radio(
        "Filter Items",
        ["All Items", "🥗 Recipes Only", "🏋️‍♂️ Workouts Only"],
        horizontal=True
    )

    type_filter = None
    if "Recipes" in filter_choice:
        type_filter = "recipe"
    elif "Workouts" in filter_choice:
        type_filter = "workout"

    favs = get_favorites(type_filter)

    if not favs:
        st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; background: var(--bg-card); border: 1px dashed rgba(255,255,255,0.1); border-radius: 14px; margin-top: 1rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⭐</div>
                <h3 style="color: #FFFFFF; font-weight: 700;">No Favorites Saved Yet</h3>
                <p style="color: #9CA3AF; max-width: 420px; margin: 0 auto 1.5rem auto;">
                    Generate a recipe or workout using the Vision AI generator, then click "Save to Favorites" to build your personal lifestyle collection.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<small style='color: #9CA3AF;'>Showing <strong>{len(favs)}</strong> saved item(s)</small>", unsafe_allow_html=True)
        
        for item in favs:
            item_id = item["id"]
            itype = item["item_type"]
            title = item["title"]
            summary = item["summary"]
            created = item["created_at"]
            data = item["data"]

            badge_html = "<span class='vf-badge' style='margin: 0;'>🥗 Recipe</span>" if itype == "recipe" else "<span class='vf-badge vf-badge-lime' style='margin: 0;'>🏋️‍♂️ Workout</span>"

            with st.container():
                st.markdown(f"""
                    <div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                            <div>
                                {badge_html}
                                <h3 style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin: 0.4rem 0 0.2rem 0;">{title}</h3>
                                <p style="color: #9CA3AF; font-size: 0.88rem; margin: 0;">{summary}</p>
                                <small style="color: #6B7280; margin-top: 4px; display: block;">Saved on {created}</small>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_view, col_dl, col_del = st.columns([2, 1, 1])
                with col_view:
                    with st.expander(f"👁️ View Complete {itype.capitalize()} Details"):
                        if itype == "recipe":
                            st.markdown(format_recipe_markdown(data))
                        else:
                            st.markdown(format_workout_markdown(data))

                with col_dl:
                    md_text = format_recipe_markdown(data) if itype == "recipe" else format_workout_markdown(data)
                    st.download_button(
                        label="⬇️ Export File",
                        data=md_text,
                        file_name=f"{itype}_{title.lower().replace(' ', '_')}.md",
                        mime="text/markdown",
                        key=f"dl_fav_{item_id}",
                        use_container_width=True
                    )

                with col_del:
                    if st.button("🗑️ Delete", key=f"del_fav_{item_id}", use_container_width=True):
                        delete_favorite(item_id)
                        st.toast(f"Removed '{title}' from favorites.", icon="🗑️")
                        st.rerun()

        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 2rem 0;'>", unsafe_allow_html=True)
        if st.button("⚠️ Clear All Saved Favorites", type="secondary"):
            count_del = clear_all_favorites()
            st.toast(f"Cleared {count_del} favorites.", icon="🧹")
            st.rerun()


# =============================================================================
# PAGE 5: ABOUT VISIONFIT AI
# =============================================================================
elif st.session_state.navigation == "About VisionFit AI":
    st.markdown("""
        <div class="vf-hero-card">
            <div class="vf-badge">About VisionFit AI</div>
            <h2 style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0.2rem 0;">
                See What You Have. Discover What You Can Do.
            </h2>
            <p style="color: #9CA3AF; font-size: 1rem; line-height: 1.5; margin-top: 0.6rem;">
                VisionFit AI was created to eliminate decision fatigue in the kitchen and the home gym. 
                Rather than asking users to type out long lists of groceries or equipment models, 
                our multimodal AI analyzes visual scenes directly.
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
            <h3 style="color: #10B981; font-weight: 700; font-size: 1.3rem;">🧠 Multimodal Architecture</h3>
            <p style="color: #D1D5DB; font-size: 0.92rem; line-height: 1.6;">
                VisionFit AI utilizes the official <code>google-genai</code> Python SDK to interface with 
                Google's multimodal <strong>Gemini 2.5 Flash</strong> and <strong>Gemini 1.5 Flash</strong> engines.
            </p>
            <ul style="color: #9CA3AF; font-size: 0.9rem; line-height: 1.6;">
                <li><strong>Safe Image Preprocessing:</strong> Files are validated for MIME type, integrity checked using Pillow, and downscaled to avoid excessive token overhead.</li>
                <li><strong>Uncertainty Awareness:</strong> Visual elements that are partially obscured, out of focus, or ambiguous are flagged explicitly rather than hallucinated.</li>
                <li><strong>Contractual Prompts:</strong> Responses are governed by structured JSON schemas to ensure deterministic rendering in modern UI cards.</li>
            </ul>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <h3 style="color: #84CC16; font-weight: 700; font-size: 1.3rem;">🛡️ Safety & Health Guardrails</h3>
            <p style="color: #D1D5DB; font-size: 0.92rem; line-height: 1.6;">
                Health, nutrition, and exercise safety must always come first:
            </p>
            <ul style="color: #9CA3AF; font-size: 0.9rem; line-height: 1.6;">
                <li><strong>Nutritional Estimates:</strong> Caloric and macronutrient values are approximate guidelines derived from standard nutritional tables.</li>
                <li><strong>Allergy Vigilance:</strong> Never rely exclusively on AI for critical allergen verification; always read manufacturer packaging.</li>
                <li><strong>Equipment Stability:</strong> An AI cannot detect micro-fractures, loose bolts, or improper anchoring from a photograph. Inspect all gear before lifting.</li>
                <li><strong>Medical Clearance:</strong> Consult a physician before beginning any strenuous physical exercise program.</li>
            </ul>
        """, unsafe_allow_html=True)

