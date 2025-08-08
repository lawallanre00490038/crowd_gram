from PIL import Image
from io import BytesIO

def resize_image(image_bytes, size=(512, 512)):
    image = Image.open(BytesIO(image_bytes))
    image = image.convert("RGB")
    image = image.resize(size)
    output = BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    return output.getvalue()


def process_image(image_bytes):
    return resize_image(image_bytes) 