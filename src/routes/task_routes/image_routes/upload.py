from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext

router = Router()


# Handle the upload command
@router.message(F.text == '/upload')
async def upload_command(message: Message):
    """"Handle the /upload command"""
    await message.answer(f"Please upload an image of {'...'}.")


# Handle the photo uploads (compressed images)
@router.message(F.photo)
async def handle_photo_upload(message: Message):
    """Handle photo uploads from users"""

    # Get the largest photo size (best quality)
    photo = message.photo[-1]

    # Extract image information
    file_id = photo.file_id
    file_size = photo.file_size
    width = photo.width
    height = photo.height

    # Send confirmation
    await message.answer(
        f"📸 Image received!\n"
    )

# Handle images sent as documents (uncompressed)
@router.message(F.document)
async def handle_document_upload(message: Message):
    """Handle image documents"""
    document = message.document

    # Check if it's an image
    