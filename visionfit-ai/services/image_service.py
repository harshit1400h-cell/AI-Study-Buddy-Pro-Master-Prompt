"""
Image Preprocessing and Transformation Service for VisionFit AI.
Handles safe resizing, format conversion, EXIF orientation, and byte optimization.
"""

import io
from typing import Tuple, Dict, Any
from PIL import Image, ImageOps

MAX_PREVIEW_WIDTH = 1600
MAX_PREVIEW_HEIGHT = 1600
JPEG_QUALITY = 88


class ImageService:
    @staticmethod
    def preprocess_image_for_gemini(image: Image.Image) -> Tuple[bytes, str, Image.Image]:
        """
        Preprocesses a PIL Image for optimal transmission to Gemini API:
        1. Auto-rotates using EXIF orientation if present.
        2. Converts color mode (RGBA/P) to standard RGB.
        3. Constrains max dimensions to prevent excessive token/bandwidth consumption.
        4. Encodes as clean JPEG bytes.

        Returns:
            (image_bytes, mime_type, processed_pil_image)
        """
        # 1. EXIF orientation correction
        try:
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        # 2. Mode conversion
        if image.mode in ("RGBA", "LA", "P"):
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            rgb_image.paste(image, mask=image.split()[-1] if "A" in image.mode else None)
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # 3. Downscale if dimensions exceed max constraints
        width, height = image.size
        if width > MAX_PREVIEW_WIDTH or height > MAX_PREVIEW_HEIGHT:
            image.thumbnail((MAX_PREVIEW_WIDTH, MAX_PREVIEW_HEIGHT), Image.Resampling.LANCZOS)

        # 4. Save to optimized JPEG bytes
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        image_bytes = buffer.getvalue()

        return image_bytes, "image/jpeg", image

    @staticmethod
    def get_image_metadata(image: Image.Image, raw_bytes: bytes) -> Dict[str, Any]:
        """
        Returns displayable metadata for an uploaded image.
        """
        width, height = image.size
        size_kb = len(raw_bytes) / 1024
        size_mb = size_kb / 1024
        
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1.0 else f"{size_kb:.1f} KB"
        
        return {
            "width": width,
            "height": height,
            "resolution": f"{width} × {height} px",
            "format": image.format or "JPEG",
            "mode": image.mode,
            "file_size": size_str,
        }

