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
    
    psnr_value = calculate_psnr(frame, noisy_frame)
    psnr_label.config(text=f"PSNR (Original vs Noisy): {psnr_value:.2f} dB")