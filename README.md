# 🏋️ Fitness AI Coach

A powerful Streamlit-based fitness coaching application that uses computer vision and AI to help users achieve their fitness goals.

## Features

- **BMR Calculator**: Calculate your Basal Metabolic Rate (daily calorie needs at rest)
- **Video Analysis**: Upload exercise videos to get real-time form analysis and rep counting
- **Webcam Mode**: Real-time exercise detection with live feedback and rep counting
- **Diet Plan Generator**: Personalized nutrition plans powered by Google Gemini AI
- **Multiple Exercises**: Push-ups, Squats, Bicep Curls, and Shoulder Presses

## Prerequisites

- Python 3.8 or higher
- Webcam (for webcam mode)
- Gemini API key (for diet plan generation) - [Get one here](https://ai.google.dev/)

## Installation

### 1. Clone or download the project
```bash
cd Fitness-AI-coach-main
```

### 2. Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirement.txt
```

## Usage

### Running the Application

```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

### Features Guide

#### 1. BMR Calculator
- Select your gender, age, weight, and height
- Get your daily calorie requirements
- Use this to plan your fitness and nutrition goals

#### 2. Video Mode
- Upload an exercise video (MP4, MOV, AVI, M4V)
- Select the exercise type
- The app will analyze the video and count repetitions
- Output video shows analysis with rep counter

#### 3. Webcam Mode
- Select your exercise and target reps
- View the correct form preview
- Click "Start Exercise" to begin
- Real-time feedback shows your current reps
- Balloons appear when you reach your goal!

#### 4. Diet Plan Generator
- Enter your Gemini API key (keep it private!)
- Fill in your personal details
- Select diet preferences (Vegetarian, Keto, etc.)
- Get a personalized nutrition plan

## Project Structure

```
Fitness-AI-coach-main/
├── main.py                  # Main Streamlit application
├── ExerciseAiTrainer.py     # Exercise detection and rep counting
├── PoseModule2.py           # MediaPipe pose detection wrapper
├── AiTrainer_utils.py       # Utility functions
├── requirement.txt          # Python dependencies
└── README.md               # This file
```

## How It Works

### Computer Vision Pipeline

1. **Pose Detection**: Uses MediaPipe to detect 33 body landmarks in real-time
2. **Angle Calculation**: Calculates joint angles from detected landmarks
3. **Rep Counting**: Uses threshold-based state machine to count repetitions
4. **Visualization**: Overlays angle values and rep counter on the video

### Exercise Detection

Each exercise has specific angle thresholds:

- **Push-up**: Measures shoulder-to-wrist distance
- **Squat**: Measures knee angles for down/up positions
- **Bicep Curl**: Measures elbow angle during curl motion
- **Shoulder Press**: Measures arm angles during press motion

## Configuration

### Adjusting Detection Parameters

Edit `ExerciseAiTrainer.py` to modify angle thresholds:

```python
# Example: Adjust squat sensitivity
SQUAT_DOWN_ANGLE = 80      # Lower value = stricter form
SQUAT_UP_ANGLE = 140       # Higher value = needs more extension
```

### API Key Setup

For diet plan generation, set up your Gemini API key:

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create a new API key
3. Enter it in the app when prompted (no need to hardcode it)

## Troubleshooting

### Webcam Not Working
- Check camera permissions in your OS settings
- Try allowing the app in firewall settings
- Restart the app

### Poor Rep Detection
- Ensure good lighting in your environment
- Position yourself fully in frame
- Move smoothly and maintain proper form
- Adjust angle thresholds if needed

### Video Processing Fails
- Ensure video codec is compatible (MP4 recommended)
- Check file isn't corrupted
- Try a shorter video first

### API Key Issues
- Ensure key is valid and has proper permissions
- Check your internet connection
- Verify quota limits on Google Cloud

## Performance Tips

1. **Lighting**: Good lighting improves pose detection accuracy
2. **Distance**: Stay 1-2 meters away from webcam
3. **Background**: Plain backgrounds work better
4. **Frame Rate**: 30 FPS is optimal
5. **Resolution**: 720p or higher recommended

## Future Enhancements

- [ ] Add more exercises (Deadlifts, Pull-ups, etc.)
- [ ] Integrate progress tracking and history
- [ ] Add workout scheduling
- [ ] Cloud-based rep statistics
- [ ] Mobile app version
- [ ] Form feedback alerts
- [ ] Custom exercise detection

## Technical Stack

- **Frontend**: Streamlit
- **Computer Vision**: OpenCV, MediaPipe
- **AI/ML**: Google Generative AI (Gemini)
- **Backend**: Python 3.8+

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## Support

For issues or questions:
1. Check this README first
2. Review the code comments
3. Check the Streamlit documentation
4. Create an issue in the repository

## Disclaimer

This application is designed for fitness tracking and education. Always consult with a healthcare provider before starting new exercise routines. Improper form can lead to injury - use this app as a guide, not a substitute for professional coaching.

---

**Made with ❤️ for fitness enthusiasts everywhere**
