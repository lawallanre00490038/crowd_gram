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
            return f"🎧 [Listen to submission]({file_url})\n\n"
        case "video":
            return f"🎥 [Watch submission]({file_url})\n\n"
        case "image":
            return f"🖼️ [View image]({file_url})\n\n"
        case "document" | "pdf":
            return f"📄 [Open document]({file_url})\n\n"
        case _:
            return f"📁 [View file]({file_url})\n\n"
