from aiogram.fsm.state import StatesGroup, State

class AnnotationStates(StatesGroup):
    start = State()    # Welcome or entry point
    task_image_sent = State()     # Send the main image for annotation
    awaiting_annotation = State() # Wait for text or audio response
    confirmation = State()  # Confirm submission
    done = State() # End or offer another task

