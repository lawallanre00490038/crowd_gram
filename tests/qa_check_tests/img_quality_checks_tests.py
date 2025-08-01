import os
import numpy as np
from pathlib import Path
from PIL import Image
import pytest
from img_quality_checks import (
    is_blurry,
    image_entropy,
    calculate_niqe_score,
    run_image_quality_checks
)

# -----------------------------
# Helper Functions
# -----------------------------

def create_image(path, size=(300, 300), noise=False):
    if noise:
        array = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    else:
        array = np.ones((size[1], size[0], 3), dtype=np.uint8) * 127
    img = Image.fromarray(array, 'RGB')
    img.save(path)

def create_corrupted_image(path):
    with open(path, "wb") as f:
        f.write(b"This is not a valid image file")

def create_unreadable_text_file(path):
    with open(path, "w") as f:
        f.write("This is just a text file, not an image.")

# -----------------------------
# Parametrized Unit Tests
# -----------------------------

@pytest.mark.parametrize("noise, threshold, expected", [
    (False, 500, True),   # blurry
    (True, 50, False),    # sharp
])
def test_is_blurry(tmp_path, noise, threshold, expected):
    path = tmp_path / f"blur_{noise}.jpg"
    create_image(path, noise=noise)
    assert is_blurry(str(path), threshold=threshold) == expected

@pytest.mark.parametrize("noise, min_entropy", [
    (False, 0.0),
    (True, 2.0),
])
def test_image_entropy_levels(tmp_path, noise, min_entropy):
    path = tmp_path / f"entropy_{noise}.jpg"
    create_image(path, noise=noise)
    entropy_val = image_entropy(str(path))
    assert entropy_val >= min_entropy

@pytest.mark.parametrize("noise", [True, False])
def test_niqe_score_output_type(tmp_path, noise):
    path = tmp_path / f"niqe_{noise}.jpg"
    create_image(path, noise=noise)
    score = calculate_niqe_score(str(path))
    assert isinstance(score, float)
    assert score > 0

# -----------------------------
# Integration Test
# -----------------------------

def test_run_image_quality_checks(tmp_path):
    path = tmp_path / "full_check.jpg"
    create_image(path, noise=True)
    report = run_image_quality_checks(str(path))
    assert isinstance(report, dict)
    assert all(k in report for k in ["blurry", "entropy", "niqe_score"])
    assert isinstance(report["blurry"], bool)
    assert isinstance(report["entropy"], float)
    assert isinstance(report["niqe_score"], float)

# -----------------------------
# Corrupted Image Tests
# -----------------------------

def test_is_blurry_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)
    assert is_blurry(str(path)) is True

def test_image_entropy_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)
    assert image_entropy(str(path)) == 0.0

def test_niqe_score_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)
    assert calculate_niqe_score(str(path)) == float("inf")

def test_run_image_quality_checks_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)
    report = run_image_quality_checks(str(path))
    assert report["blurry"] is True
    assert report["entropy"] == 0.0
    assert report["niqe_score"] == float("inf")

# -----------------------------
# Unreadable Format Tests
# -----------------------------

def test_image_entropy_unreadable_format(tmp_path):
    path = tmp_path / "fake.jpg"
    create_unreadable_text_file(path)
    assert image_entropy(str(path)) == 0.0

def test_niqe_score_unreadable_format(tmp_path):
    path = tmp_path / "fake.jpg"
    create_unreadable_text_file(path)
    assert calculate_niqe_score(str(path)) == float("inf")

# -----------------------------
# Missing File Safety Tests
# -----------------------------

def test_missing_file_safe_handling():
    fake_path = "nonexistent_image.jpg"
    assert is_blurry(fake_path) is True
    assert image_entropy(fake_path) == 0.0
    assert calculate_niqe_score(fake_path) == float("inf")
    report = run_image_quality_checks(fake_path)
    assert report["blurry"] is True
    assert report["entropy"] == 0.0
    assert report["niqe_score"] == float("inf")
