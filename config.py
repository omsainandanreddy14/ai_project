"""
Configuration file for Fitness AI Coach
Contains all adjustable parameters and settings
"""

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_NAME = "Fitness AI Coach"
APP_VERSION = "2.0"
PAGE_TITLE = "Fitness AI Coach"
PAGE_LAYOUT = "wide"

# ============================================================================
# STYLING & COLORS
# ============================================================================

COLORS = {
    "primary": "#FF6B35",           # Orange - Action buttons
    "secondary": "#004E89",         # Deep Blue - Info
    "success": "#1ECB7F",           # Green - Success messages
    "warning": "#FFB703",           # Yellow - Warnings
    "danger": "#E63946",            # Red - Errors
    "background": "#f0f2f6",        # Light gray
    "text": "#333333",              # Dark text
    "text_light": "#666666",        # Light text
}

FONT_SIZES = {
    "title": "48px",
    "heading2": "32px",
    "heading3": "24px",
    "body": "16px",
    "small": "14px",
    "code": "12px",
}

# ============================================================================
# VIDEO & PROCESSING SETTINGS
# ============================================================================

DEFAULT_FRAME_WIDTH = 640
DEFAULT_FRAME_HEIGHT = 480
DEFAULT_FPS = 30
VIDEO_CODEC = 'mp4v'

# Supported video formats
SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "m4v"]

# Maximum file size (in MB)
MAX_VIDEO_SIZE_MB = 500
MAX_FRAME_PROCESSING_TIME = 0.1  # seconds

# ============================================================================
# POSE DETECTION SETTINGS
# ============================================================================

# MediaPipe confidence thresholds
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# Number of body landmarks detected
NUM_POSE_LANDMARKS = 33

# Landmark indices for exercises
LANDMARKS = {
    "nose": 0,
    "left_eye": 2,
    "right_eye": 5,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}

# ============================================================================
# EXERCISE THRESHOLDS (All values in pixels/degrees)
# ============================================================================

EXERCISE_CONFIG = {
    "Push-Up": {
        "arm_threshold_down": 130,        # Distance for down position
        "arm_threshold_up": 250,          # Distance for up position
        "rep_key": "distance",
        "joints": ["shoulder", "elbow", "wrist"],
        "difficulty": "Intermediate",
    },
    "Squat": {
        "down_angle": 80,                 # Knee angle at bottom
        "up_angle": 140,                  # Knee angle at top
        "hip_threshold": 240,             # Hip angle threshold
        "rep_key": "angles",
        "joints": ["hip", "knee", "ankle"],
        "difficulty": "Beginner",
    },
    "Bicep Curl": {
        "down_threshold": 230,            # Arm angle at bottom
        "up_threshold": 310,              # Arm angle at top
        "rep_key": "angle",
        "joints": ["shoulder", "elbow", "wrist"],
        "difficulty": "Beginner",
    },
    "Shoulder Press": {
        "down_upper": 315,                # Right arm down threshold
        "down_lower": 40,                 # Left arm down threshold
        "up_upper": 240,                  # Right arm up threshold
        "up_lower": 130,                  # Left arm up threshold
        "rep_key": "angles",
        "joints": ["shoulder", "elbow", "wrist"],
        "difficulty": "Intermediate",
    }
}

# ============================================================================
# BMR CALCULATOR SETTINGS
# ============================================================================

BMR_EQUATIONS = {
    "male": lambda age, weight, height: 10*weight + 6.25*height - 5*age + 5,
    "female": lambda age, weight, height: 10*weight + 6.25*height - 5*age - 161,
}

ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,                   # Little or no exercise
    "Lightly Active": 1.375,            # Light exercise 1-3 days/week
    "Moderately Active": 1.55,          # Moderate exercise 3-5 days/week
    "Very Active": 1.725,               # Hard exercise 6-7 days/week
    "Extremely Active": 1.9,            # Physical job or very hard exercise
}

CALORIE_ADJUSTMENTS = {
    "weight_loss": -500,                # cal/day deficit
    "maintenance": 0,                   # no adjustment
    "muscle_gain": 300,                 # cal/day surplus
}

# ============================================================================
# DIET PLAN GENERATOR SETTINGS
# ============================================================================

DIET_TYPES = [
    "Vegetarian",
    "Vegan",
    "Non-Vegetarian",
    "Keto",
    "High-Protein",
    "Diabetic Friendly",
    "Mediterranean",
]

ACTIVITY_LEVELS = [
    "Sedentary",
    "Lightly Active",
    "Moderately Active",
    "Very Active",
    "Extremely Active",
]

FITNESS_GOALS = [
    "Weight Loss",
    "Muscle Gain",
    "Maintenance",
    "Endurance",
]

MEALS_PER_DAY_OPTIONS = [2, 3, 4, 5, 6]

# Macro nutrient ratios for different goals
MACROS_RATIOS = {
    "Weight Loss": {"protein": 0.40, "carbs": 0.40, "fats": 0.20},
    "Muscle Gain": {"protein": 0.35, "carbs": 0.45, "fats": 0.20},
    "Maintenance": {"protein": 0.30, "carbs": 0.50, "fats": 0.20},
    "Endurance": {"protein": 0.20, "carbs": 0.65, "fats": 0.15},
}

# ============================================================================
# API SETTINGS
# ============================================================================

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_TIMEOUT = 30  # seconds
GEMINI_MAX_RETRIES = 3

# ============================================================================
# FILE PATHS
# ============================================================================

DEMO_VIDEO_PATH = "demo.mp4"

FORM_VIDEO_PATHS = {
    "Bicep Curl": "curl_form.mp4",
    "Push-Up": "push_up_form.mp4",
    "Squat": "squat_form.mp4",
    "Shoulder Press": "shoulder_press_form.mp4",
}

OUTPUT_VIDEO_PATHS = {
    "Push-Up": "output_pushup.mp4",
    "Squat": "output_squat.mp4",
    "Bicep Curl": "output_bicep.mp4",
    "Shoulder Press": "output_shoulder.mp4",
}

# ============================================================================
# WEBCAM MODE SETTINGS
# ============================================================================

MAX_FRAMES_PER_SESSION = 5000  # Safety limit to prevent infinite loops
FRAME_DISPLAY_DELAY = 0.02     # seconds
REP_COUNTER_COLOR = (255, 107, 53)  # BGR format (Orange)
STATUS_BOX_COLOR = (255, 107, 53)   # BGR format
REP_COUNTER_POSITION = (0, 0)
REP_COUNTER_SIZE = (250, 100)

EXERCISE_TIPS = {
    "Push-Up": [
        "✓ Keep body straight from head to heels",
        "✓ Lower chest until it nearly touches floor",
        "✓ Push back up to starting position",
        "✓ Maintain control throughout movement",
        "✓ Don't let hips sag or stick up",
    ],
    "Squat": [
        "✓ Feet shoulder-width apart",
        "✓ Chest up, core engaged",
        "✓ Lower until thighs are parallel to ground",
        "✓ Drive through heels to stand up",
        "✓ Keep knees aligned with toes",
    ],
    "Bicep Curl": [
        "✓ Keep elbows fixed at sides",
        "✓ Curl weights toward shoulders",
        "✓ Lower with control",
        "✓ No swinging motion",
        "✓ Full range of motion",
    ],
    "Shoulder Press": [
        "✓ Feet shoulder-width apart",
        "✓ Press weights overhead",
        "✓ Extend arms fully at top",
        "✓ Lower back to shoulders",
        "✓ Keep core tight",
    ],
}

# ============================================================================
# UI TEXT STRINGS
# ============================================================================

MESSAGES = {
    "loading": "🔄 Processing... This may take a moment.",
    "success": "✅ Operation completed successfully!",
    "error": "❌ An error occurred. Please try again.",
    "warning": "⚠️ Warning: ",
    "info": "ℹ️ Info: ",
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Image resizing
IMAGE_RESIZE_WIDTH = 640
IMAGE_RESIZE_INTERPOLATION = "INTER_AREA"

# Batch processing size
BATCH_SIZE = 32

# Cache settings (Streamlit)
CACHE_TTL = 300  # seconds

# ============================================================================
# VALIDATION RANGES
# ============================================================================

VALIDATION_RANGES = {
    "age": (10, 100),
    "weight": (30, 200),            # kg
    "height": (100, 250),           # cm
    "target_reps": (1, 100),
    "video_frame_rate": (15, 60),   # fps
}

# ============================================================================
# MAGIC NUMBERS & CONSTANTS
# ============================================================================

CONFIDENCE_THRESHOLD = 0.5
LANDMARK_CIRCLE_RADIUS = 5
ANGLE_LINE_THICKNESS = 5
FONT_THICKNESS = 2
FONT_SCALE = 0.5

# ============================================================================
# DEBUG MODE
# ============================================================================

DEBUG_MODE = False  # Set to True for verbose logging
SHOW_LANDMARKS = True  # Show pose landmarks in output
SHOW_ANGLES = True  # Show angle calculations
SHOW_FPS = False  # Show FPS counter

# ============================================================================
# ENVIRONMENT & SYSTEM
# ============================================================================

SUPPORTED_OS = ["Windows", "Darwin", "Linux"]  # Windows, macOS, Linux
MIN_PYTHON_VERSION = (3, 8)
MIN_RAM_MB = 1024  # 1GB minimum

# End of Configuration
