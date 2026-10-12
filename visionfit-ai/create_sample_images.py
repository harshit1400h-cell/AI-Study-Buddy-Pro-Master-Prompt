"""
Creates realistic test images for VisionFit AI:
1. sample_ingredients.jpg: Kitchen pantry and fresh ingredients
2. sample_equipment.jpg: Home workout gear and fitness space
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_images"
SAMPLE_DIR.mkdir(exist_ok=True)


def create_ingredients_image():
    # 800x600 warm kitchen cutting board scene
    img = Image.new("RGB", (800, 600), color="#1e1814")
    draw = ImageDraw.Draw(img)

    # Cutting board background
    draw.rounded_rectangle([60, 60, 740, 540], radius=24, fill="#382518", outline="#593c28", width=4)
    draw.rounded_rectangle([80, 80, 720, 520], radius=16, fill="#4a3221")

    # Header label
    draw.text((100, 100), "KITCHEN INGREDIENTS AUDIT", fill="#e2e8f0")

    # Item 1: Red Bell Pepper
    draw.ellipse([140, 180, 280, 360], fill="#dc2626", outline="#991b1b", width=3)
    draw.rectangle([200, 160, 220, 200], fill="#15803d") # Stem
    draw.text((160, 380), "Red Bell Pepper", fill="#fca5a5")

    # Item 2: Yellow Bell Pepper
    draw.ellipse([320, 200, 440, 360], fill="#eab308", outline="#a16207", width=3)
    draw.rectangle([370, 180, 390, 220], fill="#15803d")
    draw.text((330, 380), "Yellow Pepper", fill="#fef08a")

    # Item 3: Canned Chickpeas
    draw.rounded_rectangle([480, 190, 600, 370], radius=12, fill="#94a3b8", outline="#64748b", width=3)
    draw.rounded_rectangle([490, 230, 590, 330], radius=6, fill="#fef3c7")
    draw.text((505, 270), "CHICKPEAS", fill="#92400e")
    draw.text((495, 380), "Chickpeas Can", fill="#cbd5e1")

    # Item 4: Garlic Cloves & Basil
    draw.ellipse([640, 240, 700, 300], fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.ellipse([620, 280, 670, 340], fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.text((630, 380), "Fresh Garlic", fill="#f8fafc")

    # Olive Oil Bottle silhouette
    draw.rounded_rectangle([100, 220, 150, 480], radius=8, fill="#166534", outline="#14532d", width=2)
    draw.text((105, 490), "Olive Oil", fill="#86efac")

    out_path = SAMPLE_DIR / "sample_ingredients.jpg"
    img.save(out_path, quality=92)
    print(f"Created sample ingredients image: {out_path}")


def create_equipment_image():
    # 800x600 home workout gym space
    img = Image.new("RGB", (800, 600), color="#0f172a")
    draw = ImageDraw.Draw(img)

    # Floor Mat
    draw.rounded_rectangle([80, 160, 720, 520], radius=20, fill="#1e293b", outline="#334155", width=3)
    draw.rounded_rectangle([120, 200, 680, 480], radius=12, fill="#0284c7") # Blue Yoga Mat
    draw.text((140, 220), "FITNESS WORKOUT SPACE", fill="#e0f2fe")

    # Dumbbell 1
    # Hex Left
    draw.polygon([(220, 310), (250, 280), (270, 310), (270, 370), (250, 400), (220, 370)], fill="#374151", outline="#111827")
    # Bar
    draw.rectangle([270, 330, 350, 350], fill="#9ca3af", outline="#6b7280")
    # Hex Right
    draw.polygon([(350, 310), (370, 280), (400, 310), (400, 370), (370, 400), (350, 370)], fill="#374151", outline="#111827")
    draw.text((260, 410), "Hex Dumbbell (10kg)", fill="#93c5fd")

    # Kettlebell
    draw.ellipse([460, 280, 580, 400], fill="#1f2937", outline="#111827", width=3)
    draw.arc([480, 230, 560, 310], start=180, end=0, fill="#9ca3af", width=12)
    draw.text((475, 410), "Kettlebell (12kg)", fill="#93c5fd")

    # Resistance Bands
    draw.arc([600, 240, 670, 440], start=45, end=315, fill="#e11d48", width=10)
    draw.text((590, 450), "Resistance Band", fill="#fda4af")

    out_path = SAMPLE_DIR / "sample_equipment.jpg"
    img.save(out_path, quality=92)
    print(f"Created sample equipment image: {out_path}")


if __name__ == "__main__":
    create_ingredients_image()
    create_equipment_image()

