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
We will review it shortly and notify you of the outcome.
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
✅ Your image for **{theme}** has been received and approved!
Now, please describe this image in **{target_lang}** using {annotation_type}.
Focus on what is happening, the people, objects, and actions you see.
✔ Be detailed and accurate.
✔ Use complete sentences.
❌ Avoid unrelated details.
"""
