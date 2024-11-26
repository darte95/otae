import subprocess
import time
import cv2
import numpy as np

# Set the threshold for template matching
threshold = 0.8  # Adjust based on required similarity

# Paths to the target images you want to detect
follow_1_paths = [ 'vo_follow.png']
follow_2_paths = ['vo_follow2.png']
keep_paths = ['keepgift.png']
close_paths = ['vo_close1.png', 'op_close1.png']

# Load templates in grayscale
follow_1_templates = [cv2.imread(path, 0) for path in follow_1_paths]
follow_1_sizes = [(template.shape[::-1]) for template in follow_1_templates]

follow_2_templates = [cv2.imread(path, 0) for path in follow_2_paths]
follow_2_sizes = [(template.shape[::-1]) for template in follow_2_templates]

keep_templates = [cv2.imread(path, 0) for path in keep_paths]
keep_sizes = [(template.shape[::-1]) for template in keep_templates]

close_templates = [cv2.imread(path, 0) for path in close_paths]
close_sizes = [(template.shape[::-1]) for template in close_templates]

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
    filename = f'screenshot_follow_vivo{device_id}.png'
    subprocess.run(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], stdout=open(filename, 'wb'))
    return filename

def detect_image_on_screen(device_id, templates, template_sizes):
    screenshot_path = capture_screenshot(device_id)
    screenshot = cv2.imread(screenshot_path, 0)  # Load in grayscale

    for template, (w, h) in zip(templates, template_sizes):
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        for pt in zip(*loc[::-1]):  # Get the match points
            center_x = pt[0] + w // 2  # Calculate center X
            center_y = pt[1] + h // 2  # Calculate center Y
            print(f"Image detected at: ({center_x}, {center_y})")
            return center_x, center_y  # Return the center coordinates
    return None  # No match found

def swipe_up(device_id):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '500', '1500', '500', '1100', '300'])
    print(f"Swipe up executed on device {device_id}")

def swipe_if_image_detected():
    device_id = "5001fc98"  # Predefined device ID
    if not device_id:
        print("No device selected. Exiting.")
        return

    try:
        while True:
            # Detect and click on "keep" image
            coordinates = detect_image_on_screen(device_id, keep_templates, keep_sizes)
            if coordinates:
                x, y = coordinates
                simulate_click(device_id, x, y)
                time.sleep(0.2)
                simulate_click(device_id, 771, 1603)
                time.sleep(0.2)

        
            coordinates = detect_image_on_screen(device_id, follow_1_templates, follow_1_sizes)
            if coordinates:
                            x, y = coordinates
                            simulate_click(device_id, x, y)
                            
                            time.sleep(0.5)
                            simulate_click("5001fc98", 65, 153)
                            time.sleep(0.2)
          

            coordinates = detect_image_on_screen(device_id, follow_2_templates, follow_2_sizes)
            if coordinates:
                            x, y = coordinates
                            simulate_click(device_id, x, y)
                            
                            time.sleep(0.5)
                            simulate_click("5001fc98", 65, 153)
                            time.sleep(0.2)

                            
            coordinates = detect_image_on_screen(device_id, close_templates, close_sizes)
            if coordinates:
                                    x, y = coordinates
                                    simulate_click("5001fc98", 65, 153)
                                    time.sleep(0.2)
                     
                                


          
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Process stopped by user.")

# Start the detection and swipe process
swipe_if_image_detected()
