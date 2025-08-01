import os
from PIL import Image
from img_size_check import check_image_file_size_and_resolution 
import numpy as np

def create_dummy_image(path, size=(300, 300)):
    array = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    img = Image.fromarray(array, "RGB")
    img.save(path, format="JPEG")


def test_valid_image(tmp_path):
    img_path = tmp_path / "valid.jpg"
    create_dummy_image(img_path, size=(300, 300))
    size_bytes = os.path.getsize(img_path)
    size_kb = size_bytes / 1024
    print(f"Image size: {size_kb:.2f} KB")

    result = check_image_file_size_and_resolution(str(img_path))
    assert result["exists"]
    assert result["file_size_ok"]
    assert result["resolution_ok"]
    assert not result["file_too_small"]
    assert not result["file_too_large"]
    assert not result["too_small_resolution"]

def test_too_small_resolution(tmp_path):
    img_path = tmp_path / "small.jpg"
    create_dummy_image(img_path, size=(100, 100))
    result = check_image_file_size_and_resolution(str(img_path))
    assert result["too_small_resolution"]
    assert not result["resolution_ok"]

def test_nonexistent_file():
    result = check_image_file_size_and_resolution("nonexistent.jpg")
    assert not result["exists"]
    assert not result["file_size_ok"]
    assert not result["resolution_ok"]
