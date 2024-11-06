import numpy as np

def adjust_brightness_contrast(image, brightness_factor=1.0, contrast_factor=1.0):
    """Adjust brightness and contrast of an image."""
    img_float = image.astype(np.float32)
    img_float = img_float * brightness_factor
    img_float = np.clip(img_float, 0, 255)  # Clip values to valid range
    
    # Adjust contrast
    img_float = ((img_float - 127.5) * contrast_factor) + 127.5
    return np.clip(img_float, 0, 255).astype(np.uint8)
