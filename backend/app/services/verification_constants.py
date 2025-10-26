import re
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, List, Pattern

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class MatchThresholds:
    """Thresholds used for fuzzy string matching across different verification checks"""

    FUZZY_MATCH: ClassVar[float] = 0.8  # High confidence match threshold
    CLOSE_MATCH: ClassVar[float] = (
        0.5  # Lower threshold for finding potential close matches
    )
    MAX_CLOSE_MATCHES: ClassVar[int] = 3  # Maximum number of close matches to return

    @classmethod
    def is_fuzzy_match(cls, ratio: float) -> bool:
        """Check if a similarity ratio meets the fuzzy match threshold"""
        return ratio >= cls.FUZZY_MATCH

    @classmethod
    def is_close_match(cls, ratio: float) -> bool:
        """Check if a similarity ratio meets the close match threshold"""
        return ratio >= cls.CLOSE_MATCH


class TextNormalization:
    """Common OCR text normalization substitutions for handling common OCR mistakes"""

    REPLACEMENTS: Dict[str, str] = {
        "o": "0",  # letter to number
        "0": "o",  # number to letter
        "i": "1",  # letter to number
        "1": "i",  # number to letter
        "s": "5",  # letter to number
        "5": "s",  # number to letter
    }


class AlcoholContent:
    """
    Patterns for matching alcohol content in various formats.
    Examples:
    - 45%
    - 45 %
    - 45% Alc./Vol.
    - Alc 45% by Vol
    """

    @staticmethod
    def get_patterns(content_str: str) -> List[Pattern]:
        return [
            re.compile(rf"{content_str}\s*%"),
            re.compile(rf"{content_str}\s*%\s*alc\.?\s*/\s*vol\.?"),
            re.compile(rf"alc\.?\s*{content_str}\s*%\s*by\s*vol\.?"),
        ]

    # Pattern for finding any alcohol content mention for close matches
    GENERAL_PATTERN = re.compile(
        r"\d+(?:\.\d+)?\s*%(?:\s*alc\.?\s*/\s*vol\.?|\s*by\s*vol\.?)?"
    )


class NetContents:
    """
    Patterns for matching net contents in various formats.
    Examples:
    - 750ml
    - 750mL
    - 750ML
    - 12 fl oz
    """

    @staticmethod
    def get_patterns(num: str, unit: str) -> List[Pattern]:
        return [
            re.compile(rf"{num}\s*{unit}"),  # 750ml
            re.compile(rf"{num}\s*{unit[0]}{unit[1:]}"),  # 750mL
            re.compile(rf"{num}\s*{unit.upper()}"),  # 750ML
        ]

    # Pattern for finding any volume mention for close matches
    GENERAL_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*(?:ml|mL|oz|fl\.?\s*oz)")


class FieldNames(str, Enum):
    """Enumeration of field names used in verification responses"""

    BRAND_NAME = "brand_name"
    PRODUCT_TYPE = "product_type"
    ALCOHOL_CONTENT = "alcohol_content"
    NET_CONTENTS = "net_contents"
    GOVERNMENT_WARNING = "government_warning"


class VerificationField(BaseModel):
    """Configuration for field-specific verification settings"""

    name: str = Field(..., description="Display name of the field")
    allows_fuzzy_match: bool = Field(
        default=False,
        description="Whether to allow fuzzy string matching for this field",
    )


# Field configurations
FIELD_CONFIGS = {
    FieldNames.BRAND_NAME: VerificationField(
        name="Brand Name",
        allows_fuzzy_match=True,
    ),
    FieldNames.PRODUCT_TYPE: VerificationField(
        name="Product Type",
        allows_fuzzy_match=True,
    ),
    FieldNames.ALCOHOL_CONTENT: VerificationField(
        name="Alcohol Content",
        allows_fuzzy_match=False,
    ),
    FieldNames.NET_CONTENTS: VerificationField(
        name="Net Contents",
        allows_fuzzy_match=False,
    ),
    FieldNames.GOVERNMENT_WARNING: VerificationField(
        name="Government Warning",
        allows_fuzzy_match=True,
    ),
}
