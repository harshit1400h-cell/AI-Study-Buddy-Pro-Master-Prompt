"""
Input validation utilities for VisionFit AI.
Ensures image safety, format compatibility, size constraints, and input sanitization.
"""

import io
from typing import Tuple, Optional
from PIL import Image, UnidentifiedImageError

# Supported mime types and extensions
SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
SUPPORTED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/jpg",
}

DEFAULT_MAX_SIZE_MB = 10.0
MIN_DIMENSION = 50
MAX_DIMENSION = 8000


def validate_image_file(
    file_bytes: bytes,
    file_name: str,
    max_size_mb: float = DEFAULT_MAX_SIZE_MB
) -> Tuple[bool, Optional[str], Optional[Image.Image]]:
    """
    Validates uploaded image bytes for size, format, and corruption.

    Returns:
        (is_valid, error_message, PIL_Image_or_None)
    """
    if not file_bytes:
        return False, "The uploaded file is empty. Please select a valid image.", None

    # 1. Size check
    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return (
            False,
            f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed limit of {max_size_mb} MB.",
            None,
        )

    # 2. Extension check
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if ext not in SUPPORTED_EXTENSIONS:
        return (
            False,
            f"Unsupported image format '.{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS)).upper()}.",
            None,
        )

    # 3. Pillow corruption & readability check
    try:
        image_stream = io.BytesIO(file_bytes)
        img = Image.open(image_stream)
        img.verify()  # Verify integrity without fully decoding
    except UnidentifiedImageError:
        return False, "Cannot identify image format. The file may be damaged or not a supported image.", None
    except Exception as e:
        return False, f"Corrupted or invalid image file: {str(e)}", None

    # 4. Re-open for actual processing (verify() closes or exhausts the stream)
    try:
        image_stream.seek(0)
        img = Image.open(image_stream)
        
        # Dimension check
        width, height = img.size
        if width < MIN_DIMENSION or height < MIN_DIMENSION:
            return (
                False,
                f"Image is too small ({width}x{height}px). Minimum resolution is {MIN_DIMENSION}x{MIN_DIMENSION}px.",
                None,
            )
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            return (
                False,
                f"Image resolution ({width}x{height}px) exceeds max dimensions of {MAX_DIMENSION}px.",
                None,
            )

        return True, None, img
    except Exception as e:
        return False, f"Failed to load image for processing: {str(e)}", None


def sanitize_text_input(text: Optional[str], max_chars: int = 300) -> str:
    """
    Sanitizes user text inputs (exclusions, allergies, notes).
    """
    if not text:
        return ""
    # Strip potential control characters
    cleaned = "".join(ch for ch in text if ch.isprintable())
    return cleaned.strip()[:max_chars]

