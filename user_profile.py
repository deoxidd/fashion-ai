import cv2
import mediapipe as mp
import numpy as np
import math
import os
import json
from datetime import datetime

# Set up MediaPipe
mp_pose = mp.solutions.pose

# Auto-find image
image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
image_path = None

for file in os.listdir('.'):
    if any(file.lower().endswith(ext) for ext in image_extensions):
        if not file.startswith('result') and not file.startswith('skin_sample') and not file.startswith('profile'):
            image_path = file
            break

if image_path is None:
    print("ERROR: No image file found")
    exit()

print(f"Analyzing: {image_path}")
print("Running full body + skin analysis...\n")

image = cv2.imread(image_path)
if image is None:
    print(f"ERROR: Could not load {image_path}")
    exit()

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
height, width = image.shape[:2]

# Run pose detection
with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
    results = pose.process(image_rgb)

if not results.pose_landmarks:
    print("No body detected")
    exit()

landmarks = results.pose_landmarks.landmark

# ============== BODY MEASUREMENTS ==============

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

class Point:
    pass

def midpoint(p1, p2):
    m = Point()
    m.x = (p1.x + p2.x) / 2
    m.y = (p1.y + p2.y) / 2
    return m

# Key landmarks
left_shoulder = landmarks[11]
right_shoulder = landmarks[12]
left_hip = landmarks[23]
right_hip = landmarks[24]
left_wrist = landmarks[15]
left_ankle = landmarks[27]
nose = landmarks[0]
mouth_left = landmarks[9]
mouth_right = landmarks[10]

# Measurements
shoulder_width = distance(left_shoulder, right_shoulder)
hip_width = distance(left_hip, right_hip)
torso_length = distance(midpoint(left_shoulder, right_shoulder), midpoint(left_hip, right_hip))
leg_length = distance(left_hip, left_ankle)
arm_length = distance(left_shoulder, left_wrist)
total_height = distance(nose, left_ankle)

# Ratios
shoulder_to_hip_ratio = shoulder_width / hip_width
torso_to_leg_ratio = torso_length / leg_length
shoulder_to_height_ratio = shoulder_width / total_height

# Body shape
if shoulder_to_hip_ratio > 1.15:
    body_shape = "Inverted Triangle"
    body_shape_desc = "Shoulders wider than hips"
elif shoulder_to_hip_ratio < 0.95:
    body_shape = "Triangle"
    body_shape_desc = "Hips wider than shoulders"
else:
    body_shape = "Rectangle"
    body_shape_desc = "Shoulders and hips similar width"

# Proportion type
if torso_to_leg_ratio < 0.70:
    proportion = "Long-legged"
elif torso_to_leg_ratio > 0.85:
    proportion = "Long-torso"
else:
    proportion = "Balanced"

# ============== SKIN TONE ==============

neck_center = Point()
neck_center.x = (left_shoulder.x + right_shoulder.x) / 2
mouth_y = (mouth_left.y + mouth_right.y) / 2
shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
neck_center.y = mouth_y + (shoulder_y - mouth_y) * 0.4

neck_left = Point()
neck_left.x = neck_center.x - 0.03
neck_left.y = neck_center.y

neck_right = Point()
neck_right.x = neck_center.x + 0.03
neck_right.y = neck_center.y

def get_skin_sample(landmark):
    x = int(landmark.x * width)
    y = int(landmark.y * height)
    patch_size = 12
    x1, y1 = max(0, x - patch_size), max(0, y - patch_size)
    x2, y2 = min(width, x + patch_size), min(height, y + patch_size)
    patch = image_rgb[y1:y2, x1:x2]
    return np.mean(patch, axis=(0, 1))

left_color = get_skin_sample(neck_left)
center_color = get_skin_sample(neck_center)
right_color = get_skin_sample(neck_right)
avg_skin_rgb = (left_color + center_color + right_color) / 3

rgb_pixel = np.uint8([[avg_skin_rgb]])
lab_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2LAB)[0][0]
L, a, b = lab_pixel

if L < 80:
    depth = "Deep"
elif L < 130:
    depth = "Medium"
elif L < 180:
    depth = "Light-Medium"
else:
    depth = "Light"

warm_score = b - 128
cool_score = a - 128

if warm_score > cool_score + 3:
    undertone = "Warm"
elif cool_score > warm_score + 3:
    undertone = "Cool"
else:
    undertone = "Neutral"

# ============== BUILD PROFILE ==============

profile = {
    "generated_at": datetime.now().isoformat(),
    "source_image": image_path,
    "body": {
        "shape": body_shape,
        "shape_description": body_shape_desc,
        "proportion": proportion,
        "measurements_normalized": {
            "shoulder_width": round(float(shoulder_width), 3),
            "hip_width": round(float(hip_width), 3),
            "torso_length": round(float(torso_length), 3),
            "leg_length": round(float(leg_length), 3),
            "arm_length": round(float(arm_length), 3),
            "total_height": round(float(total_height), 3),
        },
        "ratios": {
            "shoulder_to_hip": round(float(shoulder_to_hip_ratio), 2),
            "torso_to_leg": round(float(torso_to_leg_ratio), 2),
            "shoulder_to_height": round(float(shoulder_to_height_ratio), 2),
        }
    },
    "skin": {
        "depth": depth,
        "undertone": undertone,
        "rgb": [int(avg_skin_rgb[0]), int(avg_skin_rgb[1]), int(avg_skin_rgb[2])],
        "lab": [int(L), int(a), int(b)]
    }
}

# Save as JSON (machine-readable, used by recommendation engine)
with open("profile.json", "w") as f:
    json.dump(profile, f, indent=2)

# Print summary
print("=" * 55)
print("USER STYLE PROFILE")
print("=" * 55)
print(f"\n📐 BODY")
print(f"   Shape:        {body_shape} ({body_shape_desc})")
print(f"   Proportion:   {proportion}")
print(f"   Shoulder:Hip: {shoulder_to_hip_ratio:.2f}")
print(f"\n🎨 SKIN")
print(f"   Depth:        {depth}")
print(f"   Undertone:    {undertone}")
print(f"   RGB:          ({int(avg_skin_rgb[0])}, {int(avg_skin_rgb[1])}, {int(avg_skin_rgb[2])})")
print("\n" + "=" * 55)
print("✓ Profile saved to profile.json")
print("=" * 55)