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