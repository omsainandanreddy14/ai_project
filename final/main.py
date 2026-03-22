import streamlit as st
import cv2
import tempfile
import ExerciseAiTrainer as exercise
import os
import time
import mediapipe as mp
from ExerciseAiTrainer import Exercise



# Function to get diet plan based on fitness goal
def get_diet_plan(goal):
    if goal == 'Weight Loss':
        return """
        ## Weight Loss: Healthy and Balanced Plan

        ### Day 1
        - **Breakfast**: Oats with chia seeds and almond milk (300 kcal)
        - **Lunch**: Grilled chicken salad with quinoa and olive oil dressing (500 kcal)
        - **Snack**: Greek yogurt with berries (150 kcal)
        - **Dinner**: Baked salmon with steamed broccoli and sweet potatoes (600 kcal)

        ### Day 2
        - **Breakfast**: Scrambled eggs with avocado on whole wheat toast (350 kcal)
        - **Lunch**: Turkey and hummus wrap with mixed veggies (450 kcal)
        - **Snack**: Protein smoothie (200 kcal)
        - **Dinner**: Stir-fried tofu with mixed vegetables and brown rice (550 kcal)

        ### Day 3
        - **Breakfast**: Smoothie bowl with banana, berries, and almond butter (350 kcal)
        - **Lunch**: Grilled salmon with mixed greens and olive oil (500 kcal)
        - **Snack**: Carrot sticks with hummus (150 kcal)
        - **Dinner**: Chicken breast with roasted vegetables (600 kcal)

        ### Day 4
        - **Breakfast**: Greek yogurt with nuts and berries (300 kcal)
        - **Lunch**: Grilled chicken and quinoa bowl with avocado (450 kcal)
        - **Snack**: Apple slices with almond butter (200 kcal)
        - **Dinner**: Zucchini noodles with marinara sauce and turkey meatballs (500 kcal)

        ### Day 5
        - **Breakfast**: Scrambled egg whites with spinach (250 kcal)
        - **Lunch**: Tuna salad with leafy greens (400 kcal)
        - **Snack**: Protein bar (200 kcal)
        - **Dinner**: Baked cod with green beans and quinoa (600 kcal)

        ### Day 6
        - **Breakfast**: Oatmeal with flax seeds and berries (350 kcal)
        - **Lunch**: Grilled chicken with steamed veggies and sweet potato (500 kcal)
        - **Snack**: Greek yogurt with chia seeds (150 kcal)
        - **Dinner**: Baked turkey with Brussels sprouts and brown rice (600 kcal)

        ### Day 7
        - **Breakfast**: Veggie omelette with mushrooms, spinach, and tomatoes (300 kcal)
        - **Lunch**: Grilled shrimp with quinoa and asparagus (450 kcal)
        - **Snack**: Almonds and an orange (200 kcal)
        - **Dinner**: Stir-fried tofu with broccoli and brown rice (550 kcal)

        **Total Calories per Day**: ~1550 kcal
        """

    elif goal == 'Weight Gain':
        return """
        ## Weight Gain: High-Calorie Nutrient-Dense Plan

        ### Day 1
        - **Breakfast**: Scrambled eggs with toast and peanut butter (500 kcal)
        - **Lunch**: Grilled chicken with brown rice and avocado (700 kcal)
        - **Snack**: Protein bar and banana (250 kcal)
        - **Dinner**: Beef steak with sweet potatoes and broccoli (800 kcal)

        ### Day 2
        - **Breakfast**: Oats with peanut butter and honey (550 kcal)
        - **Lunch**: Salmon with quinoa and mixed vegetables (750 kcal)
        - **Snack**: Cottage cheese with nuts (300 kcal)
        - **Dinner**: Chicken breast with mashed potatoes and asparagus (850 kcal)

        ### Day 3
        - **Breakfast**: Smoothie with almond milk, protein powder, and banana (600 kcal)
        - **Lunch**: Beef stir-fry with brown rice and vegetables (800 kcal)
        - **Snack**: Greek yogurt with granola (250 kcal)
        - **Dinner**: Grilled chicken with sweet potatoes and green beans (700 kcal)

        ### Day 4
        - **Breakfast**: Omelette with cheese and avocado (600 kcal)
        - **Lunch**: Chicken Caesar salad with dressing (750 kcal)
        - **Snack**: Trail mix with dried fruit and nuts (300 kcal)
        - **Dinner**: Salmon with quinoa and roasted vegetables (800 kcal)

        ### Day 5
        - **Breakfast**: Smoothie with oats, peanut butter, and almond milk (650 kcal)
        - **Lunch**: Grilled pork chop with potatoes and greens (750 kcal)
        - **Snack**: Protein shake and banana (350 kcal)
        - **Dinner**: Turkey meatballs with spaghetti and marinara sauce (900 kcal)

        ### Day 6
        - **Breakfast**: Pancakes with syrup and butter (700 kcal)
        - **Lunch**: Chicken sandwich with avocado and cheese (800 kcal)
        - **Snack**: Cottage cheese with pineapple (250 kcal)
        - **Dinner**: Beef steak with mashed potatoes and broccoli (850 kcal)

        ### Day 7
        - **Breakfast**: Bagel with cream cheese and smoked salmon (600 kcal)
        - **Lunch**: Tuna salad with olive oil and greens (750 kcal)
        - **Snack**: Almonds and dried apricots (300 kcal)
        - **Dinner**: Pork chops with roasted carrots and rice (850 kcal)

        **Total Calories per Day**: ~2400 kcal
        """

    elif goal == 'Muscle Gain':
        return """
        ## Muscle Gain: Protein-Rich Plan

        ### Day 1
        - **Breakfast**: Eggs with spinach, avocado, and whole wheat toast (500 kcal)
        - **Lunch**: Chicken breast with quinoa and roasted vegetables (600 kcal)
        - **Snack**: Protein shake and almonds (300 kcal)
        - **Dinner**: Beef stir-fry with brown rice and broccoli (700 kcal)

        ### Day 2
        - **Breakfast**: Scrambled eggs with oats and fruit (550 kcal)
        - **Lunch**: Tuna salad with mixed greens, olive oil dressing (650 kcal)
        - **Snack**: Greek yogurt with granola (250 kcal)
        - **Dinner**: Grilled salmon with roasted potatoes and asparagus (800 kcal)

        ### Day 3
        - **Breakfast**: Protein pancakes with syrup (600 kcal)
        - **Lunch**: Grilled chicken with rice and avocado (700 kcal)
        - **Snack**: Cottage cheese with nuts (250 kcal)
        - **Dinner**: Pork tenderloin with mashed potatoes and steamed broccoli (750 kcal)

        ### Day 4
        - **Breakfast**: Oatmeal with chia seeds and berries (500 kcal)
        - **Lunch**: Turkey breast sandwich with avocado (600 kcal)
        - **Snack**: Protein smoothie with almond milk and fruit (350 kcal)
        - **Dinner**: Stir-fried tofu with vegetables and brown rice (700 kcal)

        ### Day 5
        - **Breakfast**: Smoothie bowl with protein powder, fruits, and almond butter (550 kcal)
        - **Lunch**: Chicken with quinoa, veggies, and olive oil (700 kcal)
        - **Snack**: Hard-boiled eggs and avocado (300 kcal)
        - **Dinner**: Beef steak with sweet potatoes and spinach (750 kcal)

        ### Day 6
        - **Breakfast**: Veggie omelette with whole wheat toast (500 kcal)
        - **Lunch**: Grilled shrimp with quinoa and steamed veggies (650 kcal)
        - **Snack**: Protein bar (250 kcal)
        - **Dinner**: Grilled chicken with brown rice and mixed vegetables (800 kcal)

        ### Day 7
        - **Breakfast**: Scrambled eggs with avocado and whole wheat bread (550 kcal)
        - **Lunch**: Chicken Caesar salad with dressing (650 kcal)
        - **Snack**: Greek yogurt with granola and berries (300 kcal)
        - **Dinner**: Salmon with roasted vegetables and quinoa (750 kcal)

        **Total Calories per Day**: ~2300 kcal
        """

    else:
        return "Please select a valid fitness goal."


def main():
    st.set_page_config(page_title="Fitness AI Coach", layout="wide")
    st.title('Your Fitness AI Coach')
    st.write("Welcome to your personal Fitness AI Coach powered by computer vision!")

    feature = st.sidebar.selectbox("Choose Feature", ["Diet Plan", "BMR Calculator", "Video Mode", "WebCam Mode"])

    if feature == "Diet Plan":
        goal = st.sidebar.selectbox("Select Your Fitness Goal", ['Weight Loss', 'Weight Gain', 'Muscle Gain'])
        st.subheader(" Weekly Diet Plan")
        diet_plan = get_diet_plan(goal)
        st.markdown(diet_plan)

    elif feature == "BMR Calculator":
        st.subheader(" BMR (Basal Metabolic Rate) Calculator")
        gender = st.radio("Select Gender", ['Male', 'Female'])
        age = st.number_input("Enter Age", min_value=10, max_value=100, step=1)
        weight = st.number_input("Enter Weight (kg)", min_value=30.0, max_value=200.0, step=0.5)
        height = st.number_input("Enter Height (cm)", min_value=100.0, max_value=250.0, step=0.5)

        if st.button("Calculate BMR"):
            if gender == 'Male':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            st.success(f"Your BMR is **{bmr:.2f}** calories/day.")
            st.info("This is the number of calories your body needs at rest. Use it to plan your fitness goals!")

    elif feature == "Video Mode":
        st.subheader('📹 Upload Your Exercise Video')
        video_file = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", "avi", "m4v"])
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')

        if video_file is None:
            demo_video = 'demo.mp4'
            cap = cv2.VideoCapture(demo_video)
            temp_path = demo_video
        else:
            temp_file.write(video_file.read())
            temp_path = temp_file.name
            cap = cv2.VideoCapture(temp_path)

        st.sidebar.text('📥 Input Video')
        st.sidebar.video(temp_path)

        st.markdown("### 🔎 Input Preview")
        st.video(temp_path)

        st.markdown("###  Processed Output")
        trainer = exercise.Exercise()

        output_path = trainer.squat(cap, mode='video')

        cap.release()
        cv2.destroyAllWindows()
        time.sleep(1)

        if output_path and os.path.exists(output_path):
            st.video(output_path)
        else:
            st.error(" Failed to generate output video.")

    elif feature == "WebCam Mode":
        st.subheader('Live Webcam Exercise Detection')

        # Sidebar: Select Exercise and Set Goals
        st.sidebar.subheader("🎯 Set Your Exercise Goal")
        selected_exercise = st.sidebar.selectbox("Choose Exercise", ["Push-Up", "Squat", "Bicep Curl", "Shoulder Press"])
        target_reps = st.sidebar.number_input("Target Reps", min_value=1, max_value=100, value=10)

        st.markdown("### Correct Form Preview")
        if selected_exercise == 'Bicep Curl':
            st.video('curl_form.mp4')
        elif selected_exercise == 'Push-Up':
            st.video('push_up_form.mp4')
        elif selected_exercise == 'Squat':
            st.video('squat_form.mp4')
        elif selected_exercise == 'Shoulder Press':
            st.video('shoulder_press_form.mp4')

        # Initialize session state
        if 'current_rep' not in st.session_state:
            st.session_state.current_rep = 0
        if 'goal_reached' not in st.session_state:
            st.session_state.goal_reached = False

        stframe = st.empty()
        trainer = Exercise()

        cap = cv2.VideoCapture(0)
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        if not cap.isOpened():
            st.error("Cannot open webcam.")
            return

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                if st.session_state.goal_reached:
                    break  # Exit loop once goal is achieved

                ret, frame = cap.read()
                if not ret:
                    break

                # Flip for mirror view
                frame = cv2.flip(frame, 1)

                # Run pose estimation + exercise analysis
                if selected_exercise == "Push-Up":
                    trainer.push_up(cap, mode='webcam')
                elif selected_exercise == "Squat":
                    trainer.squat(cap, mode='webcam')
                elif selected_exercise == "Bicep Curl":
                    trainer.bicept_curl(cap, mode='webcam')
                elif selected_exercise == "Shoulder Press":
                    trainer.shoulder_press(cap, mode='webcam')

                # Assuming rep_detected is a flag that turns True when a rep is counted
                rep_detected = False  # Replace with actual rep detection logic

                # Update rep logic
                if rep_detected:
                    st.session_state.current_rep += 1

                # Display Progress
                stframe.markdown(f"""
                ### 🏋️ Exercise Progress:
                - **Exercise:** {selected_exercise}  
                - **Reps Completed:** {st.session_state.current_rep}/{target_reps}  
                """)

                # Show webcam frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(frame, channels='RGB', use_column_width=True)

                # Check if workout goal is complete
                if st.session_state.current_rep >= target_reps:
                    st.session_state.goal_reached = True
                    st.success(" Workout goal completed! Great job!")
                    break  # Stop counting once the goal is achieved

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()