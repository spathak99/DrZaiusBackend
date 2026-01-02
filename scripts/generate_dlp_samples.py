#!/usr/bin/env python3
"""
Generate simple test images with embedded PII-like text for DLP redaction.
Output:
  - samples/images/ssn_phone.png
  - samples/images/email_card.png
Requires: Pillow (pip install Pillow)
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "samples" / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def draw_image(lines, filename, size=(1200, 600)):
    img = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Try a default truetype font; fallback to default if not available
    try:
        font = ImageFont.truetype("Arial.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    x, y = 40, 40
    for line in lines:
        draw.text((x, y), line, fill=(0, 0, 0), font=font)
        y += 60
    out_path = OUT_DIR / filename
    img.save(out_path)
    return out_path

def main():
    a = draw_image(
        [
            "Sample Image for DLP Redaction",
            "Call me at 415-555-1212",
            "SSN 123-45-6789",
        ],
        "ssn_phone.png",
    )
    b = draw_image(
        [
            "Contact: jane.doe@example.com",
            "Card: 4111-1111-1111-1111",
            "DOB: 01/23/1980",
        ],
        "email_card.png",
    )
    print(f"Generated:\n - {a}\n - {b}")

if __name__ == "__main__":
    main()



