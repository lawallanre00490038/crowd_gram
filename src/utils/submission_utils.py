from aiogram_dialog import Dialog, DialogManager, Window
from src.states.tasks import TaskState


async def on_score_click(callback, button, dialog_manager: DialogManager):
    score = int(button.widget_id.split("_"[1]))
    data = dialog_manager.dialog_data
    index = data.get('index', 0)
    scores = data.get("scores", {})
    review_params = data.get("review_params", [])
    
    if index < len(review_params):
        param = review_params[index]
        scores[param] = score
        data['scores'] = scores
        
        # Move to next parameter or summary
        if index + 1 < len(review_params):
            data["index"] = index + 1
            await dialog_manager.switch_to(TaskState.scoring)
        else:
            await dialog_manager.switch_to(TaskState.summary)
            


def get_submission_info(data, info_type):
    reviewers_list = data.get("reviewers_list", [])
    if reviewers_list and len(reviewers_list) > 0:
        first_task = reviewers_list[0]
        if hasattr(first_task, 'tasks') and first_task.tasks:
            submission = first_task.tasks[0].submission
            if submission:
                if info_type == "type":
                    return getattr(submission, 'type', 'Unknown')
                elif info_type == "text":
                    return getattr(submission, 'payload_text', 'No text available')[:100] + "..."
    return "N/A"