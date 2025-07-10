def validate_phone(phone):
    # Simple phone validation
    return phone.isdigit() and len(phone) >= 10
