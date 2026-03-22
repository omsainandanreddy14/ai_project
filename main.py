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
import cv2
import tempfile
import ExerciseAiTrainer as exercise
import os
import time
import mediapipe as mp
import logging
import warnings
from ExerciseAiTrainer import Exercise
from AiTrainer_utils import distanceCalculate

# Suppress unnecessary warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEMO_VIDEO_PATH = 'demo.mp4'
FORM_VIDEO_PATHS = {
    'Bicep Curl': 'curl_form.mp4',
    'Push-Up': 'push_up_form.mp4',
    'Squat': 'squat_form.mp4',
    'Shoulder Press': 'shoulder_press_form.mp4'
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
    Upload your exercise video to get:
    - Rep counting and form analysis
    - Real-time feedback
    - Performance metrics
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
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(video_file.read())
                temp_path = temp_file.name
        except Exception as e:
            st.error(f"❌ Error uploading video: {str(e)}")
            logger.error(f"Video upload error: {e}")
            return
    else:
        # Use demo video if available
        if os.path.exists(DEMO_VIDEO_PATH):
            temp_path = DEMO_VIDEO_PATH
        else:
            st.info("📌 Tip: Upload a video or place demo.mp4 in the root folder")
            return
    
    try:
        # Video preview section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📥 Input Video Preview")
            st.video(temp_path)
        
        with col2:
            st.markdown("### 📋 Analysis Settings")
            st.markdown(f"**Selected Exercise:** `{exercise_type}`")
            st.markdown(f"**Video File:** `{video_file.name if video_file else 'demo.mp4'}`")
            
            # Display form instruction
            if exercise_type in FORM_VIDEO_PATHS:
                form_video = FORM_VIDEO_PATHS[exercise_type]
                if os.path.exists(form_video):
                    st.markdown(f"#### Correct Form Guide")
                    with st.expander("View correct form"):
                        st.video(form_video)

        # Analyze button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_button = st.button("🔍 Analyze Video", use_container_width=True)
        
        if analyze_button:
            with st.spinner("🔄 Processing video... This may take a moment."):
                trainer = Exercise()
                try:
                    cap = cv2.VideoCapture(temp_path)
                    if not cap.isOpened():
                        st.error("❌ Cannot open video file")
                        return
                    
                    output_path = None
                    
                    if exercise_type == "Push-Up":
                        output_path = trainer.push_up(cap, mode='video')
                    elif exercise_type == "Squat":
                        output_path = trainer.squat(cap, mode='video')
                    elif exercise_type == "Bicep Curl":
                        output_path = trainer.bicep_curl(cap, mode='video')
                    elif exercise_type == "Shoulder Press":
                        output_path = trainer.shoulder_press(cap, mode='video')
                    
                    if output_path and os.path.exists(output_path):
                        st.markdown("---")
                        st.markdown("### ✅ Processed Output")
                        st.video(output_path)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success("✅ Video processed successfully!")
                        with col2:
                            with open(output_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Output Video",
                                    data=f.read(),
                                    file_name=output_path,
                                    mime="video/mp4"
                                )
                    else:
                        st.error(f"❌ Failed to generate output. Output path: {output_path}")
                except Exception as e:
                    st.error(f"❌ Error processing video: {str(e)}")
                    logger.error(f"Video processing error: {e}")
                finally:
                    cap.release()
                    cv2.destroyAllWindows()
    except Exception as e:
        st.error(f"❌ Error in video mode: {str(e)}")
        logger.error(f"Video mode error: {e}")


def webcam_mode():
    """Live webcam exercise detection feature."""
    st.markdown("<h2>🎥 Live Webcam Exercise Detection</h2>", unsafe_allow_html=True)

    # Initialize session state
    if 'webcam_running' not in st.session_state:
        st.session_state.webcam_running = False
    if 'current_rep' not in st.session_state:
        st.session_state.current_rep = 0
    if 'goal_reached' not in st.session_state:
        st.session_state.goal_reached = False

    # Sidebar: Select Exercise and Set Goals
    st.sidebar.markdown("### 🎯 Exercise Settings")
    selected_exercise = st.sidebar.selectbox("Choose Exercise", 
                                            ["Push-Up", "Squat", "Bicep Curl", "Shoulder Press"])
    target_reps = st.sidebar.slider("Target Reps", min_value=1, max_value=50, value=10)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📖 Correct Form Guide")
        if selected_exercise in FORM_VIDEO_PATHS:
            form_video = FORM_VIDEO_PATHS[selected_exercise]
            if os.path.exists(form_video):
                st.video(form_video)
            else:
                st.info(f"ℹ️ Form video for {selected_exercise} not found")
        
        # Exercise tips
        tips = {
            "Push-Up": [
                "✓ Keep body straight from head to heels",
                "✓ Lower chest until it nearly touches floor",
                "✓ Push back up to starting position",
                "✓ Maintain control throughout movement"
            ],
            "Squat": [
                "✓ Feet shoulder-width apart",
                "✓ Chest up, core engaged",
                "✓ Lower until thighs are parallel to ground",
                "✓ Drive through heels to stand up"
            ],
            "Bicep Curl": [
                "✓ Keep elbows fixed at sides",
                "✓ Curl weights toward shoulders",
                "✓ Lower with control",
                "✓ No swinging motion"
            ],
            "Shoulder Press": [
                "✓ Feet shoulder-width apart",
                "✓ Press weights overhead",
                "✓ Extend arms fully at top",
                "✓ Lower back to shoulders"
            ]
        }
        
        with st.expander("💡 Exercise Tips"):
            for tip in tips.get(selected_exercise, []):
                st.markdown(tip)
    
    with col2:
        st.markdown("### ⚙️ Exercise Progress")
        
        # Control buttons
        col_start, col_stop = st.columns(2)
        with col_start:
            if st.button("▶️ Start Exercise", use_container_width=True):
                st.session_state.webcam_running = True
                st.session_state.current_rep = 0
                st.session_state.goal_reached = False
                st.rerun()
        
        with col_stop:
            if st.button("⏹️ Stop Exercise", use_container_width=True):
                st.session_state.webcam_running = False
                st.rerun()
        
        # Progress display
        st.markdown("---")
        progress = st.session_state.current_rep / target_reps if target_reps > 0 else 0
        progress = min(progress, 1.0)
        
        st.metric("Current Reps", st.session_state.current_rep, f"{target_reps} target")
        st.progress(progress, f"Progress: {st.session_state.current_rep}/{target_reps}")
        
        if st.session_state.goal_reached:
            st.markdown("""
            <div class='success-card'>
                <h3>🎉 Goal Reached!</h3>
                <p>Excellent work! You've completed your target reps.</p>
            </div>
            """, unsafe_allow_html=True)

    # Live video capture
    if st.session_state.webcam_running:
        stframe = st.empty()
        status_placeholder = st.empty()
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("❌ Cannot access webcam. Please check camera permissions.")
                st.session_state.webcam_running = False
                return
            
            trainer = Exercise()
            detector = exercise.pm.posture_detector()
            counter = 0
            stage = None
            frame_count = 0
            
            while st.session_state.webcam_running and frame_count < 5000:  # Safety limit
                ret, frame = cap.read()
                if not ret:
                    st.error("❌ Failed to read from webcam")
                    break
                
                frame_count += 1
                
                # Flip for mirror view
                frame = cv2.flip(frame, 1)
                
                # Run pose detection
                img = detector.find_person(frame)
                landmark_list = detector.find_landmarks(img, False)
                
                # Only process if landmarks detected
                if landmark_list is not None and len(landmark_list) != 0:
                    # Exercise-specific detection
                    if selected_exercise == "Push-Up":
                        right_shoulder = landmark_list[12][1:]
                        right_wrist = landmark_list[16][1:]
                        distance = exercise.distanceCalculate(right_shoulder, right_wrist)
                        
                        if distance < 130:
                            stage = "down"
                        if distance > 250 and stage == "down":
                            stage = "up"
                            st.session_state.current_rep += 1
                            counter = st.session_state.current_rep
                    
                    elif selected_exercise == "Squat":
                        right_leg_angle = detector.find_angle(img, 24, 26, 28)
                        left_leg_angle = detector.find_angle(img, 23, 25, 27)
                        
                        if right_leg_angle > 140 and left_leg_angle < 240:
                            stage = "down"
                        if right_leg_angle < 80 and left_leg_angle > 270 and stage == 'down':
                            stage = "up"
                            st.session_state.current_rep += 1
                            counter = st.session_state.current_rep
                    
                    elif selected_exercise == "Bicep Curl":
                        left_arm_angle = detector.find_angle(img, 11, 13, 15)
                        
                        if left_arm_angle < 230:
                            stage = "down"
                        if left_arm_angle > 310 and stage == 'down':
                            stage = "up"
                            st.session_state.current_rep += 1
                            counter = st.session_state.current_rep
                    
                    elif selected_exercise == "Shoulder Press":
                        right_arm_angle = detector.find_angle(img, 12, 14, 16)
                        left_arm_angle = detector.find_angle(img, 11, 13, 15)
                        
                        if right_arm_angle > 315 and left_arm_angle < 40:
                            stage = "down"
                        if right_arm_angle < 240 and left_arm_angle > 130 and stage == 'down':
                            stage = "up"
                            st.session_state.current_rep += 1
                            counter = st.session_state.current_rep
                
                # Display rep counter on image
                cv2.rectangle(img, (0, 0), (250, 100), (255, 107, 53), -1)
                cv2.putText(img, 'REPS', (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(img, str(counter), (15, 95), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 3, cv2.LINE_AA)
                
                # Display status
                status_color = (50, 205, 50) if stage == "up" else (255, 107, 53)
                cv2.rectangle(img, (img.shape[1]-300, 0), (img.shape[1], 60), status_color, -1)
                cv2.putText(img, f"Status: {stage}", (img.shape[1]-280, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Display frame
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                stframe.image(img_rgb, use_column_width=True)
                
                # Update progress bar
                progress = st.session_state.current_rep / target_reps if target_reps > 0 else 0
                progress = min(progress, 1.0)
                status_placeholder.progress(progress, f"🏋️ {st.session_state.current_rep}/{target_reps} reps")
                
                # Check if workout goal is complete
                if st.session_state.current_rep >= target_reps:
                    st.session_state.goal_reached = True
                    st.balloons()
                    st.success("🎯 Target reps reached! Great job!")
                    
                    # Log the workout history
                    import json
                    from datetime import datetime
                    history_file = "workout_history.json"
                    history = []
                    if os.path.exists(history_file):
                        with open(history_file, "r") as f:
                            try:
                                history = json.load(f)
                            except:
                                pass
                    history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "exercise": selected_exercise,
                        "reps": st.session_state.current_rep
                    })
                    with open(history_file, "w") as f:
                        json.dump(history, f)
                        
                    st.session_state.webcam_running = False
                    break
                
                time.sleep(0.02)  # Small delay for smooth playback
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            st.error(f"❌ Error in webcam mode: {str(e)}")
            logger.error(f"Webcam mode error: {e}")
            st.session_state.webcam_running = False
    else:
        st.info("👆 Click 'Start Exercise' button to begin your workout!")


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

    # Check API availability
    if genai is None:
        st.error("❌ Google Generative AI not installed.")
        st.code("pip install google-generativeai", language="bash")
        return

    # Check for API key
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.error("❌ GEMINI_API_KEY not found in secrets.")
            with st.expander("📝 How to add API key"):
                st.markdown("""
                1. Create a `.streamlit/secrets.toml` file in your project root
                2. Add your Gemini API key:
                ```toml
                GEMINI_API_KEY = "your-api-key-here"
                ```
                3. Get your free API key from: https://ai.google.dev/
                """)
            return
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"❌ API configuration error: {str(e)}")
        logger.error(f"API config error: {e}")
        return

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

    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("✨ Generate Diet Plan", use_container_width=True)

    if generate_button:
        try:
            with st.spinner("🤖 Generating your personalized diet plan..."):
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                allergies_text = f"Avoid: {allergies}" if allergies else "No allergies"
                
                prompt = f"""
                Create a detailed, personalized {diet_type.lower()} diet plan with these specific criteria:
                
                **User Profile:**
                - Age: {age} years old, {gender}
                - Weight: {weight} kg, Height: {height} cm
                - Activity Level: {activity}
                - Fitness Goal: {goal}
                - {allergies_text}
                - Preferred meals per day: {meals_per_day}
                
                **Requirements:**
                1. Create a realistic weekly meal plan ({meals_per_day} meals/day)
                2. Include breakfast, lunch, dinner, and snacks with approximate calories
                3. Add macros breakdown (protein, carbs, fats) for each meal
                4. Include preparation time and difficulty level
                5. Make recipes practical and easy to follow
                6. Provide shopping list for the week
                7. Add nutritional tips for their fitness goal
                8. Include hydration recommendations
                
                Make the plan engaging, motivating, and achievable!
                """
                
                response = model.generate_content(prompt)
                
                # Display success message
                st.markdown("""
                <div class='success-card'>
                    <h3>✅ Diet Plan Generated Successfully!</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the plan
                st.markdown("---")
                st.markdown(response.text)
                
                # Save plan option
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save as Text"):
                        plan_text = f"""
PERSONALIZED DIET PLAN
Generated for: {age}yo {gender} | {weight}kg | {height}cm

PROFILE:
- Activity Level: {activity}
- Goal: {goal}
- Diet Type: {diet_type}

{response.text}
                        """
                        st.download_button(
                            label="Download Diet Plan",
                            data=plan_text,
                            file_name="my_diet_plan.txt",
                            mime="text/plain"
                        )
                
                with col2:
                    st.info("💡 Tip: Adjust portions based on your hunger and progress. Review weekly!")
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota exceeded" in error_msg:
                st.error("❌ Rate Limit Exceeded. You have used up your free Gemini API quota. Please wait a moment and try again, or use a different API key.")
            else:
                st.error(f"❌ Failed to generate diet plan: {error_msg}")
            logger.error(f"Diet plan generation error: {e}")


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
    history_file = "workout_history.json"
    
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
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