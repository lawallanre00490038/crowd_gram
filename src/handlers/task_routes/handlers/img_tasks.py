from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import Message
from states import ImageTaskSubmission
from db.mongo import submissions
from .image_validation import validate_image_input  

router = Router()

@router.message(StateFilter(ImageTaskSubmission.waiting_for_image))
async def handle_image_input(message: Message, state: FSMContext):
    image_file = None

   

    # If sent as a photo (Telegram auto-compressed image)
    if message.photo:
        image_file = message.photo[-1]  # Highest resolution

    # If sent as a document with mime type = image/*
    elif message.document and message.document.mime_type.startswith("image/"):
        image_file = message.document

    # Not a supported image
    else:
        await message.answer("⚠️ Please upload a valid image (JPG, PNG, or WEBP).")
        return

    # Download the image
    file_info = await message.bot.get_file(image_file.file_id)
    file_path = file_info.file_path
    local_path = f"media/images/{image_file.file_id}.jpg"  # You can preserve original ext if needed

    await message.bot.download_file(file_path, destination=local_path)

    # Continue with validation
    result = validate_image_input(local_path)

    if result["success"]:
        await message.answer("Image submitted successfully.\n\nTo get the next task, type /next.")
        data = await state.get_data()
        task_id = data.get("task_id")
        user_id = message.from_user.id

        await submissions.insert_one({
            "user_id": user_id,
            "task": f"Image task ({task_id})",
            "image_path": local_path,
            "type": "image",
            "status": "submitted",
            "metadata": result["metadata"]
        })
        await state.clear()
    else:
        await message.answer(
            "Image failed the quality check:\n\n" +
            "\n".join(f"• {reason}" for reason in result["fail_reasons"])
        )
