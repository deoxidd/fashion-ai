import csv
import json
import os

if not os.path.exists("profile.json"):
    print("ERROR: profile.json not found. Run user_profile.py first.")
    exit()

with open("profile.json", "r") as f:
    profile = json.load(f)

body_shape = profile["body"]["shape"]
undertone = profile["skin"]["undertone"]
proportion = profile["body"]["proportion"]

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
    }
}

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

def score_tags(item_tags_str, user_selected_tags):
    if not item_tags_str:
        return 40
    item_tags = set(item_tags_str.split(","))
    user_tags = set(user_selected_tags)
    
    if not user_tags:
        return 50
    
    overlap = item_tags.intersection(user_tags)
    
    if not overlap:
        return 25
    
    match_ratio = len(overlap) / len(user_tags)
    return round(40 + (match_ratio * 60))

all_tags = {
    "Energy": ["minimalist", "bold", "muted"],
    "Fit philosophy": ["tailored", "relaxed", "tapered"],
    "Aesthetic": ["streetwear", "workwear", "prep", "athleisure", "grunge", "y2k", "techwear", "vintage"],
    "Use case": ["everyday", "going-out", "office", "gym"]
}

print("=" * 65)
print("PERSONALIZED MATCHER — SMART TAGS")
print("=" * 65)
print(f"\nYour profile: {body_shape} | {undertone} undertone | {proportion}")
print("\nPick 2-4 tags that describe your style:")
print()

tag_list = []
tag_number = 1

for category, tags in all_tags.items():
    print(f"  {category}:")
    for tag in tags:
        print(f"    [{tag_number:2}] {tag}")
        tag_list.append(tag)
        tag_number += 1
    print()

print("-" * 65)
print("Enter numbers separated by commas (example: 1,5,10)")
print("-" * 65)

user_input = input("\nYour tags: ").strip()

try:
    selected_numbers = [int(x.strip()) for x in user_input.split(",") if x.strip()]
    user_selected_tags = [tag_list[n-1] for n in selected_numbers if 1 <= n <= len(tag_list)]
except (ValueError, IndexError):
    user_selected_tags = ["minimalist", "everyday"]

if not user_selected_tags:
    user_selected_tags = ["minimalist", "everyday"]

print(f"\nYou picked: {', '.join(user_selected_tags)}")

catalog_file = "smart_catalog.csv" if os.path.exists("smart_catalog.csv") else "real_catalog.csv"

if not os.path.exists(catalog_file):
    print(f"\nERROR: No catalog found.")
    exit()

catalog = []
with open(catalog_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        catalog.append(row)

print(f"Loaded {len(catalog)} products from {catalog_file}\n")

def score_item(item, user_tags):
    fit_score = fit_scores[body_shape].get(item["fit"], 50)
    undertone_score = score_undertone(item["undertone_match"], undertone)
    
    tags_to_use = item.get("ai_tags") or item.get("tags", "")
    tag_score = score_tags(tags_to_use, user_tags)
    
    final_score = (fit_score * 0.35) + (undertone_score * 0.30) + (tag_score * 0.35)
    
    reasons = []
    if fit_score >= 85:
        reasons.append(f"great fit for {body_shape}")
    if undertone_score >= 90:
        reasons.append(f"perfect for your {undertone.lower()} undertone")
    elif undertone_score >= 70:
        reasons.append("neutral color")
    
    item_tags = set(tags_to_use.split(","))
    matched_tags = item_tags.intersection(set(user_tags))
    if matched_tags:
        reasons.append(f"matches: {', '.join(matched_tags)}")
    
    return {
        "score": round(final_score, 1),
        "reasons": reasons
    }

scored_items = []
for item in catalog:
    result = score_item(item, user_selected_tags)
    scored_items.append({**item, **result})

scored_items.sort(key=lambda x: x["score"], reverse=True)

print("\n" + "=" * 65)
print(f"TOP MATCHES (using smart tags)")
print(f"Tags: {', '.join(user_selected_tags)}")
print("=" * 65)

for category in ["tops", "bottoms", "outerwear", "shoes"]:
    category_items = [item for item in scored_items if item["category"] == category]
    top_3 = category_items[:3]
    
    if not top_3:
        continue
    
    print(f"\n{'─' * 65}")
    print(f"  {category.upper()}")
    print(f"{'─' * 65}")
    
    for i, item in enumerate(top_3, 1):
        reasons_str = " | ".join(item["reasons"]) if item["reasons"] else "decent match"
        print(f"\n  {i}. {item['name']} — ${item['price']}")
        print(f"     Brand: {item['brand']}")
        print(f"     Color: {item['color']}")
        print(f"     Score: {item['score']}/100")
        print(f"     Why: {reasons_str}")
        print(f"     Link: {item['url']}")

print("\n" + "=" * 65)