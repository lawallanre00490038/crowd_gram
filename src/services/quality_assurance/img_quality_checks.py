import cv2
from PIL import Image
import numpy as np
from scipy.stats import entropy

def sobel_edge_cv2(image):
    # Load image as grayscale float32 between 0–1 (like skimage expects)
    image = image.astype(np.float32) / 255.0

    # Compute Sobel gradients
    sobel_x = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)

    # Compute gradient magnitude
    sobel_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)

    # Normalize result to 0–1 like skimage
    sobel_mag /= sobel_mag.max()

    return sobel_mag


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

        # # Calculate image sharpness using Sobel filter
        sobel = sobel_edge_cv2(img_array)
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

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Audio Quality Check")

    parser.add_argument("file_path", type=str, help="Path to the image file")
    parser.add_argument("--blur_thresh", type=float, default=100.0, help="Threshold for blurriness check")

    args = parser.parse_args()
    file_path = args.file_path

    if not file_path:
        print("Please provide a valid image file path.")
        sys.exit(1)

    try: 
        quality_report = run_image_quality_checks(file_path, blur_thresh=args.blur_thresh)
        print(f"Image Quality Report: {quality_report}")
    except Exception as e:
        print(f"Error processing image file: {e}")
        sys.exit(1)