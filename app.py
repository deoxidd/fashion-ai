import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import math
import csv
import os

st.set_page_config(
    page_title="Stylr AI",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .profile-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin: 1rem 0;
    }
    .product-card {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    .score-badge {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Stylr AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Built around you. Built around your style.</p>', unsafe_allow_html=True)

mp_pose = mp.solutions.pose


def analyze_image(image_bytes, gender_pref):
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        return None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    
    with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
        results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        return None
    
    landmarks = results.pose_landmarks.landmark
    
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
    
    class Point:
        pass
    
    def midpoint(p1, p2):
        m = Point()
        m.x = (p1.x + p2.x) / 2
        m.y = (p1.y + p2.y) / 2
        return m
    
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_ankle = landmarks[27]
    nose = landmarks[0]
    mouth_left = landmarks[9]
    mouth_right = landmarks[10]
    
    shoulder_width = distance(left_shoulder, right_shoulder)
    hip_width = distance(left_hip, right_hip)
    torso_length = distance(midpoint(left_shoulder, right_shoulder), midpoint(left_hip, right_hip))
    leg_length = distance(left_hip, left_ankle)
    
    shoulder_to_hip_ratio = shoulder_width / hip_width
    torso_to_leg_ratio = torso_length / leg_length
    
    if gender_pref == "womens":
        if shoulder_to_hip_ratio > 1.05:
            body_shape = "Inverted Triangle"
        elif shoulder_to_hip_ratio < 0.85:
            body_shape = "Pear"
        elif 0.95 <= shoulder_to_hip_ratio <= 1.05:
            body_shape = "Hourglass"
        else:
            body_shape = "Rectangle"
    else:
        if shoulder_to_hip_ratio > 1.15:
            body_shape = "Inverted Triangle"
        elif shoulder_to_hip_ratio < 0.95:
            body_shape = "Triangle"
        else:
            body_shape = "Rectangle"
    
    if torso_to_leg_ratio < 0.70:
        proportion = "Long-legged"
    elif torso_to_leg_ratio > 0.85:
        proportion = "Long-torso"
    else:
        proportion = "Balanced"
    
    neck_center = Point()
    neck_center.x = (left_shoulder.x + right_shoulder.x) / 2
    mouth_y = (mouth_left.y + mouth_right.y) / 2
    shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    neck_center.y = mouth_y + (shoulder_y - mouth_y) * 0.4
    
    samples = []
    for x_offset in [-0.03, 0, 0.03]:
        x = int((neck_center.x + x_offset) * width)
        y = int(neck_center.y * height)
        patch_size = 12
        x1, y1 = max(0, x - patch_size), max(0, y - patch_size)
        x2, y2 = min(width, x + patch_size), min(height, y + patch_size)
        patch = image_rgb[y1:y2, x1:x2]
        samples.append(np.mean(patch, axis=(0, 1)))
    
    avg_skin_rgb = np.mean(samples, axis=0)
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
    
    warm_score = int(b) - 128
    cool_score = int(a) - 128
    
    if warm_score > cool_score + 3:
        undertone = "Warm"
    elif cool_score > warm_score + 3:
        undertone = "Cool"
    else:
        undertone = "Neutral"
    
    return {
        "body_shape": body_shape,
        "proportion": proportion,
        "shoulder_to_hip": round(float(shoulder_to_hip_ratio), 2),
        "skin_depth": depth,
        "undertone": undertone,
        "skin_rgb": [int(avg_skin_rgb[0]), int(avg_skin_rgb[1]), int(avg_skin_rgb[2])],
        "gender_pref": gender_pref
    }


fit_scores = {
    "Inverted Triangle": {
        "slim": 90, "slim-straight": 95, "straight": 85, "tapered": 90,
        "relaxed": 75, "skinny": 30, "wide": 70, "chunky": 80, "athletic": 85
    },
    "Triangle": {
        "slim": 70, "slim-straight": 75, "straight": 70, "tapered": 80,
        "relaxed": 60, "skinny": 50, "wide": 40, "chunky": 60, "athletic": 70
    },
    "Rectangle": {
        "slim": 85, "slim-straight": 90, "straight": 85, "tapered": 85,
        "relaxed": 75, "skinny": 60, "wide": 70, "chunky": 75, "athletic": 85
    },
    "Hourglass": {
        "slim": 95, "slim-straight": 90, "straight": 75, "tapered": 80,
        "relaxed": 60, "skinny": 80, "wide": 70, "chunky": 70, "athletic": 80
    },
    "Pear": {
        "slim": 75, "slim-straight": 80, "straight": 75, "tapered": 70,
        "relaxed": 65, "skinny": 60, "wide": 50, "chunky": 60, "athletic": 70
    }
}

# Categories where fit doesn't apply (accessories)
ACCESSORY_CATEGORIES = {"hats", "eyewear", "jewelry", "watches", "bags", "belts"}


def score_undertone(item_undertone, user_undertone):
    user_lower = user_undertone.lower()
    item_lower = item_undertone.lower()
    if item_lower == user_lower:
        return 100
    elif item_lower == "neutral":
        return 80
    elif user_lower == "neutral":
        return 70
    else:
        return 30


def score_tags(item_tags_str, user_tags):
    if not item_tags_str:
        return 40
    item_tags = set(item_tags_str.split(","))
    user_set = set(user_tags)
    if not user_set:
        return 50
    overlap = item_tags.intersection(user_set)
    if not overlap:
        return 25
    match_ratio = len(overlap) / len(user_set)
    return round(40 + (match_ratio * 60))


def score_item(item, profile, user_tags):
    body_shape = profile["body_shape"]
    undertone = profile["undertone"]
    category = item.get("category", "")
    
    # For accessories, fit is always 100 (doesn't apply)
    if category in ACCESSORY_CATEGORIES:
        fit_score = 100
    else:
        fit_score = fit_scores.get(body_shape, {}).get(item["fit"], 50)
    
    undertone_score = score_undertone(item["undertone_match"], undertone)
    tags_to_use = item.get("ai_tags") or item.get("tags", "")
    tag_score = score_tags(tags_to_use, user_tags)
    
    # Different weighting for accessories (more weight on color + style, no fit penalty)
    if category in ACCESSORY_CATEGORIES:
        final_score = (undertone_score * 0.45) + (tag_score * 0.55)
    else:
        final_score = (fit_score * 0.35) + (undertone_score * 0.30) + (tag_score * 0.35)
    
    reasons = []
    if category not in ACCESSORY_CATEGORIES and fit_score >= 85:
        reasons.append(f"great fit for {body_shape}")
    if undertone_score >= 90:
        reasons.append(f"matches your {undertone.lower()} undertone")
    
    item_tags = set(tags_to_use.split(","))
    matched = item_tags.intersection(set(user_tags))
    if matched:
        reasons.append(f"matches: {', '.join(matched)}")
    
    return round(final_score, 1), reasons


if "profile" not in st.session_state:
    st.session_state.profile = None
if "step" not in st.session_state:
    st.session_state.step = "gender"
if "gender_pref" not in st.session_state:
    st.session_state.gender_pref = None
if "selected_tags" not in st.session_state:
    st.session_state.selected_tags = []


if st.session_state.step == "gender":
    st.markdown("### Step 1: How do you like to dress?")
    st.caption("This helps us recommend appropriate fits and brands.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👔 Men's", use_container_width=True, key="g_men"):
            st.session_state.gender_pref = "mens"
            st.session_state.step = "upload"
            st.rerun()
    
    with col2:
        if st.button("👗 Women's", use_container_width=True, key="g_women"):
            st.session_state.gender_pref = "womens"
            st.session_state.step = "upload"
            st.rerun()
    
    with col3:
        if st.button("✨ Both / Unisex", use_container_width=True, key="g_both"):
            st.session_state.gender_pref = "all"
            st.session_state.step = "upload"
            st.rerun()


elif st.session_state.step == "upload":
    pref_label = {"mens": "Men's", "womens": "Women's", "all": "Both / Unisex"}[st.session_state.gender_pref]
    st.markdown(f"### Step 2: Upload a full-body photo")
    st.caption(f"Style: {pref_label} · Stand facing camera, full body visible, good lighting")
    
    uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="Your photo", use_container_width=True)
        
        with col2:
            st.markdown("### Analyzing...")
            with st.spinner("Running body + skin analysis..."):
                image_bytes = uploaded_file.read()
                profile = analyze_image(image_bytes, st.session_state.gender_pref)
            
            if profile is None:
                st.error("Could not detect a body. Try a clearer full-body photo.")
            else:
                st.session_state.profile = profile
                st.success("Analysis complete!")
                
                st.markdown(f"""
                <div class="profile-card">
                    <h4>Body</h4>
                    <p><b>Shape:</b> {profile['body_shape']}</p>
                    <p><b>Proportion:</b> {profile['proportion']}</p>
                </div>
                
                <div class="profile-card">
                    <h4>Skin</h4>
                    <p><b>Depth:</b> {profile['skin_depth']}</p>
                    <p><b>Undertone:</b> {profile['undertone']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Next: Pick your style →", type="primary"):
                    st.session_state.step = "tags"
                    st.rerun()
    
    if st.button("← Change gender"):
        st.session_state.step = "gender"
        st.rerun()


elif st.session_state.step == "tags":
    profile = st.session_state.profile
    st.markdown(f"### Step 3: Pick your style")
    st.caption(f"Profile: {profile['body_shape']} · {profile['undertone']} undertone")
    
    tag_groups = {
        "Energy": ["minimalist", "bold", "muted"],
        "Fit": ["tailored", "relaxed", "tapered"],
        "Aesthetic": ["streetwear", "workwear", "prep", "athleisure", "grunge", "y2k", "techwear", "vintage"],
        "Use case": ["everyday", "going-out", "office", "gym"]
    }
    
    for group, tags in tag_groups.items():
        st.markdown(f"**{group}:**")
        cols_per_row = min(len(tags), 4)
        rows_needed = (len(tags) + cols_per_row - 1) // cols_per_row
        
        for row_idx in range(rows_needed):
            cols = st.columns(cols_per_row)
            row_tags = tags[row_idx * cols_per_row:(row_idx + 1) * cols_per_row]
            for i, tag in enumerate(row_tags):
                with cols[i]:
                    is_selected = tag in st.session_state.selected_tags
                    label = f"✓ {tag}" if is_selected else tag
                    button_type = "primary" if is_selected else "secondary"
                    if st.button(label, key=f"tag_{tag}", type=button_type, use_container_width=True):
                        if is_selected:
                            st.session_state.selected_tags.remove(tag)
                        else:
                            st.session_state.selected_tags.append(tag)
                        st.rerun()
        st.markdown("")
    
    st.markdown(f"**Selected:** {', '.join(st.session_state.selected_tags) if st.session_state.selected_tags else 'none yet'}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "upload"
            st.rerun()
    with col2:
        if len(st.session_state.selected_tags) >= 1:
            if st.button("Get Recommendations →", type="primary"):
                st.session_state.step = "results"
                st.rerun()


elif st.session_state.step == "results":
    profile = st.session_state.profile
    user_tags = st.session_state.selected_tags
    gender_pref = st.session_state.gender_pref
    
    st.markdown(f"### Your Recommendations")
    st.caption(f"Tags: {', '.join(user_tags)} · Style: {gender_pref}")
    
    catalog_file = "smart_catalog.csv" if os.path.exists("smart_catalog.csv") else "real_catalog.csv"
    
    if not os.path.exists(catalog_file):
        st.error("No catalog found. Run fetch_products.py first.")
    else:
        catalog = []
        with open(catalog_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            catalog = list(reader)
        
        if gender_pref == "mens":
            catalog = [item for item in catalog if item.get("gender") in ("mens", "unisex")]
        elif gender_pref == "womens":
            catalog = [item for item in catalog if item.get("gender") in ("womens", "unisex")]
        
        scored_items = []
        for item in catalog:
            score, reasons = score_item(item, profile, user_tags)
            scored_items.append({**item, "score": score, "reasons": reasons})
        
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        
        # Order: clothing first, then accessories
        category_order = ["tops", "bottoms", "outerwear", "shoes", "hats", "eyewear", "watches", "jewelry", "bags", "belts"]
        category_labels = {
            "tops": "TOPS",
            "bottoms": "BOTTOMS",
            "outerwear": "OUTERWEAR",
            "shoes": "SHOES",
            "hats": "HATS",
            "eyewear": "EYEWEAR",
            "watches": "WATCHES",
            "jewelry": "JEWELRY",
            "bags": "BAGS",
            "belts": "BELTS"
        }
        
        for category in category_order:
            cat_items = [i for i in scored_items if i["category"] == category]
            top_3 = cat_items[:3]
            
            if not top_3:
                continue
            
            st.markdown(f"#### {category_labels[category]}")
            cols = st.columns(3)
            
            for i, item in enumerate(top_3):
                with cols[i]:
                    st.markdown(f'<div class="product-card">', unsafe_allow_html=True)
                    
                    image_url = item.get("image_url", "").strip()
                    if image_url and image_url.startswith("http"):
                        try:
                            st.image(image_url, use_container_width=True)
                        except Exception:
                            st.markdown("📦 *(no image)*")
                    else:
                        st.markdown("📦 *(no image)*")
                    
                    st.markdown(f"**{item['name'][:50]}**")
                    st.markdown(f"${item['price']} · {item['brand']}")
                    st.markdown(f'<span class="score-badge">{item["score"]}/100</span>', unsafe_allow_html=True)
                    
                    reasons_text = " · ".join(item["reasons"]) if item["reasons"] else "decent match"
                    st.caption(reasons_text)
                    
                    st.link_button("View Product", item["url"])
                    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Change tags"):
            st.session_state.step = "tags"
            st.rerun()
    with col2:
        if st.button("Change gender"):
            st.session_state.step = "gender"
            st.session_state.selected_tags = []
            st.rerun()
    with col3:
        if st.button("Start over"):
            st.session_state.step = "gender"
            st.session_state.profile = None
            st.session_state.selected_tags = []
            st.rerun()