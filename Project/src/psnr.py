import numpy as np

def PSNR(original, compressed):
    """Calculate Peak Signal-to-Noise Ratio (PSNR)."""
    mse = np.mean((original - compressed) ** 2)
    if mse == 0:  # No noise present in the signal
        return 100
    max_pixel = 255.0
    return 20 * np.log10(max_pixel / np.sqrt(mse))
