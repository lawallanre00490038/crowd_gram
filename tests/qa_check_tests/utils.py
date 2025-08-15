import os
import numpy as np
from PIL import Image

def create_image(path, size=(300, 300), noise=False):
    if noise:
        array = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    else:
        array = np.ones((size[1], size[0], 3), dtype=np.uint8) * 127
    img = Image.fromarray(array)
    img.save(path)

def create_corrupted_image(path):
    with open(path, "wb") as f:
        f.write(b"This is not a valid image file")

def create_unreadable_text_file(path):
    with open(path, "w") as f:
        f.write("This is just a text file, not an image.")
