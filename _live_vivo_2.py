import subprocess
import time
import cv2
import numpy as np

# Set the thres
# 0
# hold for template matching
threshold = 0.7  # Adjust based on required similarity

# Paths to the target images you want to detect
template_paths = [ '011.png', '000.png',  '007.jpg']
keep_paths = ['003_3.png']#, '003.png','003_2.png'
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
        if any(zip(*loc[::-1])):  # If any match is found
            print("Image detected.")
            return True
    return False

def swipe_up(device_id):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '500', '1500', '500', '300', '300'])
    print(f"Swipe up executed on device {device_id}")

def click_on_detected_image_center(device_id, screenshot, templates, template_sizes):
    """
    Detects a template on the screen and clicks on its center.
    
    Args:
        device_id (str): The device ID for ADB commands.
        screenshot (ndarray): The screenshot image in grayscale.
        templates (list): List of template images.
        template_sizes (list): List of template dimensions (width, height).
        
    Returns:
        bool: True if an image was detected and clicked, False otherwise.
    """
    for template, (w, h) in zip(templates, template_sizes):
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        
        for pt in zip(*loc[::-1]):  # Iterate over all detected points
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            simulate_click(device_id, center_x, center_y)
            print(f"Clicked on image center at ({center_x}, {center_y})")
            return True
    return False

def swipe_if_image_detected():
    device_id = "5001fc98"#select_device()  # Let the user select the device from the list
    if not device_id:
        print("No device selected. Exiting.")
        return

    try:
        while True:
            screenshot_path = capture_screenshot(device_id)
            screenshot = cv2.imread(screenshot_path, 0)
            
            # Detect keep image
            for x in range(3):
                if click_on_detected_image_center(device_id, screenshot, keep_templates, keep_sizes):
                #if detect_image_on_screen(device_id, keep_templates, keep_sizes):
                    print("Keep image detected, clicking at position.")
                    simulate_click("5001fc98", 975, 414)
                    time.sleep(1)
                    break
                time.sleep(0.1)
                
            for x in range(3):
                # Perform a swipe if no image is detected
                if detect_image_on_screen(device_id, close_templates, close_sizes):
                    print("Close image detected, performing swipe up.")
                    simulate_click("5001fc98", 543, 1498)
                    time.sleep(1)
                    break
                time.sleep(0.1)
            
            for x in range(3):
               # Detect main image
                if not detect_image_on_screen(device_id, templates, template_sizes):
                    #print(f"Image detected on device {device_id}. Waiting 10 seconds.")
                    swipe_up(device_id)
                    #time.sleep(11) 
                    break 
                """else:
                    print("Keep image detected, performing swipe up.")
                    swipe_up(device_id)
                    time.sleep(2)
                    break """
                     
            time.sleep(10)
    except KeyboardInterrupt:
        print("Process stopped by user.")



if __name__ == "__main__":
    swipe_if_image_detected()
