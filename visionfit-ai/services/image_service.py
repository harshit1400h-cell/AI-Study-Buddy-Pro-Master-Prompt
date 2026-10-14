"""
Image Preprocessing and Sample Image Generation for VisionFit AI
Handles safe downscaling, formatting, bytes conversion, and built-in sample visuals.
"""

import io
import base64
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont


def preprocess_image(image: Image.Image, max_dimension: int = 1600) -> Image.Image:
    """
    Safely preprocesses an image:
    1. Converts to standard RGB mode (handling RGBA transparencies, Grayscale, and Palette modes).
    2. Proportionally resizes if exceeding max_dimension to optimize Gemini API latency and token usage.
    """
    # 1. Normalize color space to RGB
    if image.mode != "RGB":
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            # Convert with white background
            bg = Image.new("RGB", image.size, (255, 255, 255))
            converted = image.convert("RGBA")
            bg.paste(converted, mask=converted.split()[3])
            image = bg
        else:
            image = image.convert("RGB")

    # 2. Proportionally resize if larger than maximum dimension
    width, height = image.size
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        # Use high quality LANCZOS resampling
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return image


def image_to_bytes(image: Image.Image, format: str = "JPEG", quality: int = 88) -> bytes:
    """Encodes a PIL Image into bytes buffer."""
    buf = io.BytesIO()
    image.save(buf, format=format, quality=quality)
    return buf.getvalue()


def image_to_base64_data_uri(image: Image.Image) -> str:
    """Returns data URI string suitable for inline web preview."""
    b = image_to_bytes(image, format="JPEG")
    encoded = base64.b64encode(b).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def generate_sample_ingredients_image() -> Image.Image:
    """
    Generates a crisp visual simulation of kitchen ingredients:
    Bell Peppers, Tomatoes, Eggs, Spinach/Herbs, Olive Oil, and Garlic.
    Useful for instant demo testing without requiring personal photo upload.
    """
    img = Image.new("RGB", (800, 600), color=(26, 32, 44))
    draw = ImageDraw.Draw(img)

    # Kitchen wooden board background
    draw.rectangle([50, 50, 750, 550], fill=(61, 43, 31), outline=(139, 90, 43), width=4)
    draw.rectangle([70, 70, 730, 530], fill=(79, 56, 40))

    # Bell Pepper (Red)
    draw.ellipse([100, 120, 260, 320], fill=(220, 38, 38), outline=(153, 27, 27), width=3)
    draw.ellipse([140, 110, 220, 290], fill=(239, 68, 68))
    draw.rectangle([170, 80, 190, 120], fill=(34, 197, 94))  # Green stem

    # Bell Pepper (Green)
    draw.ellipse([270, 140, 420, 330], fill=(22, 163, 74), outline=(21, 128, 61), width=3)
    draw.rectangle([335, 100, 355, 140], fill=(20, 83, 45))

    # Ripe Tomatoes
    draw.ellipse([450, 130, 570, 250], fill=(239, 68, 68), outline=(185, 28, 28), width=2)
    draw.ellipse([540, 160, 650, 270], fill=(220, 38, 38), outline=(185, 28, 28), width=2)

    # Fresh Eggs carton
    draw.rectangle([110, 360, 360, 500], fill=(203, 213, 225), outline=(148, 163, 184), width=3)
    for x in (140, 200, 260, 320):
        draw.ellipse([x, 390, x + 35, 450], fill=(254, 243, 199), outline=(245, 158, 11), width=1)

    # Olive Oil Bottle
    draw.rectangle([440, 320, 530, 500], fill=(202, 138, 4), outline=(161, 98, 7), width=3)
    draw.rectangle([465, 280, 505, 320], fill=(161, 98, 7))  # Neck
    draw.rectangle([470, 260, 500, 280], fill=(234, 179, 8))  # Cap

    # Garlic Bulb
    draw.ellipse([590, 380, 690, 480], fill=(241, 245, 249), outline=(203, 213, 225), width=2)

    # Text Banner
    draw.rectangle([80, 510, 720, 545], fill=(15, 23, 42))
    draw.text((220, 520), "Sample Kitchen Ingredients: Veggies, Eggs, Olive Oil, Garlic", fill=(248, 250, 252))

    return img


def generate_sample_gym_image() -> Image.Image:
    """
    Generates a crisp visual simulation of gym workout equipment:
    Adjustable Dumbbells, Kettlebell, Resistance Bands, and Exercise Mat.
    Useful for instant demo testing without requiring personal photo upload.
    """
    img = Image.new("RGB", (800, 600), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Gym rubber flooring grid
    draw.rectangle([40, 40, 760, 560], fill=(30, 41, 59), outline=(51, 65, 85), width=4)

    # Exercise Mat (Emerald Teal)
    draw.rectangle([100, 100, 700, 240], fill=(13, 148, 136), outline=(15, 118, 110), width=3)
    for y in range(120, 230, 20):
        draw.line([(110, y), (690, y)], fill=(15, 118, 110), width=1)

    # Pair of Hex Dumbbells
    # Dumbbell 1
    draw.rectangle([140, 320, 170, 420], fill=(15, 23, 42), outline=(100, 116, 139), width=2)
    draw.rectangle([170, 355, 270, 385], fill=(148, 163, 184))  # Silver handle
    draw.rectangle([270, 320, 300, 420], fill=(15, 23, 42), outline=(100, 116, 139), width=2)
    draw.text((145, 360), "10kg", fill=(255, 255, 255))

    # Dumbbell 2
    draw.rectangle([140, 440, 170, 540], fill=(15, 23, 42), outline=(100, 116, 139), width=2)
    draw.rectangle([170, 475, 270, 505], fill=(148, 163, 184))
    draw.rectangle([270, 440, 300, 540], fill=(15, 23, 42), outline=(100, 116, 139), width=2)
    draw.text((145, 480), "10kg", fill=(255, 255, 255))

    # Kettlebell (Cast Iron Black with Yellow Ring)
    draw.ellipse([360, 360, 490, 490], fill=(15, 23, 42), outline=(71, 85, 105), width=3)
    draw.arc([390, 290, 460, 390], start=180, end=0, fill=(234, 179, 8), width=14)
    draw.text((405, 415), "16kg", fill=(234, 179, 8))

    # Resistance Loop Bands (Red, Blue, Green)
    draw.ellipse([540, 310, 680, 370], outline=(239, 68, 68), width=12)  # Heavy Red
    draw.ellipse([540, 390, 680, 450], outline=(59, 130, 246), width=10)  # Medium Blue
    draw.ellipse([540, 470, 680, 530], outline=(34, 197, 94), width=8)   # Light Green

    # Text Banner
    draw.rectangle([80, 530, 720, 555], fill=(11, 15, 25))
    draw.text((210, 535), "Sample Home Gym: Dumbbells (10kg), Kettlebell (16kg), Bands, Mat", fill=(16, 185, 129))

    return img

