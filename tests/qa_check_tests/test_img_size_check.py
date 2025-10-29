import os
import numpy as np
from PIL import Image

from src.services.quality_assurance.img_size_check import check_image_file_size_and_resolution
from tests.qa_check_tests.utils import create_image


def test_valid_image(tmp_path):
    img_path = tmp_path / "valid.jpg"
    create_image(img_path, size=(300, 300))
    size_bytes = os.path.getsize(img_path)
    size_kb = size_bytes / 1024
    logger.trace(f"Image size: {size_kb:.2f} KB")

    result = check_image_file_size_and_resolution(str(img_path), min_kb=1)
    assert result["exists"]
    assert result["file_size_ok"]
    assert result["resolution_ok"]
    assert not result["file_too_small"]
    assert not result["file_too_large"]
    assert not result["too_small_resolution"]


def test_too_small_resolution(tmp_path):
    img_path = tmp_path / "small.jpg"
    create_image(img_path, size=(100, 100))
    result = check_image_file_size_and_resolution(str(img_path))
    assert result["too_small_resolution"]
    assert not result["resolution_ok"]


def test_nonexistent_file():
    result = check_image_file_size_and_resolution("nonexistent.jpg")
    assert not result["exists"]
    assert not result["file_size_ok"]
    assert not result["resolution_ok"]
