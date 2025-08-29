def extract_option(callback_data: str, options: list) -> str:
    """
    Given callback_data like 'opt_1', 'opt_2', etc., and a list of options,
    return the actual option string that was selected.
    """
    if callback_data.startswith('opt_'):
        try:
            idx = int(callback_data.split('_')[1])
            return options[idx]
        except (IndexError, ValueError):
            return ''
    return ''
