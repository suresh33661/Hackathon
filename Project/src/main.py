import cv2
import numpy as np
import serial
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import json
import os

# Import custom functions for brightness adjustment and noise application
from brightness import adjust_brightness_contrast
from noise import apply_gaussian_noise

# Serial port configuration
SERIAL_PORT = "COM8"
BAUD_RATE = 9600

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

degradation_level = 25

def read_sensor_values():
    """Read sensor values from Arduino."""
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print(f"Raw data received: {line}")
        if line.startswith("Light:"):
            try:
                line = line.replace("Light:", "").replace("Temperature:", "").replace("Humidity:", "")
                ldr_value, temp_value, humidity_value = map(float, line.split(','))
                return ldr_value, temp_value, humidity_value
            except ValueError:
                print("Error parsing data. Invalid format.")
    return None

# Create a unique folder based on the current date and time for logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = os.path.join("logs", f"session_{timestamp}")
os.makedirs(log_dir, exist_ok=True)

# Path to save the JSON log file in the unique folder
log_file_path = os.path.join(log_dir, "log.json")

def log_data(sensor_values, original_frame, noisy_frame, restored_frame, psnr_value):
    """Log sensor values and frame data to a JSON file."""
    log_entry = {
        "sensor_values": sensor_values,
        "original_frame": original_frame.tolist(),
        "noisy_frame": noisy_frame.tolist(),
        "restored_frame": restored_frame.tolist(),
        "psnr": psnr_value,
        "timestamp": time.time()
    }
    
    try:
        with open(log_file_path, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")
        print(f"Log entry successfully written to {log_file_path}")
    except Exception as e:
        print(f"Failed to write log entry: {e}")

cap = cv2.VideoCapture(0)

def calculate_psnr(original, compared):
    """Calculate PSNR between two images."""
    mse = np.mean((original - compared) ** 2)
    if mse == 0:
        return 100
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

# GUI setup
root = tk.Tk()
root.title("Automotive Image Restoration and Driver Alert System")
root.geometry("1200x800")

# Sensor value labels
temperature_label = ttk.Label(root, text="Temperature: -- °C", background="lightblue", font=("Helvetica", 12, "bold"))
temperature_label.pack(pady=10, padx=15)
humidity_label = ttk.Label(root, text="Humidity: -- %", background="lightgreen", font=("Helvetica", 12, "bold"))
humidity_label.pack(pady=10, padx=15)
light_label = ttk.Label(root, text="Light Level: -- lux", background="lightyellow", font=("Helvetica", 12, "bold"))
light_label.pack(pady=10, padx=15)

# Image display frames
image_frame = ttk.Frame(root)
image_frame.pack(pady=20)

original_frame_widget = ttk.Frame(image_frame, borderwidth=2, relief="groove", padding=5)
original_frame_widget.grid(row=0, column=0, padx=10)
original_image_label = ttk.Label(original_frame_widget)
original_image_label.pack()
original_label = ttk.Label(original_frame_widget, text="Original")
original_label.pack()

noisy_frame_widget = ttk.Frame(image_frame, borderwidth=2, relief="groove", padding=5)
noisy_frame_widget.grid(row=0, column=1, padx=10)
noisy_image_label = ttk.Label(noisy_frame_widget)
noisy_image_label.pack()
noisy_label = ttk.Label(noisy_frame_widget, text="Noisy")
noisy_label.pack()

restored_frame_widget = ttk.Frame(image_frame, borderwidth=2, relief="groove", padding=5)
restored_frame_widget.grid(row=0, column=2, padx=10)
restored_image_label = ttk.Label(restored_frame_widget)
restored_image_label.pack()
restored_label = ttk.Label(restored_frame_widget, text="Restored")
restored_label.pack()

psnr_label = ttk.Label(root, text="PSNR: -- dB", background="lightgray")
psnr_label.pack(pady=10)

alert_label = ttk.Label(root, text="", background="white")
alert_label.pack(pady=10)

def update_gui(frame, noisy_frame, restored_frame):
    """Update GUI with sensor values and images."""
    sensor_values = read_sensor_values()
    
    if sensor_values:
        light_level, temperature, humidity = sensor_values
        
        # Update sensor labels in GUI
        temperature_label.config(text=f"Temperature: {temperature:.2f} °C")
        humidity_label.config(text=f"Humidity: {humidity:.2f} %")
        light_label.config(text=f"Light Level: {light_level} lux")

        # Convert OpenCV images from BGR to RGB for display in Tkinter
        original_image_rgb = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_BGR2RGB)
        original_image_pil = Image.fromarray(original_image_rgb).resize((frame.shape[1] // 3, frame.shape[0] // 3))
        original_image_label.image = ImageTk.PhotoImage(original_image_pil)
        original_image_label.config(image=original_image_label.image)

        noisy_image_rgb = cv2.cvtColor(noisy_frame.astype(np.uint8), cv2.COLOR_BGR2RGB)
        noisy_image_pil = Image.fromarray(noisy_image_rgb).resize((frame.shape[1] // 3, frame.shape[0] // 3))
        noisy_image_label.image = ImageTk.PhotoImage(noisy_image_pil)
        noisy_image_label.config(image=noisy_image_label.image)

        restored_image_rgb = cv2.cvtColor(restored_frame.astype(np.uint8), cv2.COLOR_BGR2RGB)
        restored_image_pil = Image.fromarray(restored_image_rgb).resize((frame.shape[1] // 3, frame.shape[0] // 3))
        restored_image_label.image = ImageTk.PhotoImage(restored_image_pil)
        restored_image_label.config(image=restored_image_label.image)

        # Calculate PSNR between original and noisy images
        psnr_value = calculate_psnr(frame.astype(np.float32), noisy_frame.astype(np.float32))
        psnr_label.config(text=f"PSNR (Original vs Noisy): {psnr_value:.2f} dB")

        # Trigger alert if PSNR is below a threshold
        if psnr_value < 30:
            alert_label.config(text="Poor Visibility Detected! Drive with Caution", foreground="red", background="yellow")
        else:
            alert_label.config(text="Visibility is clear. Drive safely", foreground="green", background="lightgreen")

def capture_and_process_frame():
    """Capture frame from camera and process it."""
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return
    
    # Read sensor data from Arduino
    sensor_values = read_sensor_values()
    
    if sensor_values:
        light_level, temperature, humidity = sensor_values
        
        # Adjust brightness and contrast based on light level
        if light_level < 50:
            brightness_factor, contrast_factor = 1.5, 1.2
        elif light_level < 200:
            brightness_factor, contrast_factor = 1.0, 1.0
        else:
            brightness_factor, contrast_factor = 0.8, 0.8
        
        adjusted_frame = adjust_brightness_contrast(frame.copy(), brightness_factor=brightness_factor,
                                                     contrast_factor=contrast_factor)
        
        noisy_frame = apply_gaussian_noise(adjusted_frame.copy(), degradation_level)
        
        restored_frame = cv2.fastNlMeansDenoisingColored(noisy_frame.copy(), None,
                                                         h=10,
                                                         hColor=10,
                                                         templateWindowSize=7,
                                                         searchWindowSize=21)

        # Update GUI with new images and sensor values
        update_gui(frame.copy(), noisy_frame.copy(), restored_frame.copy())
        
        # Log the data for analysis
        log_data(sensor_values=sensor_values,
                  original_frame=frame,
                  noisy_frame=noisy_frame,
                  restored_frame=restored_frame,
                  psnr_value=np.round(calculate_psnr(frame.astype(np.float32), noisy_frame.astype(np.float32)), 2))

capture_button = ttk.Button(root, text="Capture and Process", command=capture_and_process_frame)
capture_button.pack(pady=20)

root.mainloop()

cap.release()
ser.close()