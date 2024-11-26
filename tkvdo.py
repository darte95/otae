import subprocess
import time
import cv2
import numpy as np

# Set the threshold for template matching
threshold = 0.6 # Adjust based on required similarity

# Paths to the target images you want to detect
template_paths = [ 'p1.png']
                                                                                    

# Load templates in grayscale
templates = [cv2.imread(path, 0) for path in template_paths]
template_sizes = [(template.shape[::-1]) for template in templates]



def get_connected_devices():
    # Get the list of connected devices
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    # Extract device IDs (ignore the first line and "unauthorized" devices)
    devices = [line.split()[0] for line in output.splitlines()[1:] if 'device' in line]
    return devices

def select_device():
    devices = get_connected_devices()
    if not devices:
        print("No devices connected.")
        return None
    
    print("Select a device:")
    for i, device in enumerate(devices):
        print(f"{i}: {device}")
    
    # Get user selection
    while True:
        try:
            selection = int(input("Enter the number of the device to select: "))
            if 0 <= selection < len(devices):
                return devices[selection]
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Please enter a number.")



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

def swipe_if_image_detected():
    device_id = "5001fc98"#elect_device()  # Let the user select the device from the list
    if not device_id:
        print("No device selected. Exiting.")
        return

    try:
        while True:
            # Detect keep image
         

            for x in range(5):    
                # Detect main image
                if detect_image_on_screen(device_id, templates, template_sizes):
                    print(f"Image detected on device {device_id}. Waiting 20 seconds.")
                    time.sleep(20)
                    swipe_up(device_id)
                else:
                    print("Keep image detected, performing swipe up.")
                    swipe_up(device_id)
                    time.sleep(0.5)
                time.sleep(0.2)


            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Process stopped by user.")

# Start the detection and swipe process
swipe_if_image_detected()