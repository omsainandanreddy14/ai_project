"""Pose Detection Module using MediaPipe.

This module provides pose detection and analysis capabilities using MediaPipe's
Pose solution. It can detect 33 body landmarks and calculate angles between joints.
"""

import mediapipe as mp
import math
import cv2
import time


class posture_detector:
    """Pose detection class using MediaPipe.
    
    This class detects human pose landmarks in images/videos and can calculate
    joint angles for exercise analysis.
    """
    
    def __init__(self, mode=False, up_body=1, smooth=True,
                 detection_con=0.5, track_con=0.5):
        """Initialize pose detector.
        
        Args:
            mode (bool): Whether to use static image mode
            up_body (int): Whether to detect full body or upper body only
            smooth (bool): Whether to apply smoothing
            detection_con (float): Detection confidence threshold
            track_con (float): Tracking confidence threshold
        """
        self.mode = mode
        self.up_body = up_body
        self.smooth = smooth
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(self.mode, self.up_body, self.smooth,
                                     min_detection_confidence=self.detection_con, min_tracking_confidence= self.track_con)
    def find_person(self, img, draw=True):
        """Detect pose landmarks in image.
        
        Args:
            img: Input image (BGR format)
            draw (bool): Whether to draw landmarks on image
            
        Returns:
            Image with landmarks drawn (if draw=True)
        """
        # Recolor image to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)

        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(
                img, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return img

    def find_landmarks(self, img, draw=True):
        """Extract landmark coordinates from detected pose.
        
        Args:
            img: Input image
            draw (bool): Whether to draw circles on landmarks
            
        Returns:
            list: List of [id, x, y] for each landmark, or empty list if no pose detected
        """
        self.landmark_list = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.landmark_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        
        return self.landmark_list if self.landmark_list else []

    def find_angle(self, img, p1, p2, p3, draw=True):
        """Calculate angle formed by three landmarks.
        
        Args:
            img: Input image to draw on
            p1, p2, p3: Landmark indices forming the angle (p2 is vertex)
            draw (bool): Whether to draw angle visualization
            
        Returns:
            float: Angle in degrees (0-360)
        """
        # Get the landmarks
        x1, y1 = self.landmark_list[p1][1:]
        x2, y2 = self.landmark_list[p2][1:]
        x3, y3 = self.landmark_list[p3][1:]
        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360


        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 5)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 5)
            cv2.circle(img, (x1, y1), 11, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 16, (255, 60, 0), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 16, (255, 60, 0), 2)
            cv2.circle(img, (x3, y3), 11, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 16, (255, 60, 0), 2)

            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 60),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1)
        return angle

    def find_coordinate(self):
        pass
def main():
    cap = cv2.VideoCapture(0)
    detector = posture_detector()
    while True:
        ret, frame = cap.read()

        pTime = 0

        img = detector.find_person(frame)
        landmark_list = detector.find_landmarks(img, draw=True)
        # angle = detector.find_angle(img, 16, 14, 12)
       # print(landmark_list)
        if len(landmark_list) != 0:

            cv2.circle(
                img, (landmark_list[14][1], landmark_list[14][2]), 15, (0, 0, 255), cv2.FILLED)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()