import subprocess
import time

def list_devices():
    # Get the list of connected devices
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()

    # Filter out the header line and offline devices
    devices = [line.split('\t')[0] for line in lines[1:] if '\tdevice' in line]
    return devices

def select_device():
    devices = list_devices()
    
    if not devices:
        print("No devices connected.")
        return None
    elif len(devices) == 1:
        print(f"Using the only connected device: {devices[0]}")
        return devices[0]
    else:
        print("Multiple devices connected:")
        for i, device in enumerate(devices):
            print(f"{i + 1}: {device}")
        
        choice = int(input("Select a device by number: ")) - 1
        if 0 <= choice < len(devices):
            return devices[choice]
        else:
            print("Invalid selection.")
            return None

def swipe_up(device_id):
    # Run the ADB command to perform a swipe up on the specified device
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '500', '1500', '500', '800', '200'])

# Select the device
device_id = select_device()
if device_id:
    try:
        while True:
            swipe_up(device_id)
            time.sleep(40)  # Adjust delay to control detection speed
    except KeyboardInterrupt:
        print("Process stopped by user.")
else:
    print("No device selected.")
