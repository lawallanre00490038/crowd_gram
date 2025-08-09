def format_dialects(dialects_dict):
    if not dialects_dict:
        return "N/A"
    
    formatted = []
    for language, dialect in dialects_dict.items():
        formatted.append(f"{language} ({dialect})")
    
    return ", ".join(formatted)