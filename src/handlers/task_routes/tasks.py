from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
# from src.services.task_distributor import assign_task
from src.states.tasks import TaskState

router = Router()

@router.message(F.text == "/welcome")
async def cmd_welcome(message: Message):
    await message.answer("Welcome to the task portal!")

@router.message(F.text == "/status")
async def cmd_status(message: Message):
    # Fetch and display agent's status
    await message.answer("Your task status: ...")

@router.message(TaskState.waiting_for_submission)
async def handle_submission(message: Message, state: FSMContext):
    # Validate and save submission
    await message.answer("Submission received. Processing QA...")
    await state.clear()