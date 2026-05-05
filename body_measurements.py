import cv2
import mediapipe as mp
import math
import os

# Set up MediaPipe
mp_pose = mp.solutions.pose

# Auto-find any image file in the folder
image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
image_path = None

for file in os.listdir('.'):
    if any(file.lower().endswith(ext) for ext in image_extensions):
        if not file.startswith('result'):
            image_path = file
            break

if image_path is None:
    print("ERROR: No image file found in folder")
    exit()

print(f"Using image: {image_path}")
image = cv2.imread(image_path)

if image is None:
    print(f"ERROR: Could not load {image_path}")
    exit()

# Convert to RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Run pose detection
with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
    results = pose.process(image_rgb)

if not results.pose_landmarks:
    print("No body detected")
    exit()

# Grab all 33 landmarks
landmarks = results.pose_landmarks.landmark

# Helper function: calculate distance between two landmarks
def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

# Helper function: get midpoint between two landmarks
def midpoint(p1, p2):
    class Point:
        pass
    mid = Point()
    mid.x = (p1.x + p2.x) / 2
    mid.y = (p1.y + p2.y) / 2
    return mid

# Get key landmarks by their MediaPipe index numbers
left_shoulder = landmarks[11]
right_shoulder = landmarks[12]
left_hip = landmarks[23]
right_hip = landmarks[24]
left_elbow = landmarks[13]
left_wrist = landmarks[15]
left_knee = landmarks[25]
left_ankle = landmarks[27]
nose = landmarks[0]

# Calculate key measurements
shoulder_width = distance(left_shoulder, right_shoulder)
hip_width = distance(left_hip, right_hip)

# Torso length: midpoint of shoulders to midpoint of hips
shoulders_mid = midpoint(left_shoulder, right_shoulder)
hips_mid = midpoint(left_hip, right_hip)
torso_length = distance(shoulders_mid, hips_mid)

# Leg length: hip to ankle
leg_length = distance(left_hip, left_ankle)

# Arm length: shoulder to wrist
arm_length = distance(left_shoulder, left_wrist)

# Total height estimate: nose to ankle
total_height = distance(nose, left_ankle)

# Calculate ratios
shoulder_to_hip_ratio = shoulder_width / hip_width
torso_to_leg_ratio = torso_length / leg_length
shoulder_to_height_ratio = shoulder_width / total_height

# Classify body shape based on shoulder-to-hip ratio
if shoulder_to_hip_ratio > 1.15:
    body_shape = "Inverted Triangle (shoulders wider than hips)"
elif shoulder_to_hip_ratio < 0.95:
    body_shape = "Triangle / Pear (hips wider than shoulders)"
else:
    body_shape = "Rectangle / Athletic (shoulders and hips similar)"

# Print everything
print("=" * 50)
print("BODY MEASUREMENT ANALYSIS")
print("=" * 50)
print(f"\nRaw Measurements (normalized 0-1 scale):")
print(f"  Shoulder width:  {shoulder_width:.3f}")
print(f"  Hip width:       {hip_width:.3f}")
print(f"  Torso length:    {torso_length:.3f}")
print(f"  Leg length:      {leg_length:.3f}")
print(f"  Arm length:      {arm_length:.3f}")
print(f"  Total height:    {total_height:.3f}")

print(f"\nKey Ratios:")
print(f"  Shoulder-to-hip ratio:    {shoulder_to_hip_ratio:.2f}")
print(f"  Torso-to-leg ratio:       {torso_to_leg_ratio:.2f}")
print(f"  Shoulder-to-height ratio: {shoulder_to_height_ratio:.2f}")

print(f"\nBody Shape Classification:")
print(f"  {body_shape}")
print("=" * 50)