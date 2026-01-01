TEXT_TASK_PROMPT = """<b>Task Type:</b> {task_type}
<b>Language:</b> {required_language} ({required_dialects} dialect)
<b>Deadline:</b> {deadline} (extension possible: {extend_deadline})
<b>Rewards:</b> {rewards}

<b>Instructions:</b>
{task_instructions}

<b>Text to Work On:</b>
{task_description}

Kindly respond with your completed text.
"""

IMAGE_TASK_PROMPT = """<b>Task Type:</b> {task_type}
<b>Language:</b> {required_language} ({required_dialects} dialect)
<b>Deadline:</b> {deadline} (extension possible: {extend_deadline})
<b>Rewards:</b> {rewards}

<b>Instructions:</b>
{task_instructions}

<b>Text to Work On:</b>
{task_description}

Kindly respond with your completed text.
"""

VIDEO_TASK_PROMPT = """<b>Task Type:</b> {task_type}
<b>Language:</b> {required_language} ({required_dialects} dialect)
<b>Deadline:</b> {deadline} (extension possible: {extend_deadline})
<b>Rewards:</b> {rewards}

<b>Instructions:</b>
{task_instructions}

<b>Text to Work On:</b>
{task_description}

Kindly respond with your completed text.
"""

SELECT_TASK_TO_PERFORM = """
📝 <b>Select the type of task you'd like to perform:</b>

🔤 /text_task – Text-based task  
🎙️ /audio_task – Voice-based task  
🖼️ /image_task – Image-based task  
🎥 /video_task – Video-based task  
❌ /exit – Exit the task selection
"""

APPROVED_TASK_MESSAGE = """Your task has been submitted sucessfully! 🎉
You can now proceed to the next task.

/next_task – Start a new task
"""

ERROR_MESSAGE = """
⚠️ <b>There were some issues with your submission:</b>
{errors}
Please review and correct them, then try again.
"""

SUBMISSION_RECIEVED_MESSAGE = """Your submission has been received! 📥
Sit tight while we review your submission...
"""

IMAGE_REQUEST_MESSAGE = """
Awesome! Here's your theme  — share an image and describe it in {target_lang}:\n
---
Theme: {theme}
--\n\n
Describe it using: {annotation_type}
Guide: {question}
Example: {example}\n
Your {target_lang} description:
"""


IMAGE_SUBMISSION_RECEIVED_MESSAGE = """
✅ Image received!
⏳ Status: Submitted for validation
🔔 Next: You'll be notified when reviewed\n\n
"""

IMAGE_REQUEST_ANNOTATION_MESSAGE = """
✅ Your image for <b>{theme}</b> has been received and approved!
Now, please describe this image in <b>{target_lang}</b> using <b>{annotation_type}</b>.
Focus on what is happening, the people, objects, and actions you see.
✔ Be detailed and accurate.
✔ Use complete sentences.
❌ Avoid unrelated details.
"""


TASK_MSG = {
    "intro": (
        "🆕 Your task is <b>{task_type}</b> task!\n\n"
        "Instructions: <i>{task_instruction}</i>\n\n"
        "───────────────────────────────────────────\n"
        "Task Prompt: <b>{task_text}</b>\n"
        "───────────────────────────────────────────\n\n"
        "📝 Please follow the instructions carefully and submit your work when done."
    ),

    "redo_task": (
        "🔁 <b>Redo Required</b>\n\n"
        "🆕 Your task is a <b>{task_type}</b> task that needs revision.\n\n"
        "Instructions: <i>{task_instruction}</i>\n\n"
        "───────────────────────────────────────────\n"
        "Task Prompt: <b>{task_text}</b>\n"
        "───────────────────────────────────────────\n\n"
        "🧾 <b>Your Previous Submission:</b>\n<blockquote>{previous_submission}</blockquote>\n\n"
        "💬 <b>Your Audio contains:</b>\n{reviewer_comment}\n\n"
        "📝 Please revise your work according to the feedback above and resubmit when ready."
    ),

    "reminder": (
        "🔔 Reminder: This is a <b>{task_type}</b> task.\n"
        "Ensure your submission matches the expected format."
    ),

    "audio_instruction": (
        "🎙️ Since this is an *audio* task, make sure your recording is clear, "
        "background noise is minimal, and the sentence is spoken naturally."
    ),

    "text_instruction": (
        "✍️ Since this is a *text* task, double-check for typos and ensure your response "
        "matches the provided prompt."
    ),

    "image_instruction": (
        "🖼️ Since this is an *image* task, please ensure the image is relevant, "
        "clear, and meets the project requirements."
    ),

    "video_instruction": (
        "🎥 Since this is a *video* task, make sure your clip is stable, properly lit, "
        "and matches the task description."
    ),

    "submitted": (
        "✅ Your submission for this <b>{task_type}</b> task has been received successfully!\n"
        "You can move on to your next task."
    ),

    "error": (
        "⚠️ Oops! There was an issue submitting your <b>{task_type}</b> task.\n"
        "Please try again or contact support if the issue persists."
    ),
}


REVIEWER_TASK_MSG = {
    "intro": (
        "🧾 New Submission to Review!\n\n"
        "📂 Project: {project_name}\n"
        "🧠 Task Type: {submission_type}\n"
        "\n"
        "📜 Review Instructions: <b>{reviewer_instruction}</b>\n"
        "───────────────────────────────────────────\n"
        "🗒️ Task Prompt: <b>{payload_text}</b>\n\n"
        " Task Submission: {submission} \n\n"
        "{location_str}"  # Placeholder for the location line
        "───────────────────────────────────────────\n\n\n"
        "Please evaluate the submission carefully and choose an appropriate action."
    ),

    "audio_instruction": (
        "🎧 Since this is an *audio* submission, listen carefully for clarity, "
        "pronunciation accuracy, and background noise quality."
    ),

    "text_instruction": (
        "✍️ Since this is a *text* submission, check for grammar, spelling, and alignment "
        "with the original prompt or task description."
    ),

    "image_instruction": (
        "🖼️ Since this is an *image* submission, review image clarity, relevance, and compliance "
        "with the project’s visual requirements."
    ),

    "video_instruction": (
        "🎥 Since this is a *video* submission, evaluate stability, sound, lighting, and whether "
        "it meets the required scenario or prompt."
    ),

    "reminder": (
        "🔔 Reminder: You still have a pending <b>{submission_type}</b> review.\n"
        "Please complete your review to help keep the workflow on track."
    ),

    "approved": (
        "✅ You have *approved* this <b>{submission_type}</b> submission.\n"
        "The contributor will be notified and credited accordingly."
    ),

    "rejected": (
        "❌ You have *rejected* this <b>{submission_type}</b> submission.\n"
        "Please ensure your rejection includes a short reason or feedback."
    ),

    "changes_requested": (
        "🗣 You have *requested changes* for this <b>{submission_type}</b> submission.\n"
        "The contributor will be notified to revise and resubmit."
    ),

    "error": (
        "⚠️ Oops! Something went wrong while processing your review.\n"
        "Please try again or contact support if the issue persists."
    ),

    "review_summary": (
        "📝 <b>Review Summary:</b>\n\n"
        "{comments}\n\n"
        "✅ Ready to submit?"
    )

}
