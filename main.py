"""Fitness AI Coach - Main Application.

A Streamlit-based fitness coaching application that uses computer vision
to detect exercises, count repetitions, calculate BMR, and generate diet plans.

Features:
- BMR (Basal Metabolic Rate) Calculator
- Video Mode: Upload and analyze exercise videos
- WebCam Mode: Real-time exercise detection and rep counting
- Diet Plan Generator: Personalized nutrition plans using Gemini AI

Version: 2.0 (Deployment-Optimized)
Updated: 2026-07-06 - Fixed video/webcam UI for cloud deployment
"""

import streamlit as st
import tempfile
import os
import time
import logging
import warnings
from pathlib import Path
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import mediapipe as mp
except ImportError:
    mp = None

try:
    import ExerciseAiTrainer as exercise
    from ExerciseAiTrainer import Exercise
    from AiTrainer_utils import distanceCalculate
except Exception:
    exercise = None
    Exercise = None
    distanceCalculate = None

try:
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
except Exception:
    webrtc_streamer = None
    VideoTransformerBase = None

# Suppress unnecessary warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from google import genai as google_genai
except ImportError:
    google_genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CAMERA_AVAILABLE = cv2 is not None and mp is not None


def get_camera_backend():
    """Return the preferred camera backend for deployment."""
    if webrtc_streamer is not None:
        return "webrtc"
    if CAMERA_AVAILABLE:
        return "opencv"
    return "unavailable"

# Project root helpers
PROJECT_ROOT = Path(__file__).resolve().parent
HISTORY_FILE = PROJECT_ROOT / 'workout_history.json'


def resolve_project_path(*relative_parts):
    """Resolve a path relative to the project root."""
    return PROJECT_ROOT.joinpath(*relative_parts)


# Constants
DEMO_VIDEO_PATH = resolve_project_path('demo.mp4')
FORM_VIDEO_PATHS = {
    'Bicep Curl': resolve_project_path('curl_form.mp4'),
    'Push-Up': resolve_project_path('push_up_form.mp4'),
    'Squat': resolve_project_path('squat_form.mp4'),
    'Shoulder Press': resolve_project_path('shoulder_press_form.mp4')
}

# Color scheme
PRIMARY_COLOR = "#FF6B35"
SECONDARY_COLOR = "#004E89"
SUCCESS_COLOR = "#1ECB7F"
WARNING_COLOR = "#FFB703"
DANGER_COLOR = "#E63946"


def calculate_bmr(gender, age, weight, height):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
    
    Formulas:
    - Men: BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (years) + 5
    - Women: BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (years) - 161
    """
    g_str = str(gender).lower()
    if 'female' in g_str or 'woman' in g_str or '👩' in g_str:
        return 10 * weight + 6.25 * height - 5 * age - 161
    else:
        return 10 * weight + 6.25 * height - 5 * age + 5


# Local diet generator removed - Application now exclusively uses Gemini AI models for 100% personalized diet generation.



def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Fitness AI Coach", layout="wide", initial_sidebar_state="expanded")
    
    # Premium Custom styling
    # Premium Custom styling
    st.markdown("""
    <style>
        /* Import Google Fonts & Material Symbols */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        /* Global body and font styles */
        html, body, .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp button, .stApp input, .stApp select, .stApp textarea {
            font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        }

        /* Preserve Streamlit icon fonts */
        [class*="material-symbols"],
        [class*="material-icons"],
        [data-testid="stIcon"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stHeader"] *,
        [data-testid="stExpander"] *,
        span[data-testid="stExpanderToggleIcon"],
        i, .material-icons, .material-symbols-outlined {
            font-family: 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
        }

        .main {
            padding: 1.5rem 2.5rem;
            background-color: transparent;
        }

        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #eef2f6 50%, #e2e8f0 100%);
        }
        
        /* Premium Glassmorphic Cards & Containers */
        div[data-testid="stMetric"], .metric-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(226, 232, 240, 0.8);
            color: #0f172a;
            padding: 22px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div[data-testid="stMetric"]:hover, .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 30px -10px rgba(79, 70, 229, 0.12);
            border-color: rgba(99, 102, 241, 0.4);
        }

        /* Inputs & Selectboxes */
        div[data-baseweb="select"] > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {
            border-radius: 10px !important;
            border: 1px solid #cbd5e1 !important;
            background: #ffffff !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
            transition: all 0.2s ease !important;
        }
        div[data-baseweb="select"] > div:focus-within, .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
        }

        /* Premium Primary & Secondary Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.3px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(79, 70, 229, 0.5);
            background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
            color: white;
        }
        
        /* Headers & Dividers */
        h2 {
            color: #1e1b4b;
            font-weight: 700;
            font-size: 26px;
            padding-bottom: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        }
        h3 {
            color: #312e81;
            font-weight: 700;
            font-size: 20px;
        }
        
        /* Expanders & Sidebar */
        div[data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid rgba(203, 213, 225, 0.8);
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }
        div[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: 4px 0 25px rgba(0,0,0,0.04);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero App Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%); 
                padding: 32px 24px; border-radius: 20px; text-align: center; color: white; 
                margin-bottom: 28px; box-shadow: 0 15px 35px rgba(15, 23, 42, 0.22); 
                border: 1px solid rgba(255, 255, 255, 0.1);">
        <h1 style="color: #ffffff; margin: 0 0 8px 0; font-size: 38px; font-weight: 800; letter-spacing: -0.5px;">
            🏋️ Fitness AI Coach
        </h1>
        <p style="margin: 0; color: #cbd5e1; font-size: 15px; max-width: 620px; margin: 0 auto; line-height: 1.6; font-weight: 500;">
            Real-Time Pose Tracking • Automatic Rep Counter • 100% AI Nutrition & Workout Plans
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div style="padding: 10px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 15px;">
        <span style="font-size: 12px; font-weight: 800; letter-spacing: 1px; color: #4338ca; text-transform: uppercase;">⚡ FEATURES MENU</span>
    </div>
    """, unsafe_allow_html=True)

    feature = st.sidebar.selectbox("Choose Feature", 
                                  ["📊 BMR Calculator", "📈 Progress Dashboard", "📹 Video Mode", "🎥 WebCam Mode", "🥗 Diet Plan Generator", "🗓️ Weekly Workout Plan"],
                                  format_func=lambda x: x)

    if "BMR Calculator" in feature:
        bmr_calculator()
    elif "Progress Dashboard" in feature:
        progress_dashboard()
    elif "Video Mode" in feature:
        video_mode()
    elif "WebCam Mode" in feature:
        webcam_mode()
    elif "Diet Plan Generator" in feature:
        diet_plan_generator()
    elif "Weekly Workout Plan" in feature:
        workout_plan_generator()


def get_clean_exercise_name(name):
    """Extract standard exercise key without emojis."""
    for key in ['Bicep Curl', 'Push-Up', 'Squat', 'Shoulder Press']:
        if key in name:
            return key
    return name


def bmr_calculator():
    """BMR calculator feature using Mifflin-St Jeor equation."""
    st.markdown("<h2>📊 BMR (Basal Metabolic Rate) Calculator</h2>", unsafe_allow_html=True)
    st.markdown("Enter your personal details below to compute your exact Basal Metabolic Rate.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Personal Information")
        gender = st.radio("Select Gender", ['👨 Male', '👩 Female'], horizontal=True)
        age = st.number_input("Enter Age (years)", min_value=10, max_value=100, value=25, step=1)
    with col2:
        st.markdown("### Measurements")
        weight = st.number_input("Enter Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
        height = st.number_input("Enter Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔥 Calculate BMR", type="primary", use_container_width=True):
        try:
            bmr = calculate_bmr(gender, age, weight, height)
            is_female = 'female' in str(gender).lower() or '👩' in str(gender)
            
            st.markdown("---")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); 
                        padding: 30px; border-radius: 16px; text-align: center; color: white;
                        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3); margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; letter-spacing: 1px; text-transform: uppercase; opacity: 0.9;">🔥 Your Calculated Basal Metabolic Rate</p>
                <h1 style="margin: 10px 0; font-size: 56px; font-weight: 800; color: #ffffff;">{bmr:,.1f} <span style="font-size: 24px; font-weight: 500;">kcal / day</span></h1>
                <p style="margin: 0; font-size: 14px; opacity: 0.85;">This is the baseline energy your body burns at complete rest.</p>
            </div>
            """, unsafe_allow_html=True)

            w_part = 10 * weight
            h_part = 6.25 * height
            a_part = 5 * age
            formula_name = "Women" if is_female else "Men"
            const_sign = "− 161" if is_female else "+ 5"

            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; 
                        padding: 20px; border-radius: 12px; color: #1e293b;">
                <h3 style="margin-top: 0; color: #312e81;">📐 Applied Formula & Calculation Breakdown</h3>
                <p style="margin-bottom: 12px;"><b>Mifflin-St Jeor Equation for {formula_name}:</b></p>
                <code style="background: #e0e7ff; color: #3730a3; padding: 6px 12px; border-radius: 6px; font-size: 15px; display: inline-block;">
                    BMR = 10 × weight (kg) + 6.25 × height (cm) − 5 × age (years) {const_sign}
                </code>
                <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 16px 0;">
                <p style="margin-bottom: 6px;"><b>Step-by-Step Values:</b></p>
                <ul style="line-height: 1.8; margin-bottom: 0;">
                    <li>Weight Term: <code>10 × {weight} kg = {w_part:,.1f}</code></li>
                    <li>Height Term: <code>6.25 × {height} cm = {h_part:,.1f}</code></li>
                    <li>Age Term: <code>5 × {age} years = {a_part:,.1f}</code></li>
                    <li>Gender Constant: <code>{const_sign}</code></li>
                </ul>
                <p style="margin-top: 14px; font-weight: 700; color: #4f46e5; font-size: 16px;">
                    Result: {w_part:,.1f} + {h_part:,.1f} − {a_part:,.1f} {const_sign} = <u>{bmr:,.1f} kcal/day</u>
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.success("✅ Calculation complete!")
        except Exception as e:
            st.error(f"❌ Error calculating BMR: {str(e)}")
            logger.error(f"BMR calculation error: {e}")


def video_mode():
    """Video upload and analysis feature."""
    st.markdown("<h2>📹 Video Mode - Exercise Analysis</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    Upload your exercise video to analyze your form:
    - 💪 Push-Up
    - 🦵 Squat  
    - 🏋️ Bicep Curl
    - 🏋️‍♂️ Shoulder Press
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Upload Video")
        video_file = st.file_uploader("Upload your exercise video", type=["mp4", "mov", "avi", "m4v"])
    
    with col2:
        st.markdown("### Select Exercise")
        exercise_type = st.selectbox("Choose Exercise", 
                                    ["💪 Push-Up", "🦵 Squat", "🏋️ Bicep Curl", "🏋️‍♂️ Shoulder Press"])
    
    if video_file is not None:
        st.markdown("---")
        st.markdown("### 📥 Video Preview")
        st.video(video_file)
        
        st.markdown("### 📋 Video Info")
        st.markdown(f"**Selected Exercise:** `{exercise_type}`")
        st.markdown(f"**Video File:** `{video_file.name}`")
        st.markdown("**Status:** ✅ Video loaded successfully")
        st.info("💡 Video playback is optimized for browser viewing. Your form can be analyzed by comparing with the correct form guide below.")
        
        clean_exercise = get_clean_exercise_name(exercise_type)
        if clean_exercise in FORM_VIDEO_PATHS:
            form_video = FORM_VIDEO_PATHS[clean_exercise]
            if os.path.exists(form_video):
                with st.expander("📖 View Correct Form"):
                    st.video(str(form_video))
    else:
        st.info("📌 Upload a video to get started")


def webcam_mode():
    """Live webcam exercise detection feature with AI Voice Coach."""
    st.markdown("<h2>🎥 Live WebCam AI Exercise Trainer</h2>", unsafe_allow_html=True)
    st.markdown("Select your exercise below and click **🚀 Start Live Workout** for real-time rep counting & AI audio form feedback.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        selected_exercise = st.selectbox("Choose Exercise", ["💪 Push-Up", "🦵 Squat", "🏋️ Bicep Curl", "🏋️‍♂️ Shoulder Press"])
    with col2:
        target_reps = st.slider("Target Reps", min_value=1, max_value=50, value=10)

    clean_exercise = get_clean_exercise_name(selected_exercise)

    st.markdown("<br>", unsafe_allow_html=True)

    if CAMERA_AVAILABLE and cv2 is not None:
        if st.button(f"🚀 Start Live Workout ({clean_exercise})", type="primary", use_container_width=True):
            cap = cv2.VideoCapture(0)
            trainer = Exercise()
            if clean_exercise == "Push-Up":
                trainer.push_up(cap, mode='webcam', target_reps=target_reps)
            elif clean_exercise == "Squat":
                trainer.squat(cap, mode='webcam', target_reps=target_reps)
            elif clean_exercise == "Bicep Curl":
                trainer.bicep_curl(cap, mode='webcam', target_reps=target_reps)
            elif clean_exercise == "Shoulder Press":
                trainer.shoulder_press(cap, mode='webcam', target_reps=target_reps)

            st.balloons()
            st.success(f"🎉 Target Reached! Outstanding job completing your set of {target_reps} {clean_exercise}s!")
    elif webrtc_streamer is not None:
        st.info("Click 'Start Streaming' below to begin your workout with browser camera.")
        webrtc_streamer(
            key="fitness-webrtc",
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            async_processing=True,
        )
    else:
        st.warning("⚠️ Camera capture is unavailable in this environment.")




def generate_gemini_diet_plan(api_key, age, gender, weight, height, activity, goal, diet_type, meals_per_day, allergies, coach_prompt):
    """Generate pure AI diet plan using Google Gemini AI models."""
    if not api_key:
        raise ValueError("Gemini API key is required for AI diet generation. Please add GEMINI_API_KEY in .streamlit/secrets.toml.")

    prompt = f"""
    You are an expert Certified Sports Nutritionist and Elite AI Fitness Coach.
    Create a 100% customized, science-backed daily meal and nutrition plan tailored specifically to the user's requirements.

    USER PROFILE & DIETARY RESTRICTIONS:
    - Age: {age} years old
    - Gender: {gender}
    - Weight: {weight} kg
    - Height: {height} cm
    - Activity Level: {activity}
    - Primary Goal: {goal}
    - Strict Dietary Choice: {diet_type}
    - Meals Per Day: {meals_per_day}
    - Food Allergies / Restrictions: {allergies if allergies else 'None'}

    CRITICAL DIETARY RULES (YOU MUST FOLLOW ABSOLUTELY STRICTLY):
    - If Diet Choice is Vegetarian: Do NOT include chicken, meat, beef, pork, fish, seafood, or eggs. Focus on legumes, lentils, paneer, tofu, dairy, nuts, seeds, grains, and vegetables.
    - If Diet Choice is Vegan: Do NOT include meat, fish, dairy, cheese, butter, yogurt, or eggs. 100% plant-based only.
    - If Diet Choice is Keto: High healthy fats, moderate protein, very low carbohydrates (< 30g net carbs per day).
    - If Diet Choice is Non-Vegetarian: Include lean meats, poultry, eggs, fish, along with whole grains and vegetables.
    - If Diet Choice is Diabetic Friendly: Focus on low Glycemic Index (GI) foods, high soluble fiber, and controlled carbohydrate distribution.

    USER QUESTION / SPECIFIC INSTRUCTION:
    "{coach_prompt}"

    RESPONSE REQUIREMENTS:
    1. Personalized Nutrition Summary: Calculate exact daily calories (TDEE based), protein (g), carbohydrates (g), and healthy fats (g).
    2. Daily Meal Structure: Create {meals_per_day} distinct meals with specific meal names, delicious food items, exact portion sizes, and macronutrient breakdowns matching {diet_type}.
    3. Goal Alignment Tips: 3-4 actionable tips for achieving {goal}.
    4. Direct Response: Directly answer "{coach_prompt}".

    Format your output cleanly in Markdown with bold titles, bullet points, and emojis.
    """

    models_to_try = [
        'gemini-3.6-flash',
        'gemini-1.5-flash-latest',
        'gemini-flash-latest',
        'gemini-3.5-flash',
        'gemini-3-flash-preview',
        'gemini-pro-latest'
    ]

    last_error = None

    if genai is not None:
        try:
            genai.configure(api_key=api_key)
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as err:
                    last_error = err
                    continue
        except Exception as e:
            last_error = e

    if google_genai is not None:
        try:
            client = google_genai.Client(api_key=api_key)
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return response.text
                except Exception as err:
                    last_error = err
                    continue
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Could not generate AI plan with Gemini API: {last_error}")


def diet_plan_generator():
    """Personalized diet plan generator feature."""
    st.markdown("<h2>🥗 Personalized Diet Plan Generator</h2>", unsafe_allow_html=True)

    st.markdown("""
    Get a personalized nutrition plan tailored to your:
    - Body composition and metabolism
    - Activity level and fitness goals
    - Dietary preferences
    - Health requirements
    """)

    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    if api_key:
        st.success("🤖 Gemini AI API Key Active! Personalized AI nutrition coaching enabled.")
    else:
        st.error("⚠️ Gemini API key missing. Please configure GEMINI_API_KEY in `.streamlit/secrets.toml`.")

    # Collect user inputs
    st.markdown("### 👤 Your Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Gender", ["👨 Male", "👩 Female", "⚧️ Other"])
        age = st.slider("Age", 10, 100, 25)
    with col2:
        weight = st.slider("Weight (kg)", 30, 200, 70)
        height = st.slider("Height (cm)", 100, 250, 170)
    with col3:
        activity = st.selectbox("Activity Level", 
                               ["🛋️ Sedentary", "🚶 Lightly Active", "🏃 Moderately Active", "🚴 Very Active", "🏋️ Extremely Active"])
        diet_type = st.selectbox("Diet Type", 
                                ["🥗 Vegetarian", "🌱 Vegan", "🍗 Non-Vegetarian", "🥑 Keto", "🥩 High-Protein", "🍏 Diabetic Friendly", "🫒 Mediterranean"])

    # Additional preferences
    st.markdown("### 🎯 Preferences & Goals")
    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("Fitness Goal", ["🔥 Weight Loss", "💪 Muscle Gain", "⚖️ Maintenance", "🏃 Endurance"])
        allergies_flag = st.checkbox("Do you have food allergies?")
    with col2:
        meals_per_day = st.selectbox("Meals Per Day", [2, 3, 4, 5, 6])
        if allergies_flag:
            allergies = st.text_input("Enter allergies (comma-separated)")
        else:
            allergies = None

    st.markdown("### 💬 Ask Your Diet Coach")
    coach_prompt = st.text_area(
        "What would you like help with?",
        value=f"Create a simple {diet_type.lower()} meal plan for my goal to {goal.lower()} and activity level of {activity.lower()}."
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("✨ Ask Coach", use_container_width=True)

    if generate_button:
        with st.spinner("🤖 Preparing your personalized AI diet advice..."):
            plan_text = generate_gemini_diet_plan(api_key, age, gender, weight, height, activity, goal, diet_type, meals_per_day, allergies, coach_prompt)
            
            st.markdown("""
            <div class='success-card'>
                <h3>✅ Diet Coach Response Ready!</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(plan_text)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save as Text"):
                    plan_text_download = f"""
PERSONALIZED DIET PLAN
Generated for: {age}yo {gender} | {weight}kg | {height}cm

PROFILE:
- Activity Level: {activity}
- Goal: {goal}
- Diet Type: {diet_type}

{plan_text}
                    """
                    st.download_button(
                        label="Download Diet Plan",
                        data=plan_text_download,
                        file_name="my_diet_plan.txt",
                        mime="text/plain"
                    )
            
            with col2:
                st.info("💡 Tip: Adjust portions based on your hunger and progress. Review weekly!")


def progress_dashboard():
    """Dashboard to track workout history and fitness progress."""
    st.markdown("<h2>📈 Progress Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("""
    Track your workout history across different exercises. 
    Every time you complete a WebCam mode workout, it gets logged here!
    """)
    
    # Load history
    import json
    import pandas as pd
    
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []
                
        if not history:
            st.info("No workout history found yet. Complete a workout in WebCam mode to start tracking!")
            return
            
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><h3>Total <br>Workouts</h3><h1>{len(df)}</h1></div>", unsafe_allow_html=True)
        with col2:
            total_reps = df['reps'].sum()
            st.markdown(f"<div class='metric-card'><h3>Total <br>Reps</h3><h1>{total_reps}</h1></div>", unsafe_allow_html=True)
        with col3:
            fav_exercise = df['exercise'].mode()[0] if not df.empty else "N/A"
            st.markdown(f"<div class='metric-card'><h3>Favorite Exercise</h3><h3 style='color:#1e1b4b; margin-top: 15px;'>{fav_exercise}</h3></div>", unsafe_allow_html=True)
            
        st.markdown("<br><h3>🏋️ Recent Activity Logs</h3>", unsafe_allow_html=True)
        st.dataframe(df[['timestamp', 'exercise', 'reps']].sort_values(by='timestamp', ascending=False), 
                     use_container_width=True, hide_index=True)
        
    else:
        st.info("No workout history found yet. Complete a workout in 🎥 WebCam mode to automatically track your fitness journey!")


def generate_gemini_workout_plan(api_key, goal, level, days_per_week, equipment, duration, focus, notes):
    """Generate 100% customized 7-day workout routine using Gemini AI."""
    if not api_key:
        raise ValueError("Gemini API key is required for AI workout plan generation. Please configure GEMINI_API_KEY in .streamlit/secrets.toml.")

    prompt = f"""
    You are an elite Certified Strength and Conditioning Specialist (CSCS) and AI Workout Coach.
    Design a comprehensive, professional, 7-Day Weekly Workout Plan tailored precisely to the user's requirements.

    USER TRAINING PROFILE:
    - Primary Fitness Goal: {goal}
    - Experience / Fitness Level: {level}
    - Training Days Per Week: {days_per_week} days/week
    - Available Equipment: {equipment}
    - Workout Session Duration: {duration} minutes
    - Target Split / Focus: {focus}
    - Special Notes / Physical Preferences: {notes if notes else 'None'}

    CRITICAL WORKOUT DESIGN RULES:
    1. Structure a 7-day schedule (Day 1 through Day 7). Mark active workout days and designated Rest/Recovery days clearly based on {days_per_week} days/week.
    2. For every Active Workout Day, include:
       - Warm-up Routine (3-5 minutes dynamic stretches)
       - Main Workout Table: Exercise Name, Target Muscle, Sets, Reps, Rest Period, and Key Form Tip (suited for {equipment}).
       - Cool-down Routine (3-5 minutes static stretches)
    3. Ensure progressive overload principles suited for {level} level.
    4. Incorporate safety guidelines and tips for achieving {goal}.
    5. Directly address special notes: "{notes}" if provided.

    Format cleanly in GitHub-style Markdown with emojis, bold headers, and structured tables.
    """

    models_to_try = [
        'gemini-3.6-flash',
        'gemini-1.5-flash-latest',
        'gemini-flash-latest',
        'gemini-3.5-flash',
        'gemini-3-flash-preview',
        'gemini-pro-latest'
    ]

    last_error = None

    if genai is not None:
        try:
            genai.configure(api_key=api_key)
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as err:
                    last_error = err
                    continue
        except Exception as e:
            last_error = e

    if google_genai is not None:
        try:
            client = google_genai.Client(api_key=api_key)
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return response.text
                except Exception as err:
                    last_error = err
                    continue
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Could not generate AI workout plan with Gemini API: {last_error}")


def workout_plan_generator():
    """Personalized AI Weekly Workout Plan feature."""
    st.markdown("<h2>🗓️ AI Weekly Workout Routine Builder</h2>", unsafe_allow_html=True)

    st.markdown("""
    Get a custom, 7-day structured training schedule designed by AI:
    - Tailored to your fitness goal & experience level
    - Customized for your equipment (Bodyweight, Dumbbells, or Full Gym)
    - Complete with warm-ups, sets, reps, rest intervals, & cool-downs
    """)

    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    if api_key:
        st.success("🤖 Gemini AI API Key Active! Personalized AI workout routines enabled.")
    else:
        st.error("⚠️ Gemini API key missing. Please configure GEMINI_API_KEY in `.streamlit/secrets.toml`.")

    # Form inputs
    st.markdown("### 🎯 Your Workout Profile")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        goal = st.selectbox("Fitness Goal", ["🔥 Weight Loss & Fat Burn", "💪 Muscle Gain & Hypertrophy", "⚡ Strength & Power", "🏃 Endurance & Cardio", "⚖️ General Fitness & Toning"])
        level = st.selectbox("Fitness Level", ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"])
    with col2:
        days_per_week = st.selectbox("Training Days / Week", [3, 4, 5, 6])
        equipment = st.selectbox("Available Equipment", ["🧘 Bodyweight Only", "🏋️ Dumbbells Only", "🏢 Full Gym", "🎗️ Minimal / Resistance Bands"])
    with col3:
        duration = st.selectbox("Session Duration (mins)", [30, 45, 60, 75])
        focus = st.selectbox("Training Split Focus", ["🏋️ Full Body", "💪 Push / Pull / Legs", "🦵 Upper / Lower Body Split", "🔥 Cardio & HIIT Focus"])

    st.markdown("### 💬 Custom Notes / Physical Considerations")
    notes = st.text_input(
        "Any injuries, target muscle focus, or preferences?",
        placeholder="e.g. Focus on shoulder mobility, avoid heavy squats due to knee pain"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_btn = st.button("✨ Generate Weekly Plan", use_container_width=True)

    if generate_btn:
        if not api_key:
            st.error("❌ Please configure GEMINI_API_KEY in `.streamlit/secrets.toml` to generate your workout plan.")
        else:
            with st.spinner("🤖 Building your 7-day personalized workout plan..."):
                try:
                    plan_text = generate_gemini_workout_plan(api_key, goal, level, days_per_week, equipment, duration, focus, notes)
                    
                    st.markdown("""
                    <div class='success-card'>
                        <h3>✅ Weekly AI Workout Routine Ready!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(plan_text)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        download_data = f"""
PERSONALIZED WEEKLY WORKOUT PLAN
Generated for: Goal: {goal} | Level: {level} | Split: {focus}
Days/Week: {days_per_week} | Equipment: {equipment} | Duration: {duration}m

==================================================
{plan_text}
                        """
                        st.download_button(
                            label="💾 Download Workout Plan",
                            data=download_data,
                            file_name="my_weekly_workout_plan.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col2:
                        st.info("💡 Tip: Warm up before every session and stay hydrated throughout your workout!")
                except Exception as e:
                    st.error(f"❌ Error generating workout plan: {e}")


if __name__ == '__main__':
    main()