from typing import Dict, Any, List
import logging

from .img_quality_checks import (
    is_blurry,
    image_entropy,
    calculate_niqe_score,
   
 
)

from .img_size_check import check_image_file_size_and_resolution 

logger = logging.getLogger("image_validator")

def validate_image_input(image_path: str,
                         entropy_threshold: float = 3.5,
                         niqe_threshold: float = 6.0) -> Dict[str, Any]:
    """
    Validate a given image file against quality criteria.

    Args:
        image_path (str): Path to the image file.
        entropy_threshold (float): Minimum entropy threshold to consider image non-blank.
        niqe_threshold (float): Maximum NIQE threshold for acceptable quality.

    Returns:
        dict: {
            "success": bool,
            "fail_reasons": list[str],
            "metadata": dict[str, any]
        }
    """
    fail_reasons: List[str] = []
    metadata: Dict[str, Any] = {}

    # --- 1. Blur Check ---
    try:
        blurry = is_blurry(image_path)
        metadata["is_blurry"] = blurry
        if blurry:
            fail_reasons.append("Image is too blurry.")
    except Exception as e:
        logger.warning(f"Blur check failed: {e}")

    # --- 2. Entropy Check ---
    try:
        entropy = image_entropy(image_path)
        metadata["entropy"] = entropy
        if entropy < entropy_threshold:
            fail_reasons.append(f"Image entropy too low ({entropy:.2f} < {entropy_threshold}).")
    except Exception as e:
        logger.warning(f"Entropy check failed: {e}")

    # --- 3. NIQE Score ---
    try:
        niqe = calculate_niqe_score(image_path)
        metadata["niqe_score"] = niqe
        if niqe > niqe_threshold:
            fail_reasons.append(f"NIQE score too high ({niqe:.2f} > {niqe_threshold}).")
    except Exception as e:
        logger.warning(f"NIQE check failed: {e}")



    # --- 5. File Size and Resolution ---
    try:
        size_check = check_image_file_size_and_resolution(image_path)
        metadata.update(size_check)
        if size_check.get("file_too_small"):
            fail_reasons.append("File size is too small.")
        if size_check.get("pixel_too_small"):
            fail_reasons.append("Image resolution is too low.")
    except Exception as e:
        logger.warning(f"Size/resolution check failed: {e}")

    return {
        "success": len(fail_reasons) == 0,
        "fail_reasons": fail_reasons,
        "metadata": metadata
    }
