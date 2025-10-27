import io
import logging

import pytesseract
from PIL import Image, ImageEnhance

logger = logging.getLogger(__name__)


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for OCR: convert to grayscale and increase contrast.
    """
    # Convert to grayscale
    image = image.convert("L")
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Preprocess image
        processed_image = preprocess_image(image)

        # Extract text using Tesseract
        text = pytesseract.image_to_string(processed_image)

        if not text.strip():
            raise ValueError("No text could be extracted from the image")

        # Clean and normalize text
        cleaned_text = text.strip().replace("\n", " ").replace("  ", " ")

        logger.debug(f"Extracted OCR text: {cleaned_text}")

        return cleaned_text

    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}")
