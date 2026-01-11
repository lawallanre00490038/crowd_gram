from optparse import Option
import os
from loguru import logger


from aiogram.fsm.context import FSMContext
from typing import Optional, Callable, Tuple
from aiogram.types import CallbackQuery, URLInputFile, Message


from src.constant.task_constants import ContributorTaskStatus, TaskType
from src.handlers.task_handlers.audio_task_handler import handle_api2_audio_submission
from src.handlers.task_handlers.image_handlers.image_task_submission_handler import handle_image_submission
from src.handlers.task_handlers.utils import extract_project_info, fetch_user_tasks, set_task_state_by_type, update_state_with_task
from src.keyboards.inline import next_task_inline_kb, skip_task_inline_kb
from src.models.api2_models.agent import ImageAnalysisResponse, SubmissionResponseModel
from src.models.api2_models.projects import ExtractedProjectInfo
from src.models.api2_models.task import SubmissionResult, TaskDetailResponseModel
from src.responses.task_formaters import TASK_MSG
from src.services.quality_assurance.text_validation import validate_text_input
from src.services.server.api2_server.agent_submission import create_submission
from src.states.tasks import TaskState
from src.utils.file_url_handlers import build_file_section


type_map = {
    "text": "Text",
    "audio": "Audio",
    "image": "Image",
    "video": "Video"
}

async def validate_task(message: Message, task_type: TaskType) -> Optional[SubmissionResult]:
    if message.forward_date:
        await message.answer("Forwarded data is not acceptable")
        return 

    if task_type == TaskType.TEXT:
        if message.text == None:
            return SubmissionResult(
                success = False, 
                response = "- YOu did not input a text",
            )
        
        result = validate_text_input(message.text.strip(), task_lang=None, exp_task_script=None)

        return SubmissionResult(
            success=result['success'],
            response="\n * ".join(result['fail_reasons']),
            metadata=result['metadata']
        )
    elif task_type == TaskType.AUDIO:
        return await validate_audio_input(message=message)
    elif task_type == TaskType.IMAGE:
        return await validate_image_input(message=message)

async def validate_image_input(message: Message):
    if not message.photo:
        return SubmissionResult(
                success=False,
                response="Please take a photograph",
                metadata={})
    
    return await handle_image_submission(file_id = message.photo[-1].file_id, bot = message.bot) # type: ignore
    # return await handle_api2_audio_submission(task_info={}, file_id=message.voice.file_id if message.voice else message.audio.file_id, user_id=message.from_user.id, bot=message.bot)

async def validate_audio_input(message: Message):
    if not message.voice:
        return SubmissionResult(
            success=False,
            response="Please record a voice message.",
            metadata={}
        )
    if message.audio != None and message.from_user != None:
        return await handle_api2_audio_submission(task_info={}, file_id=message.voice.file_id if message.voice else message.audio.file_id, user_id=message.from_user.id, bot=message.bot)

async def finalize_submission(
    message,
    submission,
    new_path,
    project_info: ExtractedProjectInfo,
    user_data: dict,
    state
):
    """
    Finalize a submission:
    - Create submission (with or without file)
    - Remove temp file if present
    - Send success / failure messages
    - Handle next task routing

    Returns True on success, False on failure.
    """

    # Create submission
    if new_path:
        submission_response = await create_submission(
            submission, file_path=new_path
        )
    else:
        submission_response = await create_submission(submission)

    # Cleanup temp file
    if new_path and os.path.exists(new_path):
        os.remove(new_path)

    if isinstance(submission_response, ImageAnalysisResponse):
        if not submission_response.success:
            errors = "\n\n".join([f"⚠️ {err.code}\n ━━━━━━━━━━━━━━━\n❌ {err.message}\n💡 {err.instruction}" for err in submission_response.errors])
            
            await message.answer(f"There are some issues with your submission \n\n{errors}", reply_markup=skip_task_inline_kb("agent"))
            
            return False
        
    elif isinstance(submission_response, SubmissionResponseModel):
        if not submission_response:
            await message.answer("Failed to submit your work. Please try again.")
            return False
        else:
            # Success message
            await message.answer(
                f"Your {project_info.return_type} submission has been received and recorded successfully. Thank you!"
            )

            if (project_info.max_submit is not None and project_info.cur_submit is not None):
                logger.debug(f"Max Submit {project_info.max_submit} Cur Submit {project_info.cur_submit} Difference {project_info.max_submit - project_info.cur_submit}")

                if (project_info.max_submit - project_info.cur_submit) <= 1:
                    # Next task logic
                    redo_task = user_data.get("redo_task", False)
                    task_type = "redo" if redo_task else "task"

                    await message.answer(
                        "Begin the next task." if not redo_task else "Begin the next REDO task.",
                        reply_markup=next_task_inline_kb(
                            user_type="agent",
                            task_type=task_type,
                        ),
                    )
                else:
                    await state.update_data(cur_submit = project_info.cur_submit + 1)
                    await message.answer("You another image: " \
                    f"{project_info.cur_submit + 1} of {project_info.max_submit} submitted", 
                    reply_markup=skip_task_inline_kb("agent"))

            return True


# New Reusable Function
async def process_and_send_task(
    callback: CallbackQuery,
    state: FSMContext,
    status_filter: Optional[ContributorTaskStatus] = None, # Used by the REDO task handler
    no_tasks_message: str = "No tasks available at the moment. Please check back later.",
    project_not_selected_message: str = "Please select a project first using /projects.",
    build_msg_func: Optional[Callable[..., Tuple[str, str]]] = None, # build_task_message or build_redo_task_message
    is_redo_task: bool = False,
):
    """
    Handles the common logic for fetching, preparing, and sending a task to the user.
    """
    if build_msg_func is None:
        raise ValueError("build_msg_func must be provided.")

    try:
        user_data = await state.get_data()
        project_info = extract_project_info(user_data)

        if callback.message == None:
            return

        if not project_info:
            await callback.message.answer(project_not_selected_message)
            return

        skipped_task = user_data.get("skipped_task", [])
        # Core difference: Pass the status filter (None for new task, REDO for redo task)
        if status_filter == None:
            await callback.message.answer(project_not_selected_message)
            return
        
        if status_filter == ContributorTaskStatus.ASSIGNED:
            allocations = await fetch_user_tasks(project_info, status=ContributorTaskStatus.NOT_COMPLETED, skip=len(skipped_task))
            if (allocations == None) or (len(allocations) == 0):
                allocations = await fetch_user_tasks(project_info, status=status_filter, skip=len(skipped_task))
        else:
            allocations = await fetch_user_tasks(project_info, status=status_filter, skip=len(skipped_task))
        
        if (allocations == None) or (len(allocations) == 0):
            await callback.message.answer(no_tasks_message)
            return

        first_task = None
        for allocate in allocations:
            if allocate.task_id not in skipped_task:
                first_task = allocate
                break

        if not first_task:
            await callback.message.answer(no_tasks_message)
            return

        # Core difference: Call the appropriate message building function
        task_msg, task_type = build_msg_func(
            first_task, project_info.instruction, project_info.return_type)

        # Core difference: Send the message (handling audio for REDO, but can be used for new tasks too)
        if project_info.return_type == "audio" and first_task.file_url:
            audio_file = URLInputFile(str(first_task.file_url))
            await callback.message.answer_audio(
                caption=task_msg,
                audio=audio_file,
                parse_mode="HTML",
                protect_content=True,
                reply_markup=skip_task_inline_kb("agent"))
        else:
            await callback.message.answer(
                task_msg,
                parse_mode="HTML",
                reply_markup=skip_task_inline_kb("agent")
            )

        # Update state with the task info
        await update_state_with_task(
            state, project_info, first_task, task_type, task_msg, redo_task=is_redo_task
        )
        # await set_task_state_by_type(callback.message, state) # Remove Later
        await state.set_state(TaskState.waiting_for_submission)

    except Exception as e:
        logger.error(f"Error in task processing: {str(e)}")
        if callback.message != None:
            await callback.message.answer("Error occurred, please try again.")

def build_task_message(task: TaskDetailResponseModel, instruction, return_type):
    """Construct the appropriate message for the task type."""

    task_type = type_map.get(return_type)
    if not task_type:
        logger.error(f"Unknown task type for return_type={return_type}")
        task_type = "Unknown"

    task_text = getattr(task, "sentence",
                        "No task content provided.")

    task_msg = TASK_MSG["intro"].format(
        task_type=task_type,
        task_instruction=instruction,
        task_text=task_text,
        max_submit = task.max_submissions_allowed,
        cur_submit = task.current_submission_count
    )
    return task_msg, task_type


def build_redo_task_message(task: TaskDetailResponseModel, instruction, return_type):
    """Construct the appropriate message for the task type."""
    task_type = type_map.get(return_type)
    if not task_type:
        logger.error(f"Unknown task type for return_type={return_type}")
        task_type = "Unknown"

    task_text = getattr(task, "sentence",
                        "No task content provided.")

    # Handle submission type
    if return_type == "text":
        submission = task.sentence
    else:
        submission = build_file_section(
            return_type, task.file_url)

    # Handle missing review object
    reviewer_comments = task.reviewer_comments

    # Ensure reviewer_comments is iterable
    if not reviewer_comments:
        reviewer_comment = "No comments provided."
    elif isinstance(reviewer_comments, str):
        reviewer_comment = reviewer_comments
    elif isinstance(reviewer_comments, (list, set, tuple)):
        reviewer_comment = "\n".join(str(c) for c in reviewer_comments)

    task_msg = TASK_MSG["redo_task"].format(
        task_type=task_type,
        task_instruction=instruction,
        task_text=task_text,
        previous_submission=submission,
        reviewer_comment=reviewer_comment,
        max_submit = task.max_submissions_allowed,
        cur_submit = task.current_submission_count
    )

    return task_msg, task_type