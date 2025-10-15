from typing import List, Any

def reshape_list(lst: List[Any], cols: int) -> List[List[Any]]:
    """
    Reshape a flat list into a list of lists with given number of columns (cols).
    If the last row is incomplete, return it as-is.

    :param lst: The input flat list.
    :param cols: The number of columns per row.
    :return: Reshaped list.
    """
    return [lst[i:i + cols] for i in range(0, len(lst), cols)]
