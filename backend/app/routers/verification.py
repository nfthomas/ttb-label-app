import io
import logging
from typing import Dict

from fastapi import APIRouter, Form, HTTPException, UploadFile
from PIL import Image

from app.models.verification import LabelData, VerificationResult
from app.services.ocr_service import extract_text_from_image
from app.services.verification_service import verify_label

router = APIRouter()
logger = logging.getLogger(__name__)

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


class VerificationError(Exception):
    """Custom exception for verification-related errors."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def get_image_info(image_data: bytes) -> Dict:
    """Extract image dimensions and file size."""
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "file_size": len(image_data) / 1024,  # Size in KB
            }
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return {}


@router.post("/verify")
async def verify_label_image(
    image: UploadFile,
    brand_name: str = Form(...),
    product_type: str = Form(...),
    net_contents: str = Form(...),
    alcohol_content: float = Form(...),
    fuzzy_match: bool = Form(False),
) -> VerificationResult:
    """
    Verify alcohol label image against provided form data.

    Args:
        image: Image file (jpg or png)
        brand_name: Name of the alcohol brand
        product_type: Type of alcohol product
        alcohol_content: Alcohol content percentage (ABV)
        net_contents: Optional volume of the container

    Returns:
        VerificationResult with matching details

    Raises:
        HTTPException: For invalid files or processing errors
    """
    try:
        # Validate file type
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise VerificationError(
                status_code=400,
                detail="Invalid file type. Only JPEG and PNG images are allowed.",
            )

        # Read file content
        contents = await image.read()

        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise VerificationError(
                status_code=400, detail="File size exceeds maximum limit of 5MB"
            )

        # Get image information
        image_info = get_image_info(contents)
        if not image_info:
            raise VerificationError(
                status_code=422,
                detail="Unable to process image. Please ensure it is a valid JPEG or PNG file.",
            )

        # Create form data model
        form_data = LabelData(
            brand_name=brand_name,
            product_type=product_type,
            alcohol_content=alcohol_content,
            net_contents=net_contents,
        )

        # Extract text from image
        try:
            ocr_text = extract_text_from_image(contents)
            if not ocr_text.strip():
                raise VerificationError(
                    status_code=422,
                    detail="No text could be detected in the image. Please ensure the image is clear and contains readable text.",
                )
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            raise VerificationError(
                status_code=422,
                detail="Error processing image text. Please ensure the image is clear and properly oriented.",
            )

        # Verify label data
        try:
            result = verify_label(form_data, ocr_text, fuzzy_match=fuzzy_match)
            result.image_info = image_info
            return result
        except ValueError as e:
            raise VerificationError(status_code=422, detail=str(e))

    except VerificationError as e:
        logger.error(f"Verification error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the image. Please try again.",
        )
