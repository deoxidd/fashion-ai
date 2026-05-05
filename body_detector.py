import cv2
import mediapipe as mp
import os

# Set up MediaPipe's pose detection tool
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

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
    print("Add a .jpg, .jpeg, .png, or .webp file to the fashion-ai folder")
    exit()

print(f"Using image: {image_path}")
image = cv2.imread(image_path)

if image is None:
    print(f"ERROR: Could not load {image_path}")
    exit()

# Convert image to RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Run pose detection
with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
    results = pose.process(image_rgb)

# Check if a body was detected
if results.pose_landmarks:
    print("SUCCESS: Body detected!")
    print(f"Found {len(results.pose_landmarks.landmark)} landmarks")
    
    # Draw the landmarks on the image
    annotated_image = image.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )
    
    # Save the result
    cv2.imwrite("result.jpg", annotated_image)
    print("Saved result.jpg - open it to see the detection!")
else:
    print("No body detected. Try a clearer photo with a full body visible.")