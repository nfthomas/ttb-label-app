import difflib
import logging
import re
from typing import List, Optional, Set, Tuple

from app.models.verification import LabelData, VerificationResult
from app.services.verification_constants import (
    FIELD_CONFIGS,
    AlcoholContent,
    FieldNames,
    MatchThresholds,
    NetContents,
    TextNormalization,
)


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
    normalized = text.lower()

    # Try each replacement and keep track of variants
    variants = {normalized}
    for old, new in TextNormalization.REPLACEMENTS.items():
        for existing in list(variants):
            if old in existing:
                variants.add(existing.replace(old, new))

    return variants


def find_close_matches(
    target: str, text: str, threshold: float = MatchThresholds.CLOSE_MATCH
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

    # Sort matches by closest similarity and return up to MAX_CLOSE_MATCHES matched strings
    return [
        match
        for match, _ in sorted(matches, key=lambda x: x[1], reverse=True)[
            : MatchThresholds.MAX_CLOSE_MATCHES
        ]
    ]


def check_alcohol_content(
    form_value: float, normalized_ocr: str
) -> Tuple[bool, Optional[str]]:
    """
    Check if the alcohol content appears in the OCR text.
    Returns (success, closest_match).
    """
    content_str = f"{form_value:g}"
    patterns = AlcoholContent.get_patterns(content_str)

    # Check for exact matches
    if any(pattern.search(normalized_ocr) for pattern in patterns):
        return True, None

    # Look for close matches
    matches = AlcoholContent.GENERAL_PATTERN.findall(normalized_ocr)
    if matches:
        closest = matches[0]
        return False, f"{closest}"

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
            brand_name_norm, normalized_ocr, MatchThresholds.FUZZY_MATCH
        )
        if matches:
            return True, None
        # Also check in variants
        for variant in normalized_variants:
            matches = find_close_matches(
                brand_name_norm, variant, MatchThresholds.FUZZY_MATCH
            )
            if matches:
                return True, None
        # No match, find close ones
        close = find_close_matches(
            brand_name_norm, normalized_ocr, MatchThresholds.CLOSE_MATCH
        )
        logging.info(f"Close matches for brand: {close}")
        if not close:
            for variant in normalized_variants:
                close = find_close_matches(
                    brand_name_norm, variant, MatchThresholds.CLOSE_MATCH
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
            product_type_norm, normalized_ocr, MatchThresholds.FUZZY_MATCH
        )
        if matches:
            return True, None
        # Also check in variants
        for variant in normalized_variants:
            matches = find_close_matches(
                product_type_norm, variant, MatchThresholds.FUZZY_MATCH
            )
            if matches:
                return True, None
        # No match, find close ones
        close = find_close_matches(
            product_type_norm, normalized_ocr, MatchThresholds.CLOSE_MATCH
        )
        logging.info(f"Close matches for product_type: {close}")
        if not close:
            for variant in normalized_variants:
                close = find_close_matches(
                    product_type_norm, variant, MatchThresholds.CLOSE_MATCH
                )
                if close:
                    break
        return False, close[0] if close else None
    else:
        success = any(product_type_norm in variant for variant in normalized_variants)
        logging.info(f"Product type exact match: {success}")
        return success, None


def check_government_warning_text(normalized_ocr: str) -> Tuple[bool, Optional[str]]:
    """
    Check if the government warning appears in the OCR text.
    Returns (success, closest_match).
    """
    success = "government warning" in normalized_ocr
    if not success:
        closest = find_close_matches(
            "government warning", normalized_ocr, threshold=MatchThresholds.CLOSE_MATCH
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

    # Check for exact matches using predefined patterns
    patterns = NetContents.get_patterns(form_num, form_unit)
    if any(pattern.search(normalized_ocr) for pattern in patterns):
        return True, None

    # Look for close matches using general pattern
    matches = NetContents.GENERAL_PATTERN.findall(normalized_ocr)
    if matches:
        closest = matches[0]
        return False, f"{closest}"

    return False, None


def verify_label(
    form_data: LabelData,
    ocr_text: str,
    fuzzy_match: bool = False,
    check_government_warning: bool = False,
) -> VerificationResult:
    """
    Verify if the form data matches the OCR text from the label image.

    Args:
        form_data: The form data to verify against
        ocr_text: The OCR text from the image
        fuzzy_match: Whether to use fuzzy matching (default: False)
        check_government_warning: Whether to check for government warning (default: False)
    """
    if not ocr_text.strip():
        raise ValueError("No text detected in image")

    normalized_ocr = normalize_text(ocr_text)
    normalized_variants = normalize_ocr_text(ocr_text)
    matches = {}
    mismatches = []
    close_matches = {}

    # Check brand name
    config = FIELD_CONFIGS[FieldNames.BRAND_NAME]
    success, closest_match = check_brand_name(
        form_data.brand_name,
        normalized_ocr,
        normalized_variants,
        fuzzy_match and config.allows_fuzzy_match,
    )
    logging.info(f"Brand name result: success={success}, closest={closest_match}")
    matches[FieldNames.BRAND_NAME] = success
    if not success:
        mismatches.append(FieldNames.BRAND_NAME)
        if closest_match:
            close_matches[FieldNames.BRAND_NAME] = [closest_match]

    # Check product type
    config = FIELD_CONFIGS[FieldNames.PRODUCT_TYPE]
    success, closest_match = check_product_type(
        form_data.product_type,
        normalized_ocr,
        normalized_variants,
        fuzzy_match and config.allows_fuzzy_match,
    )
    logging.info(f"Product type result: success={success}, closest={closest_match}")
    matches[FieldNames.PRODUCT_TYPE] = success
    if not success:
        mismatches.append(FieldNames.PRODUCT_TYPE)
        if closest_match:
            close_matches[FieldNames.PRODUCT_TYPE] = [closest_match]

    # Check alcohol content
    success, closest_match = check_alcohol_content(
        form_data.alcohol_content, normalized_ocr
    )
    matches[FieldNames.ALCOHOL_CONTENT] = success
    if not success:
        mismatches.append(FieldNames.ALCOHOL_CONTENT)
        if closest_match:
            close_matches[FieldNames.ALCOHOL_CONTENT] = [closest_match]

    # Check net contents if provided
    if form_data.net_contents:
        success, closest_match = check_net_contents(
            form_data.net_contents, normalized_ocr
        )
        matches[FieldNames.NET_CONTENTS] = success
        if not success:
            mismatches.append(FieldNames.NET_CONTENTS)
            if closest_match:
                close_matches[FieldNames.NET_CONTENTS] = [closest_match]

    # Check government warning if requested
    if check_government_warning:
        config = FIELD_CONFIGS[FieldNames.GOVERNMENT_WARNING]
        success, closest_match = check_government_warning_text(normalized_ocr)
        matches[FieldNames.GOVERNMENT_WARNING] = success
        if not success:
            mismatches.append(FieldNames.GOVERNMENT_WARNING)
            if closest_match:
                close_matches[FieldNames.GOVERNMENT_WARNING] = [closest_match]

    # Generate human-readable message with only missing field names
    if not mismatches:
        message = "All fields successfully verified on the label"
    else:
        missing_names = [FIELD_CONFIGS[field].name for field in mismatches]
        message = "Verification failed for: " + ", ".join(missing_names)

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
