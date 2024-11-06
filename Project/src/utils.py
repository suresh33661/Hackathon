import random

def read_random_light():
    """Simulate reading random light values (in lux)."""
    return random.randint(0, 1000)  # Simulate light levels between 0 and 1000 lux

def trigger_threshold_alert(psnr_value, threshold=25):
    """Trigger alert if PSNR is below a specified threshold."""
    if psnr_value < threshold:
        print("ALERT: Restoration quality below threshold! Immediate attention required.")
