import subprocess
import time
import cv2
import numpy as np

# Set the threshold for template matching
threshold = 0.8  # Adjusted threshold for higher similarity detection

# Paths to the target images
template_paths = ['vo_follow.png', 'vo_follow2.png','vo_close1.png', 'closegift.png','vo_back.png' ]


# Load templates in grayscale
templates = [cv2.imread(path, 0) for path in template_paths]
template_sizes = [(template.shape[::-1]) for template in templates]


def get_connected_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
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
    
    while True:
        try:
            selection = int(input("Enter the number of the device to select: "))
            if 0 <= selection < len(devices):
                return devices[selection]
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Please enter a number.")

def get_device_screen_size(device_id):
    result = subprocess.run(['adb', '-s', device_id, 'shell', 'wm', 'size'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    if "Physical size" in output:
        screen_size = output.split(":")[1].strip()
        return screen_size
    return None  

def simulate_click(device_id, x, y):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)])
    print(f"Clicked on device {device_id} at position: ({x}, {y})")

def capture_screenshot(device_id):
    filename = f'screenshot_{device_id}.png'
    subprocess.run(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], stdout=open(filename, 'wb'))
    return filename

def detect_image_on_screen(device_id, templates, template_sizes):
    screenshot_path = capture_screenshot(device_id)
    screenshot = cv2.imread(screenshot_path, 0)

    for template, (w, h) in zip(templates, template_sizes):
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        for pt in zip(*loc[::-1]):  # If matches found
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            print(f"Image detected at location: {pt}, center at: ({center_x}, {center_y})")
            simulate_click(device_id, center_x, center_y)
            return True
    return False

def swipe_up(device_id):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '500', '1500', '500', '300', '300'])
    print(f"Swipe up executed on device {device_id}")

def swipe_if_image_detected():
    device_id = select_device()
    if not device_id:
        print("No device selected. Exiting.")
        return

    try:
        while True:
         
                if detect_image_on_screen(device_id, templates, template_sizes):
                    print(f"Image detected on device {device_id}. Performing action.")
                    time.sleep(0.2)  # Optional delay for stability
                else:
                    print("Keep image not detected, performing swipe up.")
                    #swipe_up(device_id)
                    time.sleep(0.2)
                time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("Process stopped by user.")

# Start the detection and swipe process
swipe_if_image_detected()
