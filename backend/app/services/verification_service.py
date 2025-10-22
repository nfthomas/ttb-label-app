import re
from typing import Tuple
from app.models.verification import LabelData, VerificationResult

def normalize_text(text: str) -> str:
    """Normalize text for comparison by converting to lowercase and removing extra whitespace."""
    return ' '.join(text.lower().split())

def check_alcohol_content(form_value: float, ocr_text: str) -> bool:
    """
    Check if the alcohol content appears in the OCR text.
    Handles variations like "45%" or "45 percent" or "45".
    """
    # Convert float to string without trailing zeros
    content_str = f"{form_value:g}"
    patterns = [
        rf"{content_str}\s*%",  # 45%
        rf"{content_str}\s*percent",  # 45 percent
        rf"{content_str}\s*vol",  # 45 vol
        content_str  # 45
    ]
    
    normalized_text = normalize_text(ocr_text)
    return any(re.search(pattern, normalized_text) for pattern in patterns)

def check_net_contents(form_value: str, ocr_text: str) -> bool:
    """
    Check if the net contents volume appears in the OCR text.
    Handles variations like "750mL", "750 mL", "750 ml".
    """
    if not form_value:
        return True
        
    # Extract number and unit from form value
    match = re.match(r'(\d+)\s*([a-zA-Z]+)', form_value)
    if not match:
        return False
        
    number, unit = match.groups()
    unit = unit.lower()
    
    # Create patterns for different format variations
    patterns = [
        rf"{number}\s*{unit}",  # 750ml
        rf"{number}\s*{unit[0]}{unit[1:]}",  # 750mL
        rf"{number}\s*{unit.upper()}"  # 750ML
    ]
    
    normalized_text = normalize_text(ocr_text)
    return any(re.search(pattern, normalized_text) for pattern in patterns)

def verify_label(form_data: LabelData, ocr_text: str) -> VerificationResult:
    """
    Verify if the form data matches the OCR text from the label image.
    
    Args:
        form_data: LabelData model containing expected values
        ocr_text: Text extracted from the image using OCR
        
    Returns:
        VerificationResult with detailed matching information
    """
    normalized_ocr = normalize_text(ocr_text)
    matches = {}
    mismatches = []
    
    # Check brand name
    matches['brand_name'] = normalize_text(form_data.brand_name) in normalized_ocr
    if not matches['brand_name']:
        mismatches.append('brand_name')
    
    # Check product type
    matches['product_type'] = normalize_text(form_data.product_type) in normalized_ocr
    if not matches['product_type']:
        mismatches.append('product_type')
    
    # Check alcohol content
    matches['alcohol_content'] = check_alcohol_content(form_data.alcohol_content, ocr_text)
    if not matches['alcohol_content']:
        mismatches.append('alcohol_content')
    
    # Check net contents if provided
    if form_data.net_contents:
        matches['net_contents'] = check_net_contents(form_data.net_contents, ocr_text)
        if not matches['net_contents']:
            mismatches.append('net_contents')
    
    # Check government warning
    matches['government_warning'] = 'government warning' in normalized_ocr
    if not matches['government_warning']:
        mismatches.append('government_warning')
    
    # Calculate overall success
    success = len(mismatches) == 0
    
    # Generate human-readable message
    if success:
        message = "All fields successfully verified on the label"
    else:
        message = f"Verification failed for: {', '.join(mismatches)}"
    
    return VerificationResult(
        success=success,
        matches=matches,
        mismatches=mismatches,
        raw_ocr_text=ocr_text,
        message=message
    )