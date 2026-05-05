import csv
import os

TAG_RULES = {
    "minimalist": [
        "essential", "minimal", "basic", "clean", "simple", "no logo",
        "plain", "solid", "monochrome", "understated", "refined"
    ],
    "bold": [
        "graphic", "print", "pattern", "logo", "statement",
        "bright", "neon", "metallic", "sequin", "embroidered"
    ],
    "muted": [
        "earth", "subtle", "muted", "olive", "khaki", "sand", "stone",
        "beige", "rust", "burgundy", "oatmeal", "natural", "heather",
        "driftwood", "burnt", "smoked", "washed", "indigo"
    ],
    "tailored": [
        "slim", "tailored", "fitted", "structured", "trim",
        "pleated", "darted", "athletic fit"
    ],
    "relaxed": [
        "relaxed", "oversized", "loose", "boxy", "drape",
        "easy", "roomy", "loungewear"
    ],
    "tapered": [
        "tapered", "modern fit", "slim taper", "carrot",
        "skinny taper", "athletic taper"
    ],
    "streetwear": [
        "graphic tee", "hoodie", "streetwear", "street style",
        "skate", "cargo", "joggers", "snapback", "track"
    ],
    "workwear": [
        "workwear", "work shirt", "canvas", "chore", "utility",
        "duck", "ripstop", "twill", "denim", "carhartt", "dickies",
        "field", "scout", "dispatch", "rugger", "rugby",
        "breakwater", "watchmaker", "ironworker", "craftsman", "foreman"
    ],
    "prep": [
        "polo", "oxford", "chino", "loafer", "rugby shirt",
        "blazer", "boat shoe", "knit polo", "tipped", "cable knit"
    ],
    "athleisure": [
        "performance", "technical", "athletic", "moisture", "wicking",
        "stretch", "compression", "running", "training", "gym",
        "workout", "tech fabric", "quick dry"
    ],
    "grunge": [
        "flannel", "distressed", "ripped", "faded", "vintage wash",
        "grunge", "thermal", "raw edge"
    ],
    "y2k": [
        "y2k", "2000s", "low rise", "trucker", "metallic",
        "rhinestone", "butterfly"
    ],
    "techwear": [
        "techwear", "gore-tex", "shell", "softshell", "modular",
        "tactical", "all black", "membrane", "waterproof tech"
    ],
    "vintage": [
        "vintage", "retro", "classic", "heritage", "throwback",
        "70s", "80s", "90s", "americana", "hemp", "organic",
        "selvedge", "rinsed indigo", "burnt", "scout", "dispatch",
        "breakwater", "broken twill", "double knit"
    ],
    "everyday": [
        "everyday", "daily", "essential", "staple", "go-to",
        "weekend", "casual", "all day", "tee", "t-shirt",
        "short sleeve", "henley"
    ],
    "going-out": [
        "going out", "going-out", "evening", "date", "night out",
        "party", "club", "cocktail", "dressy"
    ],
    "office": [
        "office", "work", "dress shirt", "suit",
        "professional", "business"
    ],
    "gym": [
        "gym", "workout", "training", "running", "performance",
        "lifting", "yoga", "active wear"
    ]
}

IMPLIED_TAGS = {
    "workwear": ["muted", "vintage"],
    "prep": ["tailored"],
    "athleisure": ["tapered"],
    "techwear": ["bold"],
}

def smart_tag(product_name, brand, subcategory, color):
    text = f"{product_name} {brand} {subcategory} {color}".lower()
    
    tags = set()
    for tag, keywords in TAG_RULES.items():
        for keyword in keywords:
            if keyword in text:
                tags.add(tag)
                break
    
    for primary, implied in IMPLIED_TAGS.items():
        if primary in tags:
            for imp in implied:
                tags.add(imp)
    
    if not tags:
        tags.add("everyday")
    
    use_tags = {"everyday", "going-out", "office", "gym"}
    if not tags.intersection(use_tags):
        tags.add("everyday")
    
    energy_tags = {"minimalist", "bold", "muted"}
    if not tags.intersection(energy_tags):
        tags.add("minimalist")
    
    return sorted(list(tags))

print("=" * 65)
print("SMART KEYWORD TAGGER")
print("=" * 65)

if not os.path.exists("real_catalog.csv"):
    print("ERROR: real_catalog.csv not found")
    exit()

products = []
with open("real_catalog.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    products = list(reader)

print(f"\nLoaded {len(products)} products")
print("Tagging with expanded keyword rules...\n")

for product in products:
    tags = smart_tag(
        product["name"],
        product["brand"],
        product["subcategory"],
        product.get("color", "")
    )
    product["ai_tags"] = ",".join(tags)

fieldnames = list(products[0].keys())
if "ai_tags" not in fieldnames:
    fieldnames.append("ai_tags")

with open("smart_catalog.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(products)

print("Sample taggings:\n")
for product in products[:8]:
    print(f"  {product['name'][:60]}")
    print(f"    Tags: {product['ai_tags']}")
    print()

print("=" * 65)
print("TAG DISTRIBUTION")
print("=" * 65)

tag_counts = {}
for product in products:
    for tag in product["ai_tags"].split(","):
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
    print(f"  {tag:15} {count:3} products")

print(f"\nDone. Tagged {len(products)} products instantly.")
print(f"Saved to: smart_catalog.csv")