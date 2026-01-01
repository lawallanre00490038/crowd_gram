import json
from re import sub
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger

from aiogram.types import ReplyKeyboardRemove

from src.constant.task_constants import ContributorTaskStatus, TaskType
from src.handlers.task_handlers.contributor_handler import build_redo_task_message, build_task_message, finalize_submission, process_and_send_task, validate_task
from src.handlers.task_handlers.utils import extract_project_info
from src.models.api2_models.agent import SubmissionModel
from src.models.api2_models.task import SubmissionResult
from src.routes.task_routes.task_formaters import ERROR_MESSAGE

@property
def meta(self):
    raise NotImplementedError

@meta.setter
def meta(self, value):
    raise NotImplementedError

from src.states.tasks import TaskState
from src.responses.task_formaters import SUBMISSION_RECIEVED_MESSAGE

import datetime as dt


from src.keyboards.reply import request_location_keyboard

router = Router()

@router.callback_query(F.data == "start_agent_task")
async def start_task_new(callback: CallbackQuery, state: FSMContext):
    await state.update_data(redo_task=False)
    # await callback.message.answer("You can not start a new task at the moment. Please try again later.")
    await process_and_send_task(
        callback=callback,
        state=state,
        # Default parameters for NEW task
        status_filter=ContributorTaskStatus.ASSIGNED, # Fetching the default available status
        no_tasks_message="No tasks available at the moment. Please check back later.",
        project_not_selected_message="Please select a project first using /projects.",
        build_msg_func=build_task_message,  
        is_redo_task=False,
    )

@router.callback_query(F.data == "skip_agent_task")
async def skip_task_new(callback: CallbackQuery, state: FSMContext):
    user_state = await state.get_data()
    skipped_task = user_state.get("skipped_task", [])
    task_id = user_state.get("task_id")
    skipped_task.append(task_id)

    logger.debug(f"Skipping task ID: {task_id} Skipped tasks so far: {skipped_task}")
        
    await state.update_data(skipped_task=skipped_task)
    
    if user_state.get("redo_task", False):
        await process_and_send_task(
            callback=callback,
            state=state,
            # Specific parameters for REDO task
            status_filter=ContributorTaskStatus.REDO,
            no_tasks_message="No tasks to REDO at the moment...",
            project_not_selected_message="Please select a project first using /start.", # Different message for REDO
            build_msg_func=build_redo_task_message,
            is_redo_task=True,
        )
    else:
        await process_and_send_task(
            callback=callback,
            state=state,
            # Default parameters for NEW task
            status_filter=ContributorTaskStatus.ASSIGNED, # Fetching the default available status
            no_tasks_message="No tasks available at the moment. Please check back later.",
            project_not_selected_message="Please select a project first using /projects.",
            build_msg_func=build_task_message,
            is_redo_task=False,
        )


@router.message(TaskState.waiting_for_submission)
async def handle_submission_input(message: Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        project_info = extract_project_info(user_data)

        if project_info == None:
            return

        # Validate Input
        result = await validate_task(message=message, task_type=project_info.return_type)
        logger.debug(f"Submission validation result: {result}")

        if result == None:
            await message.answer("There is an issue with the task.")
            return

        # If input is not valid 
        if not result.success:
            errors = ERROR_MESSAGE.format(errors=result.response or f"Failed to process {project_info.return_type} submission. Please try again.")
            await message.answer(errors)
            return

        # Validate the Submission
        submission = SubmissionModel.model_validate(user_data)
        submission.type = project_info.return_type
        logger.debug(f"Submission data: {submission}")
        await message.answer(SUBMISSION_RECIEVED_MESSAGE)

        # If the input as text
        if project_info.return_type == TaskType.TEXT:
            if message.text == None:
                await message.answer("Please input a text")
                return

            submission.payload_text = message.text.strip()

        if not project_info.require_geo:
            await finalize_submission(message, submission, result.metadata.get("new_path"), project_info, user_data)

            return
        
        await state.update_data(geo_require_time =  dt.datetime.now().isoformat())
    
        await message.answer("Great! Now click the button below to share your location.", reply_markup=request_location_keyboard)
        await state.update_data(submission = submission.model_dump())
        await state.update_data(new_path = result.metadata.get("new_path"))
        await state.set_state(TaskState.waiting_for_location)

        return
    except Exception as e:
        logger.error(f"Error in handle_audio_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")


@router.message(TaskState.waiting_for_location, F.location)
async def handle_location(message: Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        submission = user_data.get("submission")
        date_object = user_data.get("geo_require_time")
        new_path = user_data.get("new_path")

        if date_object is None:
            message.answer("Time not taken into context")

        if submission is None:
            message.answer("Submission not recieved file Please get task using /start_task")

        if new_path is None:
            message.answer("Result details is not available")

        if message.location == None:
            message.answer("Please supply your live location")
            return  
        
        submission = SubmissionModel.model_validate(submission)
        prev_time = dt.datetime.fromisoformat(str(date_object))
        cur_time = dt.datetime.now()

        if (cur_time - prev_time) > dt.timedelta(seconds=240):
            await message.answer("Wait time exceeded", reply_markup=ReplyKeyboardRemove())
            return

        lat = message.location.latitude
        lon = message.location.longitude
        
        submission.meta = {
            "lat": lat, 
            "lon": lon
        }    
    
        # You now have both! (photo_id, lat, lon)
        await message.answer(
            f" Report Received!\nCoords: {lat}, {lon}",
            reply_markup=ReplyKeyboardRemove()
        )

        project_info = extract_project_info(user_data)

        await finalize_submission(message, submission, new_path, project_info, user_data)
    
        return

    except Exception as e:
        logger.error(f"Error in handle_audio_task_submission: {str(e)}")
        await message.answer("Error occurred, please try again.")