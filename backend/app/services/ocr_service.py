import io
import logging

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


def run_advanced_image_processing(image: Image.Image) -> Image.Image:
    """
    Preprocess the image to improve OCR accuracy for alcohol labels.
    Focuses on extracting printed text (brand names, ABV) while ignoring cursive.
    """
    # Convert to OpenCV format for advanced processing
    img_array = np.array(image.convert("RGB"))
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Apply bilateral filter to reduce noise while keeping edges sharp
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # Apply adaptive thresholding to handle varying lighting conditions
    # This works better for labels with gradients or uneven lighting
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Optional: Apply morphological operations to clean up the text
    kernel = np.ones((1, 1), np.uint8)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Convert back to PIL Image
    processed = Image.fromarray(morphed)

    # Sharpen the image to make text more distinct
    processed = processed.filter(ImageFilter.SHARPEN)

    return processed


def run_basic_image_processing(image: Image.Image) -> Image.Image:
    # Convert to grayscale
    image = image.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    return image


def preprocess_image(image: Image.Image, use_advanced: bool = False) -> Image.Image:
    """
    Preprocess the image to improve OCR accuracy.
    """
    if use_advanced:
        # Advanced preprocessing can be added here
        logger.debug("Using advanced image preprocessing")
        image = run_advanced_image_processing(image)
    else:
        logger.debug("Using basic image preprocessing")
        image = run_basic_image_processing(image)
    return image


def extract_text_from_image(image_bytes: bytes, use_advanced=False) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        image_bytes (bytes): Raw image data

    Returns:
        str: Extracted text, cleaned and normalized

    Raises:
        ValueError: If image is unreadable or OCR fails
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Preprocess image
        processed_image = preprocess_image(image, use_advanced=use_advanced)

        # Extract text using Tesseract
        text = pytesseract.image_to_string(processed_image)

        if not text.strip():
            raise ValueError("No text could be extracted from the image")

        # Clean and normalize text
        cleaned_text = text.strip().replace("\n\n", "\n")

        logger.debug(f"Extracted OCR text: {cleaned_text}")

        return cleaned_text

    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}")
