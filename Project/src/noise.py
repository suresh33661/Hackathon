import numpy as np

def apply_gaussian_noise(image, degradation_level):
    """Apply Gaussian noise to an image."""
    mean = 0
    sigma = degradation_level  # Standard deviation controls the noise level
    gauss = np.random.normal(mean, sigma, image.shape)  # Generate Gaussian noise
    noisy_image = image + gauss  # Add noise to the image
    return np.clip(noisy_image, 0, 255).astype(np.uint8)
