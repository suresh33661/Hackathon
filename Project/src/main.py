import cv2
import numpy as np
import serial
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
from brightness import adjust_brightness_contrast
from noise import apply_gaussian_noise

SERIAL_PORT = "COM8"
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

degradation_level = 25

def read_sensor_values():
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

cap = cv2.VideoCapture(0)

def calculate_psnr(original, compared):
    mse = np.mean((original - compared) ** 2)
    if mse == 0:
        return 100
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

root = tk.Tk()
root.title("Automotive Image Restoration and Driver Alert System")
root.geometry("1200x800")

temperature_label = ttk.Label(root, text="Temperature: -- °C", background="lightblue", font=("Helvetica", 12, "bold"))
temperature_label.pack(pady=10, padx=15)
temperature_label.config(borderwidth=2, relief="solid", padding=(10, 5))

humidity_label = ttk.Label(root, text="Humidity: -- %", background="lightgreen", font=("Helvetica", 12, "bold"))
humidity_label.pack(pady=10, padx=15)
humidity_label.config(borderwidth=2, relief="solid", padding=(10, 5))

light_label = ttk.Label(root, text="Light Level: -- lux", background="lightyellow", font=("Helvetica", 12, "bold"))
light_label.pack(pady=10, padx=15)
light_label.config(borderwidth=2, relief="solid", padding=(10, 5))

image_frame = ttk.Frame(root)
image_frame.pack(pady=20)

original_frame = ttk.Frame(image_frame, borderwidth=2, relief="groove", padding=5)
original_frame.grid(row=0, column=0, padx=10)
original_image_label = ttk.Label(original_frame)
original_image_label.pack()
original_label = ttk.Label(original_frame, text="Original")
original_label.pack()

noisy_frame = ttk.Frame(image_frame, borderwidth=2, relief="groove", padding=5)
noisy_frame.grid(row=0, column=1, padx=10)
noisy_image_label = ttk.Label(noisy_frame)
noisy_image_label.pack()
noisy_label = ttk.Label(noisy_frame, text="Noisy")
noisy_label.pack()

restored_frame = ttk.Frame(image_frame, borderwidth=2, relief="groove", padding=5)
restored_frame.grid(row=0, column=2, padx=10)
restored_image_label = ttk.Label(restored_frame)
restored_image_label.pack()
restored_label = ttk.Label(restored_frame, text="Restored")
restored_label.pack()

psnr_label = ttk.Label(root, text="PSNR: -- dB", background="lightgray")
psnr_label.pack(pady=10)

alert_label = ttk.Label(root, text="", background="white")
alert_label.pack(pady=10)

def update_gui(frame, noisy_frame, restored_frame, temperature, humidity, light_level):
    # Update sensor values
    temperature_label.config(text=f"Temperature: {temperature:.2f} °C")
    humidity_label.config(text=f"Humidity: {humidity:.2f} %")
    light_label.config(text=f"Light Level: {light_level} lux")

    # Convert OpenCV images from BGR to RGB for display in Tkinter
    original_image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    original_image_pil = Image.fromarray(original_image_rgb).resize((frame.shape[1] // 3, frame.shape[0] // 3))
    original_image_label.image = ImageTk.PhotoImage(original_image_pil)
    original_image_label.config(image=original_image_label.image)

    noisy_image_rgb = cv2.cvtColor(noisy_frame, cv2.COLOR_BGR2RGB)
    noisy_image_pil = Image.fromarray(noisy_image_rgb).resize((frame.shape[1] // 3, frame.shape[0] // 3))
    noisy_image_label.image = ImageTk.PhotoImage(noisy_image_pil)
    noisy_image_label.config(image=noisy_image_label.image)

    restored_image_rgb = cv2.cvtColor(restored_frame, cv2.COLOR_BGR2RGB)
    restored_image_pil = Image.fromarray(restored_image_rgb).resize((frame.shape[1] // 3, frame.shape[0] // 3))
    restored_image_label.image = ImageTk.PhotoImage(restored_image_pil)
    restored_image_label.config(image=restored_image_label.image)

    # Calculate PSNR between original and noisy images
    psnr_value = calculate_psnr(frame, noisy_frame)
    psnr_label.config(text=f"PSNR (Original vs Noisy): {psnr_value:.2f} dB")

    # Trigger alert if PSNR is below a threshold
    if psnr_value < 30:
        alert_label.config(text="Poor Visibility Detected! Drive with Caution", foreground="red", background="yellow")
    else:
        alert_label.config(text="Visibility is clear. Drive safely", foreground="green", background="lightgreen")
def capture_and_process_frame():
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return
    sensor_values = read_sensor_values()
    if sensor_values:
        light_level, temperature, humidity = sensor_values
        if light_level < 50:
            brightness_factor, contrast_factor = 1.5, 1.2
        elif light_level < 200:
            brightness_factor, contrast_factor = 1.0, 1.0
        else:
            brightness_factor, contrast_factor = 0.8, 0.8
        adjusted_frame = adjust_brightness_contrast(frame, brightness_factor, contrast_factor)
        noisy_frame = apply_gaussian_noise(adjusted_frame, degradation_level)
        restored_frame = cv2.fastNlMeansDenoisingColored(noisy_frame, None, 10, 10, 7, 21)
        update_gui(frame, noisy_frame, restored_frame, temperature, humidity, light_level)

capture_button = ttk.Button(root, text="Capture and Process", command=capture_and_process_frame)
capture_button.pack(pady=20)

root.mainloop()

cap.release()
ser.close()
