"""
Image and Input Validation Utilities for VisionFit AI
Ensures files are valid, safe, within size bounds, and properly formatted before processing.
"""

from typing import Tuple, Optional
from io import BytesIO
from PIL import Image

# Allowed configurations
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_IMAGE_DIMENSION = 32
MAX_IMAGE_DIMENSION = 8000


def validate_uploaded_image(file_obj) -> Tuple[bool, str, Optional[Image.Image]]:
    """
    Validates an uploaded file object from Streamlit.
    Checks:
      1. Presence
      2. File size within allowed limits (< 10MB)
      3. Extension / MIME type
      4. Pillow integrity check (can open, verify, and read format)
      5. Minimum / maximum pixel dimensions
      
    Returns:
      (is_valid: bool, error_message: str, image_pil: Optional[Image.Image])
    """
    if file_obj is None:
        return False, "No file was uploaded.", None

    # Check file size
    try:
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(0)  # Reset pointer
    except Exception:
        file_size = getattr(file_obj, "size", 0)

    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = round(file_size / (1024 * 1024), 2)
        return False, f"File size ({size_mb} MB) exceeds maximum limit of 10 MB.", None

    if file_size == 0:
        return False, "Uploaded file appears to be empty (0 bytes).", None

    # Check extension
    filename = getattr(file_obj, "name", "image.jpg").lower()
    has_valid_ext = any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)
    if not has_valid_ext:
        return (
            False,
            f"Unsupported file format '{filename}'. Allowed formats: JPG, JPEG, PNG, WEBP.",
            None,
        )

    # Open and verify with Pillow
    try:
        # Read into BytesIO to avoid closing or altering original stream
        bytes_data = file_obj.read()
        file_obj.seek(0)
        
        img = Image.open(BytesIO(bytes_data))
        img.verify()  # Verifies file integrity
        
        # Need to reopen because verify() damages the stream for subsequent operations
        img = Image.open(BytesIO(bytes_data))
        
        # Check dimensions
        width, height = img.size
        if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
            return (
                False,
                f"Image resolution ({width}x{height}) is too small to recognize items clearly. Minimum is {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}.",
                None,
            )
            
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            return (
                False,
                f"Image resolution ({width}x{height}) exceeds maximum dimension of {MAX_IMAGE_DIMENSION}px.",
                None,
            )

        # Convert to RGB if RGBA/P to ensure compatibility across all vision models
        if img.mode in ("RGBA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                rgb_img.paste(img, mask=img.split()[3])
            else:
                rgb_img.paste(img.convert("RGBA"))
            return True, "", rgb_img

        return True, "", img

    except Exception as e:
        return False, f"Invalid or corrupted image file: {str(e)}", None


def sanitize_text_input(text: Optional[str], max_len: int = 300) -> str:
    """Safely sanitizes text input and strips leading/trailing characters."""
    if not text:
        return ""
    cleaned = text.strip()
    return cleaned[:max_len]

