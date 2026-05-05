# Fashion AI

AI-powered personal stylist that analyzes body shape and skin tone to recommend real clothing from real retailers.

## What It Does

1. Upload a full-body photo
2. Computer vision detects body proportions and skin undertone
3. Pick style tags that describe your taste
4. Get personalized recommendations with shoppable links to real products

## Tech Stack

- **Python** — backend logic
- **MediaPipe** — body landmark detection
- **OpenCV** — image processing and skin tone analysis
- **Streamlit** — web UI
- **Shopify Product APIs** — real product catalog (Taylor Stitch, Outerknown, Stussy, Aimé Leon Dore, Saturdays NYC, Ten Thousand)

## How It Works

The body analysis uses MediaPipe to extract 33 anatomical landmarks. Body shape is classified by shoulder-to-hip ratio. Skin undertone is extracted from the neck region in LAB color space.

The matching engine scores each product on three weighted factors:
- Body shape compatibility (35%)
- Color undertone match (30%)
- Style tag overlap (35%)

## Status

MVP. Built solo as a learning project.