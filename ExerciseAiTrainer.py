"""Exercise AI Trainer Module.

This module provides exercise detection and rep counting capabilities using MediaPipe
for pose detection. It supports multiple exercises: push-ups, squats, bicep curls,
and shoulder presses in both webcam and video modes.
"""

import cv2
import PoseModule2 as pm
import numpy as np
import streamlit as st
from AiTrainer_utils import *

# Constants for exercise detection
DEFAULT_FRAME_WIDTH = 640
DEFAULT_FRAME_HEIGHT = 480
VIDEO_CODEC = 'mp4v'
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# Exercise-specific angle thresholds
PUSHUP_ARM_THRESHOLD = 130
PUSHUP_EXTENDED_THRESHOLD = 250
SQUAT_DOWN_ANGLE = 80
SQUAT_UP_ANGLE = 140
SQUAT_LEFT_THRESHOLD = 240
BICEP_DOWN_THRESHOLD = 230
BICEP_UP_THRESHOLD = 310
SHOULDER_DOWN_UPPER = 315
SHOULDER_DOWN_LOWER = 40
SHOULDER_UP_UPPER = 240
SHOULDER_UP_LOWER = 130


class Exercise:
    """Exercise detection and rep counting class.
    
    This class handles exercise detection using pose landmarks and provides
    rep counting for various exercises.
    """
    
    def __init__(self):
        """Initialize the Exercise detector."""
        pass

    def visualize_angle(self, img, angle, landmark):
        """Display angle value on image at landmark position.
        
        Args:
            img: Input image to draw on
            angle: Joint angle in degrees
            landmark: Landmark coordinates (x, y)
        """
        cv2.putText(img, str(angle),
                    tuple(np.multiply(landmark, [DEFAULT_FRAME_WIDTH, DEFAULT_FRAME_HEIGHT]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    def repetitions_counter(self, img, counter):
        """Display rep counter on image.
        
        Args:
            img: Input image to draw on
            counter: Current rep count
        """
        cv2.rectangle(img, (0, 0), (225, 73), (245, 117, 16), -1)
        cv2.putText(img, 'REPS', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img, str(counter),
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

    def push_up(self, cap, mode='webcam'):
        """Detect push-ups and count repetitions.
        
        Args:
            cap: Video capture object
            mode: 'webcam' or 'video' mode
            
        Returns:
            str: Path to output video (video mode only)
        """
        counter = 0
        stage = None
        detector = pm.posture_detector()

        if mode == 'webcam':
            stframe = st.empty()

        if mode == 'video':
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            out_path = 'output_pushup.mp4'
            out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*VIDEO_CODEC), fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            img = detector.find_person(frame)
            landmark_list = detector.find_landmarks(img, False)
            
            # Only process if landmarks detected
            if landmark_list and len(landmark_list) > 0:
                right_arm_angle = detector.find_angle(img, 12, 14, 16)
                right_elbow = landmark_list[14][1:]
                self.visualize_angle(img, right_arm_angle, right_elbow)

                right_shoulder = landmark_list[12][1:]
                right_wrist = landmark_list[16][1:]

                if distanceCalculate(right_shoulder, right_wrist) < PUSHUP_ARM_THRESHOLD:
                    stage = "down"
                if distanceCalculate(right_shoulder, right_wrist) > PUSHUP_EXTENDED_THRESHOLD and stage == "down":
                    stage = "up"
                    counter += 1

            self.repetitions_counter(img, counter)

            if mode == 'webcam':
                img = image_resize(image=img, width=640)
                stframe.image(img, channels='BGR', use_container_width=True)
            else:
                out.write(img)

        cap.release()
        if mode == 'video':
            out.release()
            return out_path
        cv2.destroyAllWindows()

    def squat(self, cap, mode='webcam'):
        """Detect squats and count repetitions.
        
        Args:
            cap: Video capture object
            mode: 'webcam' or 'video' mode
            
        Returns:
            str: Path to output video (video mode only)
        """
        counter = 0
        stage = None
        detector = pm.posture_detector()

        if mode == 'webcam':
            stframe = st.empty()

        if mode == 'video':
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            out_path = 'output_squat.mp4'
            out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*VIDEO_CODEC), fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            img = detector.find_person(frame)
            landmark_list = detector.find_landmarks(img, False)
            
            # Only process if landmarks detected
            if landmark_list and len(landmark_list) > 0:
                right_leg_angle = detector.find_angle(img, 24, 26, 28)
                left_leg_angle = detector.find_angle(img, 23, 25, 27)
                right_knee = landmark_list[26][1:]
                self.visualize_angle(img, right_leg_angle, right_knee)

                if right_leg_angle > SQUAT_UP_ANGLE and left_leg_angle < SQUAT_LEFT_THRESHOLD:
                    stage = "down"
                if right_leg_angle < SQUAT_DOWN_ANGLE and left_leg_angle > 270 and stage == 'down':
                    stage = "up"
                    counter += 1

            self.repetitions_counter(img, counter)

            if mode == 'webcam':
                img = image_resize(image=img, width=640)
                stframe.image(img, channels='BGR', use_container_width=True)
            else:
                out.write(img)

        cap.release()
        if mode == 'video':
            out.release()
            return out_path
        cv2.destroyAllWindows()

    def bicep_curl(self, cap, mode='webcam'):
        """Detect bicep curls and count repetitions.
        
        Args:
            cap: Video capture object
            mode: 'webcam' or 'video' mode
            
        Returns:
            str: Path to output video (video mode only)
        """
        counter = 0
        stage = None
        detector = pm.posture_detector()

        if mode == 'webcam':
            stframe = st.empty()

        if mode == 'video':
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            out_path = 'output_bicep.mp4'
            out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*VIDEO_CODEC), fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            img = detector.find_person(frame)
            landmark_list = detector.find_landmarks(img, False)
            
            # Only process if landmarks detected
            if landmark_list and len(landmark_list) > 0:
                right_arm_angle = detector.find_angle(img, 12, 14, 16)
                left_arm_angle = detector.find_angle(img, 11, 13, 15)
                right_elbow = landmark_list[14][1:]
                self.visualize_angle(img, right_arm_angle, right_elbow)

                if left_arm_angle < BICEP_DOWN_THRESHOLD:
                    stage = "down"
                if left_arm_angle > BICEP_UP_THRESHOLD and stage == 'down':
                    stage = "up"
                    counter += 1

            self.repetitions_counter(img, counter)

            if mode == 'webcam':
                img = image_resize(image=img, width=640)
                stframe.image(img, channels='BGR', use_container_width=True)
            else:
                out.write(img)

        cap.release()
        if mode == 'video':
            out.release()
            return out_path
        cv2.destroyAllWindows()

    def shoulder_press(self, cap, mode='webcam'):
        """Detect shoulder presses and count repetitions.
        
        Args:
            cap: Video capture object
            mode: 'webcam' or 'video' mode
            
        Returns:
            str: Path to output video (video mode only)
        """
        counter = 0
        stage = None
        detector = pm.posture_detector()

        if mode == 'webcam':
            stframe = st.empty()

        if mode == 'video':
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            out_path = 'output_shoulder.mp4'
            out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*VIDEO_CODEC), fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            img = detector.find_person(frame)
            landmark_list = detector.find_landmarks(img, False)
            
            # Only process if landmarks detected
            if landmark_list and len(landmark_list) > 0:
                right_arm_angle = detector.find_angle(img, 12, 14, 16)
                left_arm_angle = detector.find_angle(img, 11, 13, 15)
                right_elbow = landmark_list[14][1:]
                self.visualize_angle(img, right_arm_angle, right_elbow)

                if right_arm_angle > SHOULDER_DOWN_UPPER and left_arm_angle < SHOULDER_DOWN_LOWER:
                    stage = "down"
                if right_arm_angle < SHOULDER_UP_UPPER and left_arm_angle > SHOULDER_UP_LOWER and stage == 'down':
                    stage = "up"
                    counter += 1

            self.repetitions_counter(img, counter)

            if mode == 'webcam':
                img = image_resize(image=img, width=640)
                stframe.image(img, channels='BGR', use_container_width=True)
            else:
                out.write(img)

        cap.release()
        if mode == 'video':
            out.release()
            return out_path
        cv2.destroyAllWindows()