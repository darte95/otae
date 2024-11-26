import cv2
import numpy as np
import subprocess
import time

# Set the threshold for template matching
threshold = 0.7  # Adjust based on how similar the image must be to match

# Path to the target image you want to detect
template_path = '003.jpg'
template = cv2.imread(template_path, 0)  # Read in grayscale
w, h = template.shape[::-1]

# Function to capture screenshot from a specific device using its ID
def capture_screenshot(device_id):
    # Capture a screenshot from the specified device
    subprocess.run(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], stdout=open('screenshot.png', 'wb'))

# Function to detect the image on the screen
def detect_image_on_screen(device_id):
    # Capture screenshot
    capture_screenshot(device_id)
    
    # Read the screenshot
    screenshot = cv2.imread('screenshot.png', 0)  # Read in grayscale

    # Perform template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)  # Get locations that match the threshold

    # Check if there's a match
    for pt in zip(*loc[::-1]):  # Switch x and y locations
        print(f"Image detected at location: {pt}")
        # Draw a rectangle around the matched area (optional)
        cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
        cv2.imshow('Detected', screenshot)  # Show the result for visual feedback
        cv2.waitKey(1000)  # Display each match for a second
        return True  # Return True on detection

    return False  # No match found

# Function to get connected devices
def get_connected_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    devices = [line.split()[0] for line in output.splitlines()[1:] if 'device' in line]
    return devices

# Main logic to handle a single device input
def detect_on_single_device():
    devices = get_connected_devices()
    if not devices:
        print("No devices connected.")
        return
    
    print(f"Connected devices: {devices}")
    
    # Prompt user to input a device ID
    device_id = input("Enter the device ID you want to use from the list above: ")
    if device_id not in devices:
        print(f"Device ID {device_id} is not connected.")
        return

    try:
        while True:
            print(f"Checking device {device_id}...")
            found = detect_image_on_screen(device_id)
            if found:
                print(f"Target image found on device {device_id}!")
                break  # Exit the loop if the image is found
            time.sleep(0.5)  # Adjust delay to control detection speed

    except KeyboardInterrupt:
        print("Process stopped by user.")
    finally:
        cv2.destroyAllWindows()

# Run the detection on the specified device
detect_on_single_device()
