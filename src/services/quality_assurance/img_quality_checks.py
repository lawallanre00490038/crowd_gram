import cv2
from PIL import Image
import numpy as np
from scipy.stats import entropy
import torch
import torchvision.transforms as T
from skimage import filters, measure


def is_blurry(image_path, threshold=100.0):
    """
    Check if image is blurry using Laplacian variance.
    Lower variance = more blur.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return True
    variance = cv2.Laplacian(image, cv2.CV_64F).var()
    return bool (variance < threshold)


def image_entropy(image_path):
    """
    Estimate compression/noise by measuring entropy of the image histogram.
    Low entropy may indicate poor quality or blank images.
    """
    try:
        with Image.open(image_path) as img:
            histogram = img.histogram()
            histogram = np.array(histogram) / sum(histogram)
            return entropy(histogram)
    except Exception:
        return 0.0


def calculate_niqe_score(image_path):
    """
    Estimate image quality using image sharpness metrics.
    """
    try:
        image = Image.open(image_path).convert("L")  # Convert to grayscale
        img_array = np.array(image)
        
        # Calculate image sharpness using Sobel filter
        sobel = filters.sobel(img_array)
        sharpness = np.mean(sobel)
        
        # Convert to NIQE-like score (lower = better)
        return 1 / (1 + sharpness) if sharpness > 0 else float("inf")
        
    except Exception:
        return float("inf")


def run_image_quality_checks(image_path, blur_thresh=100.0):
    """
    Run all image quality checks and return a report.
    """
    return {
        "blurry": is_blurry(image_path, threshold=blur_thresh),
        "entropy": image_entropy(image_path),
        "niqe_score": calculate_niqe_score(image_path)
    }
