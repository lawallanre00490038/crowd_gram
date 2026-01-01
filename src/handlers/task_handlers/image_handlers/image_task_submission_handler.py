from loguru import logger

from src.models.api2_models.task import SubmissionResult
from src.services.quality_assurance.image_validation import validate_image_input
from src.utils.downloader import download_telegram
from src.utils.image_processing import process_image

async def handle_image_submission(file_id, bot):
    """
    Handles image submission by validating quality, processing, and returning a SubmissionResult.
    """

    # 1. Download image
    file_path = await download_telegram(file_id, bot=bot)

    # 2. Run consolidated validation
    # This now handles blur, entropy, NIQE, and size/resolution in one go
    validation_report = validate_image_input(image_path=file_path)
    
    # Check if validation failed
    if not validation_report["success"]:
        errors = ", ".join(validation_report["fail_reasons"])
        logger.warning(f"Image validation failed: {errors}")
        
        return SubmissionResult(
            success=False,
            response=errors,
            metadata=validation_report["metadata"]
        )

    # 3. Processing (Only if validation passes)
    try:
        # Update metadata with the new path
        final_metadata = validation_report["metadata"]
        final_metadata["new_path"] = file_path

        return SubmissionResult(
            success=True,
            response="Image accepted and passed all checks.",
            metadata=final_metadata
        )
        
    except Exception as e:
        logger.error(f"Error during image processing: {e}")
        return SubmissionResult(
            success=False,
            response=f"Processing error: {str(e)}",
            metadata={"file_path": file_path}
        )
