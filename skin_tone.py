import cv2
import mediapipe as mp
import numpy as np
import os

mp_pose = mp.solutions.pose

image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
image_path = None

for file in os.listdir('.'):
    if any(file.lower().endswith(ext) for ext in image_extensions):
        if not file.startswith('result') and not file.startswith('skin_sample'):
            image_path = file
            break

if image_path is None:
    print("ERROR: No image file found")
    exit()

print(f"Using image: {image_path}")
image = cv2.imread(image_path)

if image is None:
    print(f"ERROR: Could not load {image_path}")
    exit()

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
height, width = image.shape[:2]

with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
    results = pose.process(image_rgb)

if not results.pose_landmarks:
    print("No body detected")
    exit()

landmarks = results.pose_landmarks.landmark

# Neck sampling: between mouth and shoulders
mouth_left = landmarks[9]
mouth_right = landmarks[10]
left_shoulder = landmarks[11]
right_shoulder = landmarks[12]

# Neck center: horizontal midpoint between shoulders,
# vertical midpoint between mouth and shoulders
class Point:
    pass

neck_center = Point()
neck_center.x = (left_shoulder.x + right_shoulder.x) / 2
mouth_y = (mouth_left.y + mouth_right.y) / 2
shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
# Sample at 40% down from mouth to shoulder (lower neck, more skin showing)
neck_center.y = mouth_y + (shoulder_y - mouth_y) * 0.4

# Also sample two points to average
neck_left = Point()
neck_left.x = neck_center.x - 0.03  # slightly left
neck_left.y = neck_center.y

neck_right = Point()
neck_right.x = neck_center.x + 0.03  # slightly right
neck_right.y = neck_center.y

def get_skin_sample(landmark, label):
    x = int(landmark.x * width)
    y = int(landmark.y * height)
    
    patch_size = 12
    x1 = max(0, x - patch_size)
    y1 = max(0, y - patch_size)
    x2 = min(width, x + patch_size)
    y2 = min(height, y + patch_size)
    
    patch = image_rgb[y1:y2, x1:x2]
    avg_color = np.mean(patch, axis=(0, 1))
    
    print(f"  {label} sample at ({x},{y}): RGB({int(avg_color[0])},{int(avg_color[1])},{int(avg_color[2])})")
    return avg_color, (x1, y1, x2, y2)

print("\nSampling skin from neck region:")
left_color, left_box = get_skin_sample(neck_left, "Neck left")
center_color, center_box = get_skin_sample(neck_center, "Neck center")
right_color, right_box = get_skin_sample(neck_right, "Neck right")

# Average all three samples
avg_skin_rgb = (left_color + center_color + right_color) / 3

# Convert to LAB
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
    undertone_desc = "golden, yellow, or peachy undertones"
elif cool_score > warm_score + 3:
    undertone = "Cool"
    undertone_desc = "pink, red, or blue undertones"
else:
    undertone = "Neutral"
    undertone_desc = "balanced mix of warm and cool"

color_recs = {
    "Warm": {
        "best": "Earth tones, olive green, mustard, rust, warm reds, camel, cream, terracotta",
        "avoid": "Icy blues, pure white, bright pink, jewel tones",
        "metals": "Gold, bronze, copper"
    },
    "Cool": {
        "best": "Jewel tones, sapphire blue, emerald, true red, pure white, charcoal, fuchsia",
        "avoid": "Orange, mustard yellow, warm browns, beige",
        "metals": "Silver, platinum, white gold"
    },
    "Neutral": {
        "best": "Soft neutrals, dusty pinks, jade green, teal, lavender, navy, true red",
        "avoid": "Very few restrictions",
        "metals": "Both gold and silver work"
    }
}

recs = color_recs[undertone]

# Draw sample boxes
annotated = image.copy()
cv2.rectangle(annotated, (left_box[0], left_box[1]), (left_box[2], left_box[3]), (0, 255, 0), 2)
cv2.rectangle(annotated, (center_box[0], center_box[1]), (center_box[2], center_box[3]), (0, 255, 0), 2)
cv2.rectangle(annotated, (right_box[0], right_box[1]), (right_box[2], right_box[3]), (0, 255, 0), 2)
cv2.imwrite("skin_sample_result.jpg", annotated)

print("\n" + "=" * 50)
print("SKIN TONE ANALYSIS")
print("=" * 50)
print(f"\nAverage skin RGB:  ({int(avg_skin_rgb[0])}, {int(avg_skin_rgb[1])}, {int(avg_skin_rgb[2])})")
print(f"LAB values:        L={L}, a={a}, b={b}")
print(f"\nSkin Depth:        {depth}")
print(f"Undertone:         {undertone}")
print(f"Description:       {undertone_desc}")
print(f"\nColor Palette for You:")
print(f"  Best colors:   {recs['best']}")
print(f"  Avoid:         {recs['avoid']}")
print(f"  Metals/jewelry: {recs['metals']}")
print("\nSaved skin_sample_result.jpg")
print("=" * 50)