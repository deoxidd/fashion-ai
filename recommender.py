import json
import os
import sys

# Load the user profile
if not os.path.exists("profile.json"):
    print("ERROR: profile.json not found. Run user_profile.py first.")
    exit()

with open("profile.json", "r") as f:
    profile = json.load(f)

body_shape = profile["body"]["shape"]
proportion = profile["body"]["proportion"]
undertone = profile["skin"]["undertone"]
depth = profile["skin"]["depth"]

# ============== FIT RULES (BODY SHAPE) ==============

fit_rules = {
    "Inverted Triangle": {
        "tops": {
            "recommended": ["V-neck tees", "scoop neck tees", "henleys", "open-collar shirts", "slim-fit knits", "bomber jackets (not boxy)"],
            "avoid": ["boat necks", "padded shoulders", "horizontal stripes across chest", "boxy oversized tees"],
            "fit_notes": "Slight taper through torso, medium shoulder room"
        },
        "bottoms": {
            "recommended": ["straight leg jeans", "slim-straight jeans", "relaxed chinos", "tapered cargo pants", "wider leg trousers"],
            "avoid": ["skinny jeans (reinforces V-shape too much)", "super slim pants"],
            "fit_notes": "Balance upper body mass with fuller lower body"
        },
        "outerwear": {
            "recommended": ["longer topcoats", "unstructured blazers", "overshirts", "denim trucker jackets"],
            "avoid": ["padded shoulders", "cropped jackets that emphasize shoulder line"]
        }
    },
    "Triangle": {
        "tops": {
            "recommended": ["structured button-ups", "oxford shirts", "light shoulder padding", "horizontal patterns up top"],
            "avoid": ["deep V-necks (narrows chest visually)", "extremely slim tops"],
            "fit_notes": "Add visual weight up top"
        },
        "bottoms": {
            "recommended": ["slim/tapered jeans", "slim chinos", "slightly cropped pants"],
            "avoid": ["wide leg", "cargo pants", "pleated pants"],
            "fit_notes": "Streamline lower body"
        },
        "outerwear": {
            "recommended": ["structured blazers", "cropped jackets", "puffer vests", "denim jackets with structure"],
            "avoid": ["long flowing coats", "unstructured long cardigans"]
        }
    },
    "Rectangle": {
        "tops": {
            "recommended": ["crew necks", "henleys", "layered tees", "textured knits", "patterns and prints"],
            "avoid": ["overly baggy shapeless tees"],
            "fit_notes": "Create definition through layering and structure"
        },
        "bottoms": {
            "recommended": ["slim fit", "slim-straight", "tapered chinos"],
            "avoid": ["extremely baggy or extremely skinny"],
            "fit_notes": "Slim-to-tapered is your best friend"
        },
        "outerwear": {
            "recommended": ["denim jackets", "bombers", "structured overshirts", "field jackets"],
            "avoid": ["shapeless oversized coats"]
        }
    }
}

# ============== COLOR RULES (UNDERTONE) ==============

color_palettes = {
    "Warm": {
        "neutrals": ["cream", "warm white", "camel", "chocolate brown", "olive green", "warm gray"],
        "statement": ["rust", "mustard", "burnt orange", "warm red", "terracotta", "burgundy"],
        "accents": ["gold", "bronze", "copper", "amber"],
        "avoid": ["icy pastels", "pure bright white", "hot pink", "cool blues"]
    },
    "Cool": {
        "neutrals": ["pure white", "charcoal", "black", "navy", "cool gray", "taupe"],
        "statement": ["sapphire blue", "emerald", "true red", "fuchsia", "royal purple"],
        "accents": ["silver", "platinum", "white gold"],
        "avoid": ["mustard yellow", "orange", "warm browns", "olive"]
    },
    "Neutral": {
        "neutrals": ["soft white", "gray", "navy", "camel", "taupe", "black"],
        "statement": ["dusty rose", "jade", "teal", "soft red", "lavender"],
        "accents": ["both gold and silver"],
        "avoid": ["extreme warm OR extreme cool"]
    }
}

# ============== PROPORTION RULES ==============

proportion_tips = {
    "Long-legged": "Higher-rise pants work well. You can pull off cropped pants and tucked-in tops. Longer tops also look great on you.",
    "Long-torso": "Lower-rise pants balance proportions. Untucked tops and shorter jackets work. Avoid cropped tops.",
    "Balanced": "Most pant rises and top lengths will work. Experiment freely."
}

# ============== STYLE PRESETS ==============

