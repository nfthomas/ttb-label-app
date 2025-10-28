import io
import logging

import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for OCR: convert to grayscale, denoise, and enhance contrast.
    """
    # Convert to grayscale
    image = image.convert("L")

    np_image = np.array(image)

    # Slight denoise and upscale (rescaled_2x)
    np_image = cv2.resize(np_image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # Apply CLAHE to normalize lighting and contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    np_image = clahe.apply(np_image)

    # Light contrast boost
    np_image = cv2.convertScaleAbs(np_image, alpha=1.3, beta=0)

    return Image.fromarray(np_image)


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Preprocess image
        processed_image = preprocess_image(image)

        # Extract text using Tesseract
        config = "--psm 11 --oem 3"  # PSM 11 = sparse text, OEM 3 = LSTM only
        text = pytesseract.image_to_string(processed_image, config=config)

        if not text.strip():
            raise ValueError("No text could be extracted from the image")

        # Clean and normalize text
        cleaned_text = text.strip().replace("\n", " ").replace("  ", " ")

        logger.debug(f"Extracted OCR text: {cleaned_text}")

        return cleaned_text

    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}")
