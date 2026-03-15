import numpy as np
import io

def calculate_distance(p1, p2):
    return np.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

def extract_measurements(image_bytes: bytes, reference_height_cm: float = 170.0) -> dict:
    
    # Lazy imports (VERY IMPORTANT)
    import cv2
    import mediapipe as mp

    mp_pose = mp.solutions.pose

    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image.")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(image_rgb)

        if not results.pose_world_landmarks:
            raise ValueError("No human pose detected.")

        landmarks = results.pose_world_landmarks.landmark

        # Height estimation
        mid_ankle_x = (landmarks[27].x + landmarks[28].x) / 2
        mid_ankle_y = (landmarks[27].y + landmarks[28].y) / 2
        mid_ankle_z = (landmarks[27].z + landmarks[28].z) / 2

        class Mock:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z

        mid_ankle = Mock(mid_ankle_x, mid_ankle_y, mid_ankle_z)

        raw_height = calculate_distance(landmarks[0], mid_ankle)

        scale_factor = reference_height_cm / raw_height

        raw_shoulder = calculate_distance(landmarks[11], landmarks[12])
        shoulder_width_cm = raw_shoulder * scale_factor

        raw_hip = calculate_distance(landmarks[23], landmarks[24])
        hip_width_cm = raw_hip * scale_factor

        hips_cm = hip_width_cm * 2.5
        chest_cm = shoulder_width_cm * 2.4
        waist_cm = hip_width_cm * 2.2

    return {
        "height_cm": round(reference_height_cm, 1),
        "shoulder_width_cm": round(shoulder_width_cm, 1),
        "chest_cm": round(chest_cm, 1),
        "waist_cm": round(waist_cm, 1),
        "hips_cm": round(hips_cm, 1)
    }
