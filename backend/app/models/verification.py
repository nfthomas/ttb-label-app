from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LabelData(BaseModel):
    brand_name: str = Field(..., description="Name of the alcohol brand")
    product_type: str = Field(..., description="Type of alcohol product")
    alcohol_content: float = Field(..., description="Alcohol content percentage (ABV)")
    net_contents: Optional[str] = Field(
        None, description="Volume of the container (e.g., '750 mL')"
    )


class VerificationResult(BaseModel):
    success: bool = Field(..., description="Overall verification result")
    matches: Dict[str, bool] = Field(
        ..., description="Fields that matched successfully"
    )
    mismatches: List[str] = Field(
        ..., description="List of fields that failed to match"
    )
    raw_ocr_text: str = Field(..., description="Raw text extracted from the image")
    message: str = Field(..., description="Human-readable result message")
    close_matches: Dict[str, List[str]] = Field(
        default_factory=dict, description="Close matches found for failed verifications"
    )
    image_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Information about the processed image (dimensions, file size)",
    )
