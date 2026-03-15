import cv2
import mediapipe as mp
import numpy as np
import io

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# We will need the pose landmarker model. But since we might not have it locally
# for this quick takehome, let's fall back to trying direct solutions if they exist
# wait, my previous check of `mp` dir showed solutions wasn't there at root.
# Let's import it properly. Sometimes it's nested.
import mediapipe.python.solutions.pose as mp_pose

def calculate_distance(p1, p2):
    """Calculates 3D Euclidean distance between two landmarks."""
    return np.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

def extract_measurements(image_bytes: bytes, reference_height_cm: float = 170.0) -> dict:
    """
    Extract body measurements from an image.
    Uses MediaPipe's pose_world_landmarks which estimates real-world 3D coordinates in meters.
    We normalize these measurements against a known/estimated height to get accurate cm values.
    """
    # Load image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Could not decode image.")

    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(image_rgb)

        if not results.pose_world_landmarks:
            raise ValueError("No human pose detected in the image.")

        landmarks = results.pose_world_landmarks.landmark

        # MediaPipe Landmarks:
        # 0: nose
        # 11: left shoulder, 12: right shoulder
        # 23: left hip, 24: right hip
        # 27: left ankle, 28: right ankle
        
        # Calculate raw 3D distances (MediaPipe outputs these roughly in meters)
        # However, because scale is ambiguous, we scale everything based on the reference height
        
        # 1. Estimate Height (Nose to average of ankles)
        mid_ankle_x = (landmarks[27].x + landmarks[28].x) / 2
        mid_ankle_y = (landmarks[27].y + landmarks[28].y) / 2
        mid_ankle_z = (landmarks[27].z + landmarks[28].z) / 2
        
        class MockLandmark:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z
                
        mid_ankle = MockLandmark(mid_ankle_x, mid_ankle_y, mid_ankle_z)
        
        raw_height = calculate_distance(landmarks[0], mid_ankle)

        # 2. Scale factor: desired height / raw height
        # (Converting raw meters to desired cm scale)
        scale_factor = reference_height_cm / raw_height

        # 3. Shoulder Width (Distance between shoulders)
        raw_shoulder_width = calculate_distance(landmarks[11], landmarks[12])
        shoulder_width_cm = raw_shoulder_width * scale_factor

        # 4. Hips (Distance between hips)
        raw_hip_width = calculate_distance(landmarks[23], landmarks[24])
        # Hips circumference is roughly an ellipse. We estimate width.
        # A simple estimation: hips circumference ~ 2.5 * frontal width
        hip_width_cm = raw_hip_width * scale_factor
        hips_cm = hip_width_cm * 2.5 

        # 5. Waist
        # MediaPipe doesn't have a waist landmark. 
        # We can interpolate it as the midpoint between shoulders and hips
        waist_width_cm = ((shoulder_width_cm + hip_width_cm) / 2) * 0.85 # Slight taper
        waist_cm = waist_width_cm * 2.5

        # 6. Chest
        # A bit below the shoulders
        chest_width_cm = shoulder_width_cm * 0.95
        chest_cm = chest_width_cm * 2.5

    return {
        "height_cm": round(reference_height_cm, 1),
        "shoulder_width_cm": round(shoulder_width_cm, 1),
        "chest_cm": round(chest_cm, 1),
        "waist_cm": round(waist_cm, 1),
        "hips_cm": round(hips_cm, 1)
    }
