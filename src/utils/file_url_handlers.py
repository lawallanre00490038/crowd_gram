def build_file_section(submission_type: str, file_url: str | None) -> str:
    """
    Generate a formatted file section for reviewer or contributor messages.

    Args:
        submission_type (str): The type of submission ('audio', 'video', 'image', etc.)
        file_url (str | None): The file URL if available.

    Returns:
        str: A formatted section string with appropriate emoji and label.
    """
    if not file_url:
        return ""

    submission_type = (submission_type or "").lower()

    match submission_type:
        case "audio":
            return f'Listen to Submission'
        case "video":
            return f'🎥 <a href="{file_url}">Watch submission</a>  \n\n'
        case "image":
            return f'Verify the Submission'
        case "document" | "pdf":
            return f'📄 <a href="{file_url}">Open document</a> \n\n'
        case _:
            return f'📁 <a href="{file_url}">View file</a> \n\n'


def formdata_to_dict(form_data_keys):
    result = {}
    for item in form_data_keys:
        multidict, _, value = item
        key = multidict.get('name')
        # For files, take the filename if it exists
        if 'filename' in multidict:
            result[key] = multidict['filename']
        else:
            result[key] = value
    return result
