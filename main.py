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
    st.set_page_config(page_title="Fitness AI Coach", layout="wide")
    st.title('🏋️ Your Fitness AI Coach')
    st.write("Welcome to your personal Fitness AI Coach powered by computer vision!")

    feature = st.sidebar.selectbox("Choose Feature", 
                                  ["BMR Calculator", "Video Mode", "WebCam Mode", "Diet Plan Generator"])

    if feature == "BMR Calculator":
        bmr_calculator()
    elif feature == "Video Mode":
        video_mode()
    elif feature == "WebCam Mode":
        webcam_mode()
    elif feature == "Diet Plan Generator":
        diet_plan_generator()


def bmr_calculator():
    """BMR calculator feature."""
    st.subheader("📊 BMR (Basal Metabolic Rate) Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("Select Gender", ['Male', 'Female'])
        age = st.number_input("Enter Age", min_value=10, max_value=100, value=25, step=1)
    with col2:
        weight = st.number_input("Enter Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
        height = st.number_input("Enter Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)

    if st.button("Calculate BMR"):
        try:
            bmr = calculate_bmr(gender, age, weight, height)
            st.success(f"Your BMR is **{bmr:.2f}** calories/day")
            st.info("This is the number of calories your body needs at rest. Use it to plan your fitness goals!")
        except Exception as e:
            st.error(f"Error calculating BMR: {str(e)}")
            logger.error(f"BMR calculation error: {e}")


def video_mode():
    """Video upload and analysis feature."""
    st.subheader('📹 Upload Your Exercise Video')
    
    video_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "m4v"])
    
    if video_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(video_file.read())
                temp_path = temp_file.name
        except Exception as e:
            st.error(f"Error uploading video: {str(e)}")
            logger.error(f"Video upload error: {e}")
            return
    else:
        # Use demo video if available
        if os.path.exists(DEMO_VIDEO_PATH):
            temp_path = DEMO_VIDEO_PATH
        else:
            st.warning("No video provided and demo.mp4 not found")
            return
    
    try:
        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            st.error("Cannot open video file")
            return

        # Display input video
        st.markdown("### 📥 Input Preview")
        st.video(temp_path)

        # Select exercise
        exercise_type = st.selectbox("Select Exercise Type", 
                                    ["Push-Up", "Squat", "Bicep Curl", "Shoulder Press"])

        if st.button("Analyze Video"):
            with st.spinner("Processing video..."):
                trainer = Exercise()
                try:
                    if exercise_type == "Push-Up":
                        output_path = trainer.push_up(cap, mode='video')
                    elif exercise_type == "Squat":
                        output_path = trainer.squat(cap, mode='video')
                    elif exercise_type == "Bicep Curl":
                        output_path = trainer.bicep_curl(cap, mode='video')
                    elif exercise_type == "Shoulder Press":
                        output_path = trainer.shoulder_press(cap, mode='video')
                    
                    if output_path and os.path.exists(output_path):
                        st.markdown("### ✅ Processed Output")
                        st.video(output_path)
                        st.success("Video processed successfully!")
                    else:
                        st.error("Failed to generate output video.")
                except Exception as e:
                    st.error(f"Error processing video: {str(e)}")
                    logger.error(f"Video processing error: {e}")
                finally:
                    cap.release()
                    cv2.destroyAllWindows()
    except Exception as e:
        st.error(f"Error in video mode: {str(e)}")
        logger.error(f"Video mode error: {e}")


def webcam_mode():
    """Live webcam exercise detection feature."""
    st.subheader('📹 Live Webcam Exercise Detection')

    # Sidebar: Select Exercise and Set Goals
    st.sidebar.subheader("🎯 Set Your Exercise Goal")
    selected_exercise = st.sidebar.selectbox("Choose Exercise", 
                                            ["Push-Up", "Squat", "Bicep Curl", "Shoulder Press"])
    target_reps = st.sidebar.number_input("Target Reps", min_value=1, max_value=100, value=10)

    # Show correct form preview
    st.markdown("### 📖 Correct Form Preview")
    if selected_exercise in FORM_VIDEO_PATHS:
        form_video = FORM_VIDEO_PATHS[selected_exercise]
        if os.path.exists(form_video):
            st.video(form_video)
        else:
            st.info(f"Form video for {selected_exercise} not available")

    # Initialize session state
    if 'current_rep' not in st.session_state:
        st.session_state.current_rep = 0
    if 'goal_reached' not in st.session_state:
        st.session_state.goal_reached = False
    if 'webcam_running' not in st.session_state:
        st.session_state.webcam_running = False

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Cannot open webcam. Please check your camera permissions.")
            return

        stframe = st.empty()
        status_placeholder = st.empty()
        trainer = Exercise()
        detector = exercise.pm.posture_detector()
        counter = 0
        stage = None

        # Start button
        col1, col2 = st.columns(2)
        with col1:
            start_button = st.button("Start Exercise")
        with col2:
            stop_button = st.button("Stop Exercise")

        if start_button:
            st.session_state.webcam_running = True
            st.session_state.current_rep = 0
            st.session_state.goal_reached = False

        while st.session_state.webcam_running:
            if stop_button or st.session_state.goal_reached:
                st.session_state.webcam_running = False
                break

            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read from webcam")
                break

            # Flip for mirror view
            frame = cv2.flip(frame, 1)

            # Run pose detection
            img = detector.find_person(frame)
            landmark_list = detector.find_landmarks(img, False)

            # Only process if landmarks detected
            if landmark_list is not None and len(landmark_list) != 0:
                # Exercise-specific angle detection
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
            cv2.rectangle(img, (0, 0), (225, 73), (245, 117, 16), -1)
            cv2.putText(img, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Display frame
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            stframe.image(img_rgb, channels='RGB', use_column_width=True)

            # Display progress
            status_placeholder.markdown(f"""
            ### 🏋️ Exercise Progress:
            - **Exercise:** {selected_exercise}  
            - **Reps Completed:** {st.session_state.current_rep}/{target_reps}  
            - **Status:** {'✅ Goal Reached!' if st.session_state.current_rep >= target_reps else '🔄 In Progress'}
            """)

            # Check if workout goal is complete
            if st.session_state.current_rep >= target_reps:
                st.session_state.goal_reached = True
                st.balloons()
                st.success("🎯 Target reps reached! Great job!")
                st.warning("Click 'Stop Exercise' to finish")
                break

            time.sleep(0.1)  # Small delay to prevent excessive processing

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        st.error(f"Error in webcam mode: {str(e)}")
        logger.error(f"Webcam mode error: {e}")


def diet_plan_generator():
    """Personalized diet plan generator feature."""
    st.subheader("🥗 Personalized Diet Plan Generator")

    if genai is None:
        st.error("Google Generative AI not installed. Please install: pip install google-generativeai")
        return

    # Configure Gemini API using Streamlit Secrets
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"API configuration error: {str(e)}")
        logger.error(f"API error: {e}")
        return

    # Collect user inputs
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Select Gender", ["Male", "Female"])
        age = st.slider("Age", 10, 100, 25)
        weight = st.slider("Weight (kg)", 30, 200, 70)
    with col2:
        height = st.slider("Height (cm)", 100, 250, 170)
        activity = st.selectbox("Activity Level", 
                               ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        diet_type = st.selectbox("Diet Preference", 
                                ["Vegetarian", "Vegan", "Non-Vegetarian", "Keto", "High-Protein", "Diabetic Friendly"])

    if st.button("Generate Diet Plan"):
        try:
            with st.spinner("Generating your personalized diet plan..."):
                model = genai.GenerativeModel("gemini-2.0-flash")
                prompt = f"""
                Generate a personalized {diet_type.lower()} diet plan for a {age}-year-old {gender.lower()} 
                who weighs {weight} kg and is {height} cm tall.
                Activity level: {activity}.
                Include breakfast, lunch, dinner, and 2 snacks with approximate calories.
                Make it practical and easy to follow.
                """
                response = model.generate_content(prompt)
                st.success("✅ Diet plan generated!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"❌ Failed to generate diet plan: {str(e)}")
            logger.error(f"Diet plan generation error: {e}")


if __name__ == '__main__':
    main()
