from aiogram import Router, types

router = Router()


@router.message()
async def handle_forwarded_message(message: types.Message):
    if message.forward_from_chat:
        logger.trace("CHANNEL ID:", message.forward_from_chat.id)
        await message.reply(f"Channel ID is: {message.forward_from_chat.id}")
    else:
        await message.reply("This is not a forwarded channel message.")