style_presets = {
    "minimal": {
        "core_items": ["solid tees", "plain knits", "clean denim", "minimal sneakers"],
        "color_strategy": "Stick to 2-3 colors max, mostly neutrals + 1 accent",
        "vibe": "Clean lines, quality fabrics, no logos or loud prints"
    },
    "streetwear": {
        "core_items": ["graphic tees", "oversized hoodies", "cargo pants", "chunky sneakers"],
        "color_strategy": "Mix neutrals with bold accent pieces",
        "vibe": "Relaxed fits, statement pieces, sneaker-forward"
    },
    "smart_casual": {
        "core_items": ["oxford shirts", "polos", "chinos", "loafers", "minimal leather sneakers"],
        "color_strategy": "Muted neutrals with occasional rich accent",
        "vibe": "Polished but not formal, versatile"
    },
    "athletic": {
        "core_items": ["performance tees", "technical joggers", "running-inspired sneakers"],
        "color_strategy": "Mostly neutrals (black, gray, white) with brand accents",
        "vibe": "Function-first, clean silhouettes"
    }
}

# ============== INPUT ==============

print("=" * 55)
print("STYLE RECOMMENDATION ENGINE")
print("=" * 55)
print(f"\nLoaded profile: {body_shape} | {proportion} | {undertone}")
print()
print("Choose your style direction:")
print("  1. Minimal")
print("  2. Streetwear")
print("  3. Smart Casual")
print("  4. Athletic")
print()

choice = input("Enter 1-4: ").strip()

style_map = {"1": "minimal", "2": "streetwear", "3": "smart_casual", "4": "athletic"}

if choice not in style_map:
    print("Invalid choice. Defaulting to minimal.")
    choice = "1"

style = style_map[choice]

# ============== BUILD RECOMMENDATION ==============

fit = fit_rules[body_shape]
colors = color_palettes[undertone]
preset = style_presets[style]

print("\n" + "=" * 55)
print(f"YOUR {style.upper()} STYLE GUIDE")
print("=" * 55)

print(f"\n🎯 THE VIBE")
print(f"   {preset['vibe']}")

print(f"\n👕 TOPS FOR YOU")
print(f"   Wear: {', '.join(fit['tops']['recommended'][:4])}")
print(f"   Avoid: {', '.join(fit['tops']['avoid'][:3])}")

print(f"\n👖 BOTTOMS FOR YOU")
print(f"   Wear: {', '.join(fit['bottoms']['recommended'][:3])}")
print(f"   Avoid: {', '.join(fit['bottoms']['avoid'][:2])}")

print(f"\n🧥 OUTERWEAR")
print(f"   Wear: {', '.join(fit['outerwear']['recommended'][:3])}")

print(f"\n🎨 YOUR COLOR PALETTE")
print(f"   Neutrals:  {', '.join(colors['neutrals'][:4])}")
print(f"   Statement: {', '.join(colors['statement'][:3])}")
print(f"   Metals:    {', '.join(colors['accents'][:2])}")

print(f"\n📏 PROPORTION TIP")
print(f"   {proportion_tips[proportion]}")

print(f"\n💡 COLOR STRATEGY FOR {style.upper()}")
print(f"   {preset['color_strategy']}")

# ============== BUILD SAMPLE OUTFIT ==============

# Pick one item from each category to build a complete outfit
top_choice = fit['tops']['recommended'][0]
bottom_choice = fit['bottoms']['recommended'][0]
neutral_color = colors['neutrals'][0]
statement_color = colors['statement'][0]
metal = colors['accents'][0]

print(f"\n" + "=" * 55)
print("SAMPLE OUTFIT BUILD")
print("=" * 55)

# Different outfit templates based on style
if style == "minimal":
    print(f"   Top:       {neutral_color.title()} {top_choice.rstrip('s')}")
    print(f"   Bottom:    Dark {bottom_choice.rstrip('s')}")
    print(f"   Shoes:     White minimal sneakers")
    print(f"   Accent:    {metal.title()} watch")
elif style == "streetwear":
    print(f"   Top:       Oversized {statement_color} graphic tee")
    print(f"   Layer:     {neutral_color.title()} hoodie (optional)")
    print(f"   Bottom:    Black tapered cargo pants")
    print(f"   Shoes:     Chunky sneakers (white or cream)")
    print(f"   Accent:    {metal.title()} chain")
elif style == "smart_casual":
    print(f"   Top:       {neutral_color.title()} oxford shirt, {top_choice.split()[0]} fit")
    print(f"   Bottom:    {bottom_choice.title()} in navy or olive")
    print(f"   Shoes:     Minimal leather sneakers or loafers")
    print(f"   Accent:    {metal.title()} watch")
elif style == "athletic":
    print(f"   Top:       {neutral_color.title()} performance tee, slim fit")
    print(f"   Bottom:    Tapered technical joggers (black)")
    print(f"   Shoes:     Clean runners")
    print(f"   Accent:    Minimal {metal} details")

print("\n" + "=" * 55)
print("✓ Recommendation complete!")
print("=" * 55)