from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.models.verification import LabelData, VerificationResult
from app.services.ocr_service import extract_text_from_image
from app.services.verification_service import verify_label

router = APIRouter()
logger = logging.getLogger(__name__)

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

@router.post("/verify", response_model=VerificationResult)
async def verify_label_image(
    image: UploadFile,
    brand_name: str = Form(...),
    product_type: str = Form(...),
    alcohol_content: float = Form(...),
    net_contents: Optional[str] = Form(None),
    use_advanced_ocr: bool = Form(False)
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
    # Validate file type
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG and PNG images are allowed."
        )
    
    # Read file content
    contents = await image.read()
    
    # Check file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds maximum limit of 5MB"
        )
    
    try:
        # Create form data model
        form_data = LabelData(
            brand_name=brand_name,
            product_type=product_type,
            alcohol_content=alcohol_content,
            net_contents=net_contents
        )
        
        # Extract text from image using optional advanced processing
        ocr_text = extract_text_from_image(contents, use_advanced=use_advanced_ocr)
        
        # Verify label data
        result = verify_label(form_data, ocr_text)
    
        return result
        
    except ValueError as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the image"
        )