
import cv2
import os
import numpy as np
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def simulate_sensor_values():
    temperature = random.uniform(15.0, 30.0)  # Simulate temperature between 15 and 30°C
    humidity = random.uniform(40.0, 90.0)     # Simulate humidity between 40% and 90%
    light_level = random.randint(0, 1000)     # Simulate light levels between 0 and 1000 lux
    return temperature, humidity, light_level