import pytesseract #This is a Python "wrapper." It doesn’t actually do the reading itself; instead, it sends the image to a powerful engine called Tesseract OCR (originally developed by HP and now maintained by Google) and brings the results back to Python.
from PIL import Image #This comes from the Pillow library. It is the standard tool in Python for opening and manipulating image files (JPG, PNG, etc.).


def extract_text(image: Image.Image):
    return pytesseract.image_to_string(image)
#image: Image.Image: This is a type hint. It tells other developers (and your code editor) that the input should be a loaded Pillow image object, not just a filename string.
#image_to_string: This is the most common function in the library. It takes the pixels, analyzes the shapes of the characters using a neural network, and returns a single Python string containing all the text it found.