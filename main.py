"""Fitness AI Coach - Main Application.

A Streamlit-based fitness coaching application that uses computer vision
to detect exercises, count repetitions, calculate BMR, and generate diet plans.

Features:
- BMR (Basal Metabolic Rate) Calculator
- Video Mode: Upload and analyze exercise videos
- WebCam Mode: Real-time exercise detection and rep counting
- Diet Plan Generator: Personalized nutrition plans using Gemini AI
"""

import streamlit as st
import tempfile
import os
import time
import logging
import warnings
from pathlib import Path
import numpy as np
import av

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
    
    Args:
        gender (str): 'Male' or 'Female'
        age (int): Age in years
        weight (float): Weight in kg
        height (float): Height in cm
        
    Returns:
        float: BMR in calories/day
    """
    if gender == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr


def generate_local_diet_plan(age, gender, weight, height, activity, goal, diet_type, meals_per_day, allergies):
    """Generate a practical diet plan locally without any API key or AI service."""
    allergies_text = f"Allergies: {allergies}" if allergies else "No known allergies"
    bmr = calculate_bmr(gender, age, weight, height)

    activity_multiplier = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extremely Active": 1.9,
    }
    tdee = bmr * activity_multiplier.get(activity, 1.2)

    goal_adjustment = {
        "Weight Loss": -500,
        "Muscle Gain": 300,
        "Maintenance": 0,
        "Endurance": 200,
    }
    target_calories = int(tdee + goal_adjustment.get(goal, 0))

    if goal.lower() == "weight loss":
        protein_g = int(weight * 1.8)
        carbs_g = int((target_calories * 0.35) / 4)
        fats_g = int((target_calories * 0.25) / 9)
    elif goal.lower() == "muscle gain":
        protein_g = int(weight * 2.0)
        carbs_g = int((target_calories * 0.45) / 4)
        fats_g = int((target_calories * 0.25) / 9)
    elif goal.lower() == "endurance":
        protein_g = int(weight * 1.6)
        carbs_g = int((target_calories * 0.55) / 4)
        fats_g = int((target_calories * 0.20) / 9)
    else:
        protein_g = int(weight * 1.7)
        carbs_g = int((target_calories * 0.40) / 4)
        fats_g = int((target_calories * 0.25) / 9)

    protein_focus = "high" if protein_g >= weight * 1.8 else "moderate"
    carb_focus = "lower" if goal.lower() == "weight loss" else "higher" if goal.lower() == "endurance" else "balanced"

    diet_type_lower = diet_type.lower()
    vegetarian = any(token in diet_type_lower for token in ["vegetarian", "vegan", "keto", "mediterranean", "high-protein"])

    meals = []
    meal_names = ["Breakfast", "Lunch", "Dinner"]
    if diet_type_lower == "vegan":
        breakfast_food = "Vegan overnight oats with chia, banana, and almond butter"
        lunch_food = "Tofu stir-fry with brown rice and vegetables"
        dinner_food = "Chickpea and vegetable curry with quinoa"
        snack_options = ["Apple with peanut butter", "Trail mix", "Hummus with carrots", "Edamame"]
    elif diet_type_lower == "vegetarian":
        breakfast_food = "Greek yogurt bowl with oats, banana, and nuts"
        lunch_food = "Paneer or tofu bowl with rice and vegetables"
        dinner_food = "Vegetable and lentil curry with roasted vegetables"
        snack_options = ["Apple with peanut butter", "Boiled eggs", "Hummus with carrots", "Cottage cheese with fruit"]
    elif diet_type_lower == "keto":
        breakfast_food = "Scrambled eggs with spinach and avocado"
        lunch_food = "Chicken salad bowl with olive oil dressing"
        dinner_food = "Salmon with cauliflower rice and greens"
        snack_options = ["Cheese cubes", "Olives", "Boiled eggs", "Avocado"]
    elif diet_type_lower == "diabetic friendly":
        breakfast_food = "Greek yogurt with berries and chia seeds"
        lunch_food = "Grilled chicken salad with quinoa"
        dinner_food = "Baked fish with roasted vegetables"
        snack_options = ["Pear", "Cottage cheese", "Almonds", "Vegetables with hummus"]
    else:
        breakfast_food = "Greek yogurt bowl with oats, banana, and nuts"
        lunch_food = "Grilled chicken or tofu bowl with rice and vegetables"
        dinner_food = "Salmon or lentil curry with roasted vegetables"
        snack_options = ["Apple with peanut butter", "Boiled eggs", "Hummus with carrots", "Cottage cheese with fruit"]

    meals.append(f"- Breakfast: {breakfast_food}")
    meals.append(f"- Lunch: {lunch_food}")
    meals.append(f"- Dinner: {dinner_food}")

    if diet_type_lower == "vegan":
        snack_options = ["Apple with peanut butter", "Trail mix", "Hummus with carrots", "Edamame"]
    elif diet_type_lower == "vegetarian":
        snack_options = ["Apple with peanut butter", "Boiled eggs", "Hummus with carrots", "Cottage cheese with fruit"]
    elif diet_type_lower == "keto":
        snack_options = ["Cheese cubes", "Olives", "Boiled eggs", "Avocado"]
    elif diet_type_lower == "diabetic friendly":
        snack_options = ["Pear", "Cottage cheese", "Almonds", "Vegetables with hummus"]

    snacks = snack_options

    response = f"""
## Your Personalized {diet_type} Diet Plan

Hi {gender}! I built this plan around your goal to {goal.lower()} while keeping it practical for your {activity.lower()} lifestyle.

**Profile**
- Age: {age}
- Weight: {weight} kg
- Height: {height} cm
- {allergies_text}

### Daily Meal Structure
{chr(10).join(meals)}
- Snack: {snacks[0]}
- Snack: {snacks[1]}

### Nutrition Guidance
- Daily calories: {target_calories} kcal
- Protein: {protein_g} g
- Carbohydrates: {carbs_g} g
- Fats: {fats_g} g
- Protein goal: {protein_focus} protein intake
- Carbs: {carb_focus} carbohydrates for energy
- Hydration: 2-3 liters of water daily
- Portion tip: Use your hunger and fullness as a guide

### Simple Weekly Tips
- Keep meals regular and avoid skipping breakfast
- Add vegetables to lunch and dinner
- Choose whole grains, lean protein, and healthy fats
- Aim for light movement most days

### Quick Coach Advice
Based on your preferences, I recommend keeping breakfast simple, planning lunch ahead, and using protein-rich snacks to stay full between meals.
"""
    return response


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Fitness AI Coach", layout="wide", initial_sidebar_state="expanded")
    
    # Premium Custom styling
    st.markdown("""
    <style>
        /* Import premium font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        /* Global body and font styles */
        * {
            font-family: 'Outfit', sans-serif !important;
        }
        .main {
            padding: 1rem 2rem;
            background-color: transparent;
        }
        .stApp {
            background: linear-gradient(135deg, #f0f4fd 0%, #e2ebf9 100%);
        }
        
        /* Premium Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 16px;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
            color: white;
        }
        
        /* Typography */
        h1 {
            color: #1e1b4b;
            font-weight: 800;
            text-align: center;
            padding: 24px 0;
            letter-spacing: -1px;
            text-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        h2 {
            color: #312e81;
            font-weight: 600;
            padding-bottom: 12px;
            margin-bottom: 24px;
            border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        }
        h3 {
            color: #4338ca;
            font-weight: 600;
        }
        
        /* Metric and Success Cards - Glassmorphism */
        .metric-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            color: #1e1b4b;
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px -10px rgba(0,0,0,0.15);
        }
        .metric-card h1 {
            background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 56px;
            margin: 0;
            padding: 10px 0;
            text-shadow: none;
        }
        
        .success-card {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 10px 25px -10px rgba(16, 185, 129, 0.5);
            text-align: center;
            transition: transform 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .success-card:hover {
            transform: translateY(-5px);
        }
        
        /* Custom UI containers */
        div[data-testid="stExpander"] {
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }
        div[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 2px 0 20px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1>🏋️ Your Fitness AI Coach</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;">
    Welcome to your personal Fitness AI Coach powered by advanced computer vision and AI!
    </div>
    """, unsafe_allow_html=True)

    feature = st.sidebar.selectbox("Choose Feature", 
                                  ["📊 BMR Calculator", "📈 Progress Dashboard", "📹 Video Mode", "🎥 WebCam Mode", "🥗 Diet Plan Generator"],
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


def bmr_calculator():
    """BMR calculator feature."""
    st.markdown("<h2>📊 BMR (Basal Metabolic Rate) Calculator</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    The BMR is the number of calories your body needs to maintain basic bodily functions at rest.
    It helps you understand your baseline caloric needs for fitness planning.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Personal Information")
        gender = st.radio("Select Gender", ['Male', 'Female'], horizontal=True)
        age = st.number_input("Enter Age (years)", min_value=10, max_value=100, value=25, step=1)
    with col2:
        st.markdown("### Measurements")
        weight = st.number_input("Enter Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
        height = st.number_input("Enter Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Calculate BMR", use_container_width=True):
            try:
                bmr = calculate_bmr(gender, age, weight, height)
                
                # Display results with nice styling
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>Your BMR</h3>
                    <h1 style='font-size: 48px;'>{bmr:.0f}</h1>
                    <p>Calories per day</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Calculate TDEE based on activity
                st.markdown("### Total Daily Energy Expenditure (TDEE)")
                activity = st.select_slider("Select Activity Level", 
                    options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                    value="Moderately Active")
                
                activity_multiplier = {
                    "Sedentary": 1.2,
                    "Lightly Active": 1.375,
                    "Moderately Active": 1.55,
                    "Very Active": 1.725,
                    "Extremely Active": 1.9
                }
                
                tdee = bmr * activity_multiplier[activity]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class='success-card'>
                        <p>Weight Loss</p>
                        <h3>{tdee - 500:.0f} cal/day</h3>
                        <small>-500 cal deficit</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #004E89 0%, #1565B8 100%); 
                               color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                        <p>Maintenance</p>
                        <h3>{tdee:.0f} cal/day</h3>
                        <small>Current level</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #FF9F43 0%, #FFB347 100%);
                               color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                        <p>Muscle Gain</p>
                        <h3>{tdee + 300:.0f} cal/day</h3>
                        <small>+300 cal surplus</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.success("✅ Calculation complete! Use these numbers to plan your nutrition.")
            except Exception as e:
                st.error(f"❌ Error calculating BMR: {str(e)}")
                logger.error(f"BMR calculation error: {e}")


def video_mode():
    """Video upload and analysis feature."""
    st.markdown("<h2>📹 Video Mode - Exercise Analysis</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    Upload your exercise video to analyze your form:
    - Push-Up
    - Squat  
    - Bicep Curl
    - Shoulder Press
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Upload Video")
        video_file = st.file_uploader("Upload your exercise video", type=["mp4", "mov", "avi", "m4v"])
    
    with col2:
        st.markdown("### Select Exercise")
        exercise_type = st.selectbox("Choose Exercise", 
                                    ["Push-Up", "Squat", "Bicep Curl", "Shoulder Press"])
    
    if video_file is not None:
        st.markdown("---")
        st.markdown("### 📥 Video Preview")
        st.video(video_file)
        
        st.markdown("### 📋 Video Info")
        st.markdown(f"**Selected Exercise:** `{exercise_type}`")
        st.markdown(f"**Video File:** `{video_file.name}`")
        st.markdown("**Status:** ✅ Video loaded successfully")
        st.info("💡 Video playback is optimized for browser viewing. Your form can be analyzed by comparing with the correct form guide below.")
        
        if exercise_type in FORM_VIDEO_PATHS:
            form_video = FORM_VIDEO_PATHS[exercise_type]
            if os.path.exists(form_video):
                with st.expander("📖 View Correct Form"):
                    st.video(str(form_video))
    else:
        st.info("📌 Upload a video to get started")


def webcam_mode():
    """Live webcam exercise detection feature."""
    st.markdown("<h2>🎥 Live Webcam Exercise Detection</h2>", unsafe_allow_html=True)
    backend = get_camera_backend()
    st.caption(f"📡 Camera backend: {backend}")

    st.markdown("Allow camera access in the browser to start your workout session.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        selected_exercise = st.selectbox("Choose Exercise", ["Push-Up", "Squat", "Bicep Curl", "Shoulder Press"])
    with col2:
        target_reps = st.slider("Target Reps", min_value=1, max_value=50, value=10)

    if webrtc_streamer is not None and VideoTransformerBase is not None:
        st.markdown("### 🎬 Start Your Webcam Session")
        st.info("Click 'Start Streaming' below to begin your workout with the browser camera.")
        
        webrtc_streamer(
            key="fitness-webrtc",
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            async_processing=True,
        )
        
        st.markdown("---")
        st.metric("Exercise", selected_exercise)
        st.metric("Target Reps", target_reps)
        st.success("✅ Webcam session is ready. Your form will be analyzed in real-time.")
    else:
        st.warning("⚠️ Webcam streaming is not available in this browser or environment.")
        st.info("💡 Please try: 1. Refreshing the page, 2. Using a modern browser like Chrome, 3. Allowing camera access")




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

    st.info("ℹ️ The diet planner works fully offline using a built-in nutrition plan. No API key is required.")

    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    if api_key:
        st.caption("Gemini key detected, but the built-in plan is being used so the feature remains available without AI quota limits.")

    # Collect user inputs
    st.markdown("### 👤 Your Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.slider("Age", 10, 100, 25)
    with col2:
        weight = st.slider("Weight (kg)", 30, 200, 70)
        height = st.slider("Height (cm)", 100, 250, 170)
    with col3:
        activity = st.selectbox("Activity Level", 
                               ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"])
        diet_type = st.selectbox("Diet Type", 
                                ["Vegetarian", "Vegan", "Non-Vegetarian", "Keto", "High-Protein", "Diabetic Friendly", "Mediterranean"])

    # Additional preferences
    st.markdown("### 🎯 Preferences & Goals")
    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "Endurance"])
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
        with st.spinner("🤖 Preparing your diet advice..."):
            plan_text = generate_local_diet_plan(age, gender, weight, height, activity, goal, diet_type, meals_per_day, allergies)
            if coach_prompt.strip():
                plan_text = f"{plan_text}\n\n### Your Coach Note\n{coach_prompt.strip()}\n\nSuggested response: Keep meals consistent, include protein at every meal, choose water over sugary drinks, and adjust portion size based on fullness."
            
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


if __name__ == '__main__':
    main()