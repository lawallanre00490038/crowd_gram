import cv2
import pytest
import numpy as np
from src.services.quality_assurance.img_quality_checks import (
    is_blurry,
    image_entropy,
    calculate_niqe_score,
    run_image_quality_checks
)
from tests.qa_check_tests.utils import create_image, create_corrupted_image, create_unreadable_text_file

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

    image = cv2.imread(path)
    
    assert is_blurry(image, threshold=threshold) == expected

@pytest.mark.parametrize("noise, min_entropy", [
    (False, 0.0),
    (True, 2.0),
])
def test_image_entropy_levels(tmp_path, noise, min_entropy):
    path = tmp_path / f"entropy_{noise}.jpg"
    create_image(path, noise=noise)

    image = cv2.imread(path)
    entropy_val = image_entropy(image)

    assert entropy_val >= min_entropy

@pytest.mark.parametrize("noise", [True, False])
def test_niqe_score_output_type(tmp_path, noise):
    path = tmp_path / f"niqe_{noise}.jpg"
    create_image(path, noise=noise)

    image = cv2.imread(path)
    score = calculate_niqe_score(image)

    print(score)

    assert isinstance(score, (float, np.floating))
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
    assert isinstance(report["entropy"], (float, np.floating))
    assert isinstance(report["niqe_score"], (float, np.floating))

# -----------------------------
# Corrupted Image Tests
# -----------------------------

def test_is_blurry_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)

    image = cv2.imread(path)
    assert is_blurry(image) is True

def test_image_entropy_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    
    create_corrupted_image(path)
    image = cv2.imread(path)

    assert image_entropy(image) == 0.0

def test_niqe_score_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)

    image = cv2.imread(path)
    assert calculate_niqe_score(image) == float("inf")

def test_run_image_quality_checks_corrupted(tmp_path):
    path = tmp_path / "corrupt.jpg"
    create_corrupted_image(path)

    image = cv2.imread(path)
    report = run_image_quality_checks(image)
    assert report["blurry"] is True
    assert report["entropy"] == 0.0
    assert report["niqe_score"] == float("inf")

# -----------------------------
# Unreadable Format Tests
# -----------------------------

def test_image_entropy_unreadable_format(tmp_path):
    path = tmp_path / "fake.jpg"
    create_unreadable_text_file(path)
    
    image = cv2.imread(path)

    assert image_entropy(image) == 0.0

def test_niqe_score_unreadable_format(tmp_path):
    path = tmp_path / "fake.jpg"
    create_unreadable_text_file(path)
    
    image = cv2.imread(path)

    assert calculate_niqe_score(image) == float("inf")

# -----------------------------
# Missing File Safety Tests
# -----------------------------

def test_missing_file_safe_handling():
    fake_path = "nonexistent_image.jpg"

    image = cv2.imread(fake_path)

    assert is_blurry(image) is True
    assert image_entropy(image) == 0.0
    assert calculate_niqe_score(image) == float("inf")
    report = run_image_quality_checks(fake_path)
    assert report["blurry"] is True
    assert report["entropy"] == 0.0
    assert report["niqe_score"] == float("inf")
