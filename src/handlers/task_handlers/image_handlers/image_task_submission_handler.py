from loguru import logger
from PIL import Image, ImageEnhance

from src.services.quality_assurance.image_validation import validate_image_input
from src.services.quality_assurance.img_quality_checks import run_image_quality_checks
from src.services.quality_assurance.img_size_check import check_image_file_size_and_resolution
from src.services.task_distributor import assign_task, get_full_task_detail, Task
from src.utils.downloader import download_telegram
from src.utils.image_processing import process_image
from src.constant.auth_constants import TOKEN_LOCATION


async def handle_image_submission(task_info, file_id, user_id, bot):
    """
    Handles the image submission for a given task.

    Args:
        task (Task): The task object containing details about the image task.
    """
    task_info = Task(**task_info)
    task_full_details = await get_full_task_detail(task_info.task_id, user_id)

    file_path = await download_telegram(file_id, bot=bot)

    # Validate image input
    is_valid, validation_msg = validate_image_input(image_path=file_path)
    if not is_valid:
        logger.warning(f"Image validation failed: {validation_msg}")
        return {"status": "error", "message": f"Image validation failed: {validation_msg}"}

    # Check image file size and resolution
    size_ok, size_msg = check_image_file_size_and_resolution(
        image_path=file_path)
    if not size_ok:
        logger.warning(f"Image size/resolution check failed: {size_msg}")
        return {"status": "error", "message": f"Image size/resolution check failed: {size_msg}"}

    # Run image quality checks
    quality_ok, quality_msg = run_image_quality_checks(image_path=file_path)
    if not quality_ok:
        logger.warning(f"Image quality check failed: {quality_msg}")
        return {"status": "error", "message": f"Image quality check failed: {quality_msg}"}

    image = Image.open(file_path)

    new_image = process_image(image)

    new_path = file_path.replace(".jpg", "_enhanced.jpg")
    new_image.save(new_path)
    logger.info(f"New image saved at {new_path}")

    logger.info("Image passed all checks.")
    return {"status": "success", "message": "Image accepted and passed all checks."}
