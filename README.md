# Stylr AI

Personal stylist powered by computer vision. Analyzes your body shape and skin tone, then recommends real clothing from real retailers that work for YOUR specific frame.

## What It Does

1. Upload a full-body photo
2. AI analyzes your body proportions (shape, frame, proportion)
3. AI detects your skin tone undertone (warm/cool/neutral)
4. Pick style tags that describe your taste
5. Get personalized recommendations with shoppable links

Built around you. Built around your style.

## Tech Stack

- **Python + Streamlit** — web app
- **MediaPipe** — body landmark detection
- **OpenCV** — image processing + skin tone analysis  
- **Shopify Product APIs** — real product catalog (Taylor Stitch, Outerknown, Stussy, Aimé Leon Dore, Miansai, Saturdays NYC, Ten Thousand)

## How It Works

Body analysis uses MediaPipe to extract 33 anatomical landmarks. Body shape classification is based on shoulder-to-hip ratio (men's: Inverted Triangle, Triangle, Rectangle; women's: Hourglass, Pear, Inverted Triangle, Rectangle). Skin undertone is extracted from the neck region in LAB color space.

The matching engine scores each product on three weighted factors:
- Body shape compatibility (35%)
- Color undertone match (30%)
- Style tag overlap (35%)

Accessories use a custom scoring (45% undertone, 55% tags, no fit penalty).

## Status

MVP. Live at `dylan-fashion-ai.streamlit.app`. Catalog: 500+ products from 7 brands.

## Roadmap

- Affiliate network integration (Skimlinks, Awin) — unlocks major retailers
- Better gender detection using brand-level rules
- Outfit builder (combines top + bottom + shoes into cohesive looks)
- Mobile-responsive design
- iOS app version