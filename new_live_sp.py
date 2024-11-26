import subprocess
import time
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, Listbox, END

# Set the threshold for template matching
threshold = 0.7  # Adjust based on required similarity

# Paths to the target images you want to detect
template_paths = ['000.png', '007.jpg']
keep_paths = ['003.png']
close_paths = ['005.jpg']

# Load templates in grayscale
templates = [cv2.imread(path, 0) for path in template_paths]
template_sizes = [(template.shape[::-1]) for template in templates]

keep_templates = [cv2.imread(path, 0) for path in keep_paths]
keep_sizes = [(template.shape[::-1]) for template in keep_templates]

close_templates = [cv2.imread(path, 0) for path in close_paths]
close_sizes = [(template.shape[::-1]) for template in close_templates]

process_running = False  # To control the start/stop process


def get_connected_devices():
    # Get the list of connected devices
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    # Extract device IDs (ignore the first line and "unauthorized" devices)
    devices = [line.split()[0] for line in output.splitlines()[1:] if 'device' in line]
    return devices


def simulate_click(device_id, x, y):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)])
    print(f"Clicked on device {device_id} at position: ({x}, {y})")


def capture_screenshot(device_id):
    filename = f'screenshot_{device_id}.png'
    subprocess.run(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], stdout=open(filename, 'wb'))
    return filename


def detect_image_on_screen(device_id, templates, template_sizes):
    screenshot_path = capture_screenshot(device_id)
    screenshot = cv2.imread(screenshot_path, 0)  # Load in grayscale

    for template, (w, h) in zip(templates, template_sizes):
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        if any(zip(*loc[::-1])):  # If any match is found
            print("Image detected.")
            return True
    return False


def swipe_up(device_id):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '500', '1500', '500', '300', '300'])
    print(f"Swipe up executed on device {device_id}")


def start_process(device_id, status_label):
    global process_running
    process_running = True

    def process():
        try:
            while process_running:
                # Detect keep image
                if detect_image_on_screen(device_id, keep_templates, keep_sizes):
                    print("Keep image detected, clicking at position.")
                    simulate_click(device_id, 980, 410)
                    time.sleep(2)

                # Detect close image
                elif detect_image_on_screen(device_id, close_templates, close_sizes):
                    print("Close image detected, performing swipe up.")
                    simulate_click(device_id, 543, 1498)
                    time.sleep(2)

                # Detect main image
                elif detect_image_on_screen(device_id, templates, template_sizes):
                    print(f"Image detected on device {device_id}. Waiting 10 seconds.")
                    time.sleep(10)
                else:
                    print("No image detected, performing swipe up.")
                    swipe_up(device_id)
                    time.sleep(2)

                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Process stopped by user.")

    status_label.config(text=f"Running on device {device_id}...")
    process()


def stop_process(status_label):
    global process_running
    process_running = False
    status_label.config(text="Process stopped.")


def create_gui():
    devices = get_connected_devices()
    if not devices:
        messagebox.showerror("Error", "No devices connected.")
        return

    def on_start():
        selection = device_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a device.")
            return
        selected_device = devices[selection[0]]
        start_process(selected_device, status_label)



    # Create the main window
    root = tk.Tk()
    root.title("ADB Device Manager")
    root.resizable(False, False)

    tk.Label(root, text="Select a device:").pack(pady=5)

    device_listbox = Listbox(root, height=5)
    for device in devices:
        device_listbox.insert(END, device)
    device_listbox.pack(pady=5)

    start_button = tk.Button(root, text="Start Process", command=on_start)
    start_button.pack(pady=5)



    status_label = tk.Label(root, text="Status: Waiting...", fg="blue")
    status_label.pack(pady=10)

    root.mainloop()


# Run the GUI
create_gui()
