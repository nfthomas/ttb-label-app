import difflib
import logging
import re
from typing import List, Optional, Set, Tuple

from app.models.verification import LabelData, VerificationResult

FUZZY_MATCH_THRESHOLD = 0.8
CLOSE_MATCH_THRESHOLD = 0.5


def normalize_text(text: str) -> str:
    """Normalize text for comparison by converting to lowercase and removing extra whitespace."""
    return " ".join(text.lower().split())


def get_similarity_ratio(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings using difflib."""
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def normalize_ocr_text(text: str) -> Set[str]:
    """
    Normalize OCR text by handling common OCR mistakes.

    Substitute letter->number and number->letter
    """
    # Handle common OCR mistakes
    replacements = {"o": "0", "0": "o", "i": "1", "1": "i", "s": "5", "5": "s"}
    normalized = text.lower()

    # Try each replacement and keep track of variants
    variants = {normalized}
    for old, new in replacements.items():
        for existing in list(variants):
            if old in existing:
                variants.add(existing.replace(old, new))

    return variants


def find_close_matches(
    target: str, text: str, threshold: float = CLOSE_MATCH_THRESHOLD
) -> List[str]:
    """Find close matches in text using fuzzy matching with a sliding window."""
    words = text.split()
    window_size = len(target.split())
    matches = []

    for i in range(len(words) - window_size + 1):
        window = " ".join(words[i : i + window_size])
        similarity = get_similarity_ratio(target, window)
        if similarity >= threshold:
            matches.append((window, similarity))

    # Sort matches by closest similarity and return the matched strings
    return [match for match, _ in sorted(matches, key=lambda x: x[1], reverse=True)]


def check_alcohol_content(
    form_value: float, normalized_ocr: str
) -> Tuple[bool, Optional[str]]:
    """
    Check if the alcohol content appears in the OCR text.
    Returns (success, closest_match).
    """
    content_str = f"{form_value:g}"
    patterns = [
        rf"{content_str}\s*%",  # 45% or 45 %
        rf"{content_str}\s*%\s*alc\.?\s*/\s*vol\.?",  # 45% Alc./Vol.
        rf"alc\.?\s*{content_str}\s*%\s*by\s*vol\.?",  # Alc 45% by Vol
    ]

    normalized_text = normalized_ocr

    # Check for exact matches
    if any(re.search(pattern, normalized_text) for pattern in patterns):
        return True, None

    # Look for close matches
    alcohol_pattern = r"\d+(?:\.\d+)?\s*%(?:\s*alc\.?\s*/\s*vol\.?|\s*by\s*vol\.?)?"
    matches = re.findall(alcohol_pattern, normalized_text)
    if matches:
        closest = matches[0]
        return False, f"Found {closest} (expected {content_str}%)"

    return False, None


def check_brand_name(
    form_value: str,
    normalized_ocr: str,
    normalized_variants: Set[str],
    fuzzy_match: bool,
) -> Tuple[bool, Optional[str]]:
    """
    Check if the brand name appears in the OCR text.
    Returns (success, closest_match).
    """
    brand_name_norm = normalize_text(form_value)

    if fuzzy_match:
        # Check sliding window matches in normalized_ocr
        matches = find_close_matches(
            brand_name_norm, normalized_ocr, FUZZY_MATCH_THRESHOLD
        )
        if matches:
            return True, None
        # Also check in variants
        for variant in normalized_variants:
            matches = find_close_matches(
                brand_name_norm, variant, FUZZY_MATCH_THRESHOLD
            )
            if matches:
                return True, None
        # No match, find close ones
        close = find_close_matches(
            brand_name_norm, normalized_ocr, CLOSE_MATCH_THRESHOLD
        )
        logging.info(f"Close matches for brand: {close}")
        if not close:
            for variant in normalized_variants:
                close = find_close_matches(
                    brand_name_norm, variant, CLOSE_MATCH_THRESHOLD
                )
                if close:
                    break
        return False, close[0] if close else None
    else:
        success = any(brand_name_norm in variant for variant in normalized_variants)
        logging.info(f"Brand name exact match: {success}")
        return success, None


def check_product_type(
    form_value: str,
    normalized_ocr: str,
    normalized_variants: Set[str],
    fuzzy_match: bool,
) -> Tuple[bool, Optional[str]]:
    """
    Check if the product type appears in the OCR text.
    Returns (success, closest_match).
    """
    product_type_norm = normalize_text(form_value)

    if fuzzy_match:
        # Check sliding window matches in normalized_ocr
        matches = find_close_matches(
            product_type_norm, normalized_ocr, FUZZY_MATCH_THRESHOLD
        )
        if matches:
            return True, None
        # Also check in variants
        for variant in normalized_variants:
            matches = find_close_matches(
                product_type_norm, variant, FUZZY_MATCH_THRESHOLD
            )
            if matches:
                return True, None
        # No match, find close ones
        close = find_close_matches(
            product_type_norm, normalized_ocr, CLOSE_MATCH_THRESHOLD
        )
        logging.info(f"Close matches for product_type: {close}")
        if not close:
            for variant in normalized_variants:
                close = find_close_matches(
                    product_type_norm, variant, CLOSE_MATCH_THRESHOLD
                )
                if close:
                    break
        return False, close[0] if close else None
    else:
        success = any(product_type_norm in variant for variant in normalized_variants)
        logging.info(f"Product type exact match: {success}")
        return success, None


def check_government_warning(normalized_ocr: str) -> Tuple[bool, Optional[str]]:
    """
    Check if the government warning appears in the OCR text.
    Returns (success, closest_match).
    """
    success = "government warning" in normalized_ocr
    if not success:
        closest = find_close_matches(
            "government warning", normalized_ocr, threshold=CLOSE_MATCH_THRESHOLD
        )
        return False, closest[0] if closest else None
    return True, None


def check_net_contents(
    form_value: str, normalized_ocr: str
) -> Tuple[bool, Optional[str]]:
    """
    Check if the net contents volume appears in the OCR text.
    Returns (success, closest_match).
    """
    if not form_value:
        return True, None

    # Extract number and unit from form value
    match = re.match(r"(\d+)\s*([a-zA-Z]+)", form_value)
    if not match:
        return False, None

    form_num, form_unit = match.groups()
    form_unit = form_unit.lower()

    normalized_text = normalized_ocr

    # Create patterns for different format variations
    patterns = [
        rf"{form_num}\s*{form_unit}",  # 750ml
        rf"{form_num}\s*{form_unit[0]}{form_unit[1:]}",  # 750mL
        rf"{form_num}\s*{form_unit.upper()}",  # 750ML
    ]

    # Check for exact matches
    if any(re.search(pattern, normalized_text) for pattern in patterns):
        return True, None

    # Look for close matches
    volume_pattern = r"\d+(?:\.\d+)?\s*(?:ml|mL|oz|fl\.?\s*oz)"
    matches = re.findall(volume_pattern, normalized_text)
    if matches:
        closest = matches[0]
        return False, f"Found {closest} (expected {form_value})"

    return False, None


def verify_label(
    form_data: LabelData, ocr_text: str, fuzzy_match: bool = False
) -> VerificationResult:
    """
    Verify if the form data matches the OCR text from the label image.

    Args:
        form_data: The form data to verify against
        ocr_text: The OCR text from the image
        fuzzy_match: Whether to use fuzzy matching (default: False)
    """
    if not ocr_text.strip():
        raise ValueError("No text detected in image")

    normalized_ocr = normalize_text(ocr_text)
    normalized_variants = normalize_ocr_text(ocr_text)
    matches = {}
    mismatches = []
    close_matches = {}

    # Check brand name, allows for variants
    success, closest_match = check_brand_name(
        form_data.brand_name, normalized_ocr, normalized_variants, fuzzy_match
    )
    logging.info(f"Brand name result: success={success}, closest={closest_match}")
    matches["brand_name"] = success
    if not success:
        mismatches.append("brand_name")
        if closest_match:
            close_matches["brand_name"] = [closest_match]

    # Check product type, allows for variants
    success, closest_match = check_product_type(
        form_data.product_type, normalized_ocr, normalized_variants, fuzzy_match
    )
    logging.info(f"Product type result: success={success}, closest={closest_match}")
    matches["product_type"] = success
    if not success:
        mismatches.append("product_type")
        if closest_match:
            close_matches["product_type"] = [closest_match]

    # Check alcohol content
    success, closest_match = check_alcohol_content(
        form_data.alcohol_content, normalized_ocr
    )
    matches["alcohol_content"] = success
    if not success:
        mismatches.append("alcohol_content")
        if closest_match:
            close_matches["alcohol_content"] = [closest_match]

    # Check net contents if provided
    if form_data.net_contents:
        success, closest_match = check_net_contents(
            form_data.net_contents, normalized_ocr
        )
        matches["net_contents"] = success
        if not success:
            mismatches.append("net_contents")
            if closest_match:
                close_matches["net_contents"] = [closest_match]

    # Check government warning
    success, closest_match = check_government_warning(normalized_ocr)
    matches["government_warning"] = success
    if not success:
        mismatches.append("government_warning")
        if closest_match:
            close_matches["government_warning"] = [closest_match]

    # Generate human-readable message
    if not mismatches:
        message = "All fields successfully verified on the label"
    else:
        message = "Verification failed for: " + ", ".join(
            f"{field} ({close_matches[field][0]})" if field in close_matches else field
            for field in mismatches
        )

    label_success = len(mismatches) == 0
    return VerificationResult(
        success=label_success,
        matches=matches,
        mismatches=mismatches,
        raw_ocr_text=ocr_text,
        message=message,
        close_matches=close_matches,
        image_info=None,
    )
