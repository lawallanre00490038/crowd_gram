from PIL import Image, ImageEnhance
from io import BytesIO

def resize_image(image_input, size=(512, 512)):
    # Handle both bytes and PIL.Image
    if isinstance(image_input, bytes):
        image = Image.open(BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        image = image_input
    else:
        raise TypeError("Expected bytes or PIL.Image")
    
    # Convert, resize, enhance
    image = image.convert("RGB")
    image = image.resize(size)
    enchancer = ImageEnhance.Sharpness(image)
    image = enchancer.enhance(2.0)
    return image


def process_image(image_bytes):
    return resize_image(image_bytes) 