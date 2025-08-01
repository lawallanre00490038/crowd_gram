import os
from PIL import Image

def check_image_file_size_and_resolution(image_path, min_kb=10, max_mb=5, min_width=200, min_height=200):
    """
    Returns a dictionary indicating if the image passes min/max size and resolution checks.
    """
    results = {
        "exists": False,
        "file_size_ok": False,
        "file_too_small": False,
        "file_too_large": False,
        "resolution_ok": False,
        "too_small_resolution": False
    }

    if not os.path.isfile(image_path):
        return results

    results["exists"] = True

    size_bytes = os.path.getsize(image_path)
    size_kb = size_bytes / 1024
    size_mb = size_bytes / (1024 * 1024)

    results["file_too_small"] = size_kb < min_kb
    results["file_too_large"] = size_mb > max_mb
    results["file_size_ok"] = not results["file_too_small"] and not results["file_too_large"]

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            results["resolution_ok"] = width >= min_width and height >= min_height
            results["too_small_resolution"] = not results["resolution_ok"]
    except Exception:
        results["resolution_ok"] = False
        results["too_small_resolution"] = True

    return results
