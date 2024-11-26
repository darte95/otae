import subprocess
import cv2
import numpy as np
from datetime import datetime
import time

def capture_screenshot():
    """Capture a screenshot from the connected Android device."""
    try:
        result = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            capture_output=True,
            text=False
        )
        if result.returncode != 0:
            raise Exception("Failed to capture screenshot.")
        # Save the screenshot to a file
        screenshot_path = "screenshot.png"  # Use a static name to overwrite each time
        with open(screenshot_path, "wb") as f:
            f.write(result.stdout)
        return screenshot_path
    except Exception as e:
        print(f"Error: {e}")
        return None

def detect_image_in_image(screenshot_path, template_path, threshold=0.6):
    """Detect template image in the screenshot and return the center of the detected area."""
    try:
        # Load the screenshot and template
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)

        if screenshot is None or template is None:
            raise ValueError(f"Failed to load images. Check paths: {template_path}")

        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # Calculate the bounding box of the detected region
            template_h, template_w = template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)

            # Calculate the center of the detected region
            center_x = top_left[0] + template_w // 2
            center_y = top_left[1] + template_h // 2

            print(f"Template {template_path} found at center: ({center_x}, {center_y})")
            return center_x, center_y
        else:
            print(f"Template {template_path} not found in the screenshot.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def tap_on_coordinates(x, y):
    """Simulate a tap on the Android device at the given coordinates."""
    try:
        command = f"adb shell input tap {x} {y}"
        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Tapped at coordinates ({x}, {y})")
        else:
            print("Failed to perform tap action.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    template_paths = ["bag.png"]  # List of template image paths

    try:
        while True:  # Infinite loop
            # Capture a new screenshot
            screenshot_path = capture_screenshot()
            
            if screenshot_path:
                # Iterate through all template images
                for template_path in template_paths:
                    # Detect the image in the screenshot
                    center_coordinates = detect_image_in_image(screenshot_path, template_path)

                    if center_coordinates:
                        # Tap on the center of the detected image
                        tap_on_coordinates(*center_coordinates)

            # Wait before the next iteration to avoid overloading the device
            time.sleep(1)  # Adjust the delay as needed (1 second in this case)
    except KeyboardInterrupt:
        print("Process stopped by user.")
