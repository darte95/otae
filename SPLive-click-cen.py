import subprocess
import time
import cv2
import numpy as np

# Set the threshold for template matching
threshold = 0.6  # Adjust based on required similarity

# Paths to the target images you want to detect
template_paths = ['000.jpg', '006.jpg']
keep_paths = ['003.jpg']
close_paths = ['005.jpg']

# Load templates in grayscale
templates = [cv2.imread(path, 0) for path in template_paths]
template_sizes = [(template.shape[::-1]) for template in templates]

keep_templates = [cv2.imread(path, 0) for path in keep_paths]
keep_sizes = [(template.shape[::-1]) for template in keep_templates]

close_templates = [cv2.imread(path, 0) for path in close_paths]
close_sizes = [(template.shape[::-1]) for template in close_templates]

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
    filename = f'screenshot_{device_id}.png'
    subprocess.run(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], stdout=open(filename, 'wb'))
    return filename

def detect_image_on_screen(device_id, templates, template_sizes):
    screenshot_path = capture_screenshot(device_id)
    screenshot = cv2.imread(screenshot_path, 0)  # Load in grayscale

    for template, (w, h) in zip(templates, template_sizes):
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        for pt in zip(*loc[::-1]):  # If a match is found
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
    device_id = select_device()  # Let the user select the device from the list
    if not device_id:
        print("No device selected. Exiting.")
        return

    try:
        while True:
            # Detect keep image
            for x in range(5):
                if detect_image_on_screen(device_id, keep_templates, keep_sizes):
                    print("Keep image detected, clicking at position.")
                    time.sleep(2)
                time.sleep(1)
                
            for x in range(5):
                # Perform a swipe if no image is detected
                if detect_image_on_screen(device_id, close_templates, close_sizes):
                    print("Close image detected, performing swipe up.")
                    simulate_click(device_id, 495, 1450)
                time.sleep(1)
            
            for x in range(5):
               # Detect main image
                if detect_image_on_screen(device_id, templates, template_sizes):
                    print(f"Image detected on device {device_id}. Waiting 305 seconds.")
                    time.sleep(32)  
                else:
                    print("Keep image detected, performing swipe up.")
                    swipe_up(device_id)
                    time.sleep(1)
                time.sleep(1)   
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Process stopped by user.")

# Start the detection and swipe process
swipe_if_image_detected()
