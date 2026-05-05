import requests
import csv
import time

STORES = [
    {
        "name": "Taylor Stitch",
        "url": "https://www.taylorstitch.com/products.json",
        "default_undertone": "warm"
    },
    {
        "name": "Outerknown",
        "url": "https://www.outerknown.com/products.json",
        "default_undertone": "neutral"
    },
    {
        "name": "Saturdays NYC",
        "url": "https://www.saturdaysnyc.com/products.json",
        "default_undertone": "neutral"
    },
    {
        "name": "Aime Leon Dore",
        "url": "https://www.aimeleondore.com/products.json",
        "default_undertone": "neutral"
    },
    {
        "name": "Stussy",
        "url": "https://www.stussy.com/products.json",
        "default_undertone": "neutral"
    },
    {
        "name": "Ten Thousand",
        "url": "https://www.tenthousand.cc/products.json",
        "default_undertone": "neutral"
    }
]

PRODUCTS_PER_STORE = 80


def infer_tags(product_name, product_type, product_description):
    text = f"{product_name} {product_type} {product_description}".lower()
    tags = []
    
    if any(w in text for w in ["minimal", "essential", "basic", "clean"]):
        tags.append("minimalist")
    if any(w in text for w in ["graphic", "bold", "print", "pattern"]):
        tags.append("bold")
    if any(w in text for w in ["muted", "earth", "neutral", "subtle"]):
        tags.append("muted")
    
    if any(w in text for w in ["slim", "tailored", "fitted"]):
        tags.append("tailored")
    if any(w in text for w in ["relaxed", "oversized", "loose"]):
        tags.append("relaxed")
    if any(w in text for w in ["tapered", "modern fit"]):
        tags.append("tapered")
    
    if any(w in text for w in ["workwear", "work shirt", "canvas", "chore", "utility"]):
        tags.append("workwear")
    if any(w in text for w in ["polo", "oxford", "chino", "loafer"]):
        tags.append("prep")
    if any(w in text for w in ["performance", "technical", "athletic", "moisture"]):
        tags.append("athleisure")
    if any(w in text for w in ["vintage", "retro", "classic", "heritage"]):
        tags.append("vintage")
    if any(w in text for w in ["streetwear", "street", "graphic tee"]):
        tags.append("streetwear")
    
    if any(w in text for w in ["everyday", "daily", "essential"]):
        tags.append("everyday")
    if any(w in text for w in ["gym", "workout", "training", "performance"]):
        tags.append("gym")
    if any(w in text for w in ["office", "work", "dress shirt", "blazer"]):
        tags.append("office")
    
    if not tags:
        tags.append("everyday")
    
    return ",".join(tags)


def detect_gender(product_name, product_type, vendor=""):
    text = f"{product_name} {product_type} {vendor}".lower()
    
    womens_keywords = [
        "women", "women's", "womens", "ladies", "her", "girls",
        "skirt", "dress", "blouse", "bra", "leggings",
        "tankini", "bikini", "midi", "maxi", "mini dress",
        "hourglass", "fit and flare", "wrap dress", "bodysuit",
        "halter", "camisole", "peplum", "kimono"
    ]
    
    mens_keywords = [
        "men", "men's", "mens", "him", "guys",
        "boxer", "boxer brief", "boxers"
    ]
    
    for kw in womens_keywords:
        if kw in text:
            return "womens"
    
    for kw in mens_keywords:
        if kw in text:
            return "mens"
    
    return "unisex"


COLOR_MAP = {
    "cream": ("cream", "warm-white", "warm"),
    "off-white": ("cream", "warm-white", "warm"),
    "camel": ("camel", "brown", "warm"),
    "tan": ("camel", "brown", "warm"),
    "rust": ("rust", "orange", "warm"),
    "terracotta": ("terracotta", "orange", "warm"),
    "olive": ("olive", "green", "warm"),
    "mustard": ("mustard", "yellow", "warm"),
    "brown": ("brown", "brown", "warm"),
    "tobacco": ("brown", "brown", "warm"),
    "burgundy": ("burgundy", "red", "warm"),
    "navy": ("navy", "blue", "cool"),
    "royal": ("royal", "blue", "cool"),
    "sapphire": ("sapphire", "blue", "cool"),
    "emerald": ("emerald", "green", "cool"),
    "pure white": ("white", "neutral", "cool"),
    "pink": ("pink", "pink", "cool"),
    "white": ("white", "neutral", "neutral"),
    "black": ("black", "neutral", "neutral"),
    "gray": ("gray", "gray", "neutral"),
    "grey": ("gray", "gray", "neutral"),
    "charcoal": ("charcoal", "gray", "neutral"),
    "stone": ("stone", "gray", "neutral"),
    "khaki": ("khaki", "brown", "warm"),
    "indigo": ("indigo", "blue", "cool"),
    "denim": ("dark-blue", "blue", "neutral"),
    "heather": ("gray", "gray", "neutral"),
    "silver": ("silver", "neutral", "cool"),
    "gold": ("gold", "yellow", "warm"),
}


def detect_color(product_name, variant_title=""):
    text = f"{product_name} {variant_title}".lower()
    for keyword, (color, family, undertone) in COLOR_MAP.items():
        if keyword in text:
            return color, family, undertone
    return "unknown", "neutral", "neutral"


def detect_category(product_type, product_name):
    text = f"{product_type} {product_name}".lower()
    
    # Hats first (more specific than tops)
    if any(w in text for w in ["hat", "cap", "beanie", "bucket", "5-panel", "trucker hat", "snapback"]):
        return "hats"
    
    # Eyewear
    if any(w in text for w in ["sunglasses", "eyewear", "shades", "glasses", "frames"]):
        return "eyewear"
    
    # Jewelry
    if any(w in text for w in ["bracelet", "necklace", "ring ", "rings", "chain", "pendant", "earring"]):
        return "jewelry"
    
    # Watches
    if any(w in text for w in ["watch", "wristwatch", "timepiece"]):
        return "watches"
    
    # Bags
    if any(w in text for w in ["bag", "tote", "backpack", "crossbody", "duffle", "duffel", "pouch", "fanny", "messenger"]):
        return "bags"
    
    # Belts
    if any(w in text for w in ["belt", "buckle"]):
        return "belts"
    
    # Tops
    if any(w in text for w in ["tee", "t-shirt", "shirt", "henley", "polo", "sweater", "sweatshirt", "hoodie", "knit", "turtleneck"]):
        if any(w in text for w in ["jacket", "coat", "overshirt", "blazer"]):
            return "outerwear"
        return "tops"
    
    # Bottoms
    if any(w in text for w in ["pant", "jean", "trouser", "chino", "short", "joggers", "cargo"]):
        return "bottoms"
    
    # Shoes
    if any(w in text for w in ["shoe", "sneaker", "boot", "loafer", "sandal"]):
        return "shoes"
    
    # Outerwear
    if any(w in text for w in ["jacket", "coat", "blazer", "parka", "vest", "overshirt"]):
        return "outerwear"
    
    return None


def detect_fit(product_name, product_description, category):
    """Fit doesn't matter for accessories."""
    if category in ("hats", "eyewear", "jewelry", "watches", "bags", "belts"):
        return "n/a"
    
    text = f"{product_name} {product_description}".lower()
    
    if "skinny" in text:
        return "skinny"
    if "slim straight" in text or "slim-straight" in text:
        return "slim-straight"
    if "slim" in text or "tailored" in text or "fitted" in text:
        return "slim"
    if "tapered" in text:
        return "tapered"
    if "wide" in text or "loose" in text:
        return "wide"
    if "relaxed" in text or "oversized" in text:
        return "relaxed"
    if "straight" in text:
        return "straight"
    
    return "slim"


def fetch_store(store):
    print(f"\nFetching from {store['name']}...")
    all_items = []
    
    try:
        for page in range(1, 5):
            url = f"{store['url']}?limit=50&page={page}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"  Error: status {response.status_code}")
                break
            
            data = response.json()
            products = data.get("products", [])
            
            if not products:
                break
            
            for product in products:
                variants = product.get("variants", [])
                if not variants:
                    continue
                
                images = product.get("images", [])
                image_url = images[0]["src"] if images else ""
                
                name = product.get("title", "")
                product_type = product.get("product_type", "")
                description = (product.get("body_html") or "")[:500]
                vendor = product.get("vendor", "")
                
                category = detect_category(product_type, name)
                if not category:
                    continue
                
                variant = variants[0]
                variant_title = variant.get("title", "")
                color, color_family, undertone = detect_color(name, variant_title)
                
                if color == "unknown":
                    continue
                
                fit = detect_fit(name, description, category)
                tags = infer_tags(name, product_type, description)
                gender = detect_gender(name, product_type, vendor)
                
                price = variant.get("price", "0")
                try:
                    price_float = float(price)
                except:
                    price_float = 0
                
                handle = product.get("handle", "")
                base_url = store["url"].replace("/products.json", "")
                product_url = f"{base_url}/products/{handle}"
                
                all_items.append({
                    "id": f"{store['name'][:3].lower()}_{product['id']}",
                    "name": name,
                    "category": category,
                    "subcategory": product_type,
                    "color": color,
                    "color_family": color_family,
                    "undertone_match": undertone,
                    "fit": fit,
                    "tags": tags,
                    "gender": gender,
                    "price": round(price_float, 2),
                    "brand": store["name"],
                    "url": product_url,
                    "image_url": image_url
                })
                
                if len(all_items) >= PRODUCTS_PER_STORE:
                    break
            
            if len(all_items) >= PRODUCTS_PER_STORE:
                break
            
            time.sleep(0.5)
        
        print(f"  Got {len(all_items)} items from {store['name']}")
        return all_items
    
    except requests.RequestException as e:
        print(f"  Error fetching {store['name']}: {e}")
        return []


print("=" * 60)
print("FETCHING REAL PRODUCT DATA")
print("=" * 60)

all_products = []
for store in STORES:
    items = fetch_store(store)
    all_products.extend(items)

print(f"\n\nTotal products collected: {len(all_products)}")

if len(all_products) == 0:
    print("No products fetched.")
    exit()

output_file = "real_catalog.csv"
fieldnames = ["id", "name", "category", "subcategory", "color", "color_family",
              "undertone_match", "fit", "tags", "gender", "price", "brand", "url", "image_url"]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print(f"Saved to {output_file}")

print("\n--- Breakdown by Category ---")
categories = {}
for p in all_products:
    categories[p["category"]] = categories.get(p["category"], 0) + 1
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

print("\n--- Breakdown by Brand ---")
brands = {}
for p in all_products:
    brands[p["brand"]] = brands.get(p["brand"], 0) + 1
for brand, count in sorted(brands.items()):
    print(f"  {brand}: {count}")

print("\n--- Breakdown by Gender ---")
genders = {}
for p in all_products:
    genders[p["gender"]] = genders.get(p["gender"], 0) + 1
for g, count in sorted(genders.items()):
    print(f"  {g}: {count}")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)