import subprocess
import time
import cv2
import numpy as np
from datetime import datetime
import pytz

# Define the timezone
timezone = pytz.timezone('Asia/Bangkok')

# Set the thres
# 0
# hold for template matching
threshold = 0.7  # Adjust based on required similarity

# Paths to the target images you want to detect
template_paths = [ '011.png', '000.png',  '007.jpg']
keep_paths = ['003.png','003_2.png']
close_paths = ['005.jpg']
following_paths = ['following.png']
sorry_paths = ['sorry.png']

# Load templates in grayscale
templates = [cv2.imread(path, 0) for path in template_paths]
template_sizes = [(template.shape[::-1]) for template in templates]

keep_templates = [cv2.imread(path, 0) for path in keep_paths]
keep_sizes = [(template.shape[::-1]) for template in keep_templates]

close_templates = [cv2.imread(path, 0) for path in close_paths]
close_sizes = [(template.shape[::-1]) for template in close_templates]

following_templates = [cv2.imread(path, 0) for path in following_paths]
following_sizes = [(template.shape[::-1]) for template in following_templates]

sorry_templates = [cv2.imread(path, 0) for path in sorry_paths]
sorry_sizes = [(template.shape[::-1]) for template in sorry_templates]


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

def get_device_screen_size(device_id):
    # Get the screen resolution of the connected device
    result = subprocess.run(['adb', '-s', device_id, 'shell', 'wm', 'size'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    if "Physical size" in output:
        # Extract the screen size from the output
        screen_size = output.split(":")[1].strip()
        return screen_size
    return None  

def simulate_click(device_id, x, y):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'tap', str(x), str(y)])
    print(f"Clicked on device {device_id} at position: ({x}, {y})")

def capture_screenshot(device_id):
    filename = f'screenshot_oppo{device_id}.png'
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
    device_id = "734d6104"#select_device()  # Let the user select the device from the list
    if not device_id:
        print("No device selected. Exiting.")
        return

    try:
        while True:
            # Detect keep image
            for x in range(2):
                
                if detect_image_on_screen(device_id, keep_templates, keep_sizes):
                    
                    if detect_image_on_screen(device_id, following_templates, following_sizes):
                        print("Keep image detected, clicking at position.")
                        simulate_click("734d6104", 978, 565)
                        time.sleep(2)
                    else:
                        print("Keep image detected, clicking at position.")
                        simulate_click("734d6104", 978, 450)
                        time.sleep(2)
                    
                    break
                time.sleep(1)
                
            for x in range(2):
                # Perform a swipe if no image is detected
                if detect_image_on_screen(device_id, close_templates, close_sizes):
                    print("Close image detected, performing swipe up.")
                    simulate_click("734d6104", 540, 1474)#495, 1450)
                    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
                    print(current_time)
                    time.sleep(2)
                    break
                time.sleep(1)
            
            for x in range(3):
               # Detect main image
                if detect_image_on_screen(device_id, templates, template_sizes):
                    print(f"Image detected on device {device_id}. Waiting 10 seconds.")
                    time.sleep(11) 
                    break 
                else:
                    print("Keep image detected, performing swipe up.")
                    swipe_up(device_id)
                    time.sleep(2)
                    break 
                time.sleep(0.2)  
            if detect_image_on_screen(device_id, sorry_templates, sorry_sizes):
                    print("Close image detected, performing swipe up.")
                    simulate_click("734d6104", 544, 1498)
                    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
                    print(current_time)

            
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("Process stopped by user.")

if __name__ == "__main__":
    swipe_if_image_detected()