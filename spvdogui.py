import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time

# Function to get a list of connected devices
def list_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    devices = [line.split('\t')[0] for line in lines[1:] if '\tdevice' in line]
    return devices

# Function to perform a swipe up on the specified device
def swipe_up(device_id):
    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '500', '1500', '500', '800', '200'])

# Thread to continuously swipe up at intervals
def start_swiping():
    global stop_swipe
    device_id = selected_device.get()
    
    if not device_id:
        messagebox.showwarning("No Device Selected", "Please select a device.")
        return
    
    stop_swipe = False
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    def swipe_loop():
        while not stop_swipe:
            swipe_up(device_id)
            time.sleep(400)  # Delay between swipes

    threading.Thread(target=swipe_loop, daemon=True).start()

# Function to stop the swipe loop
def stop_swiping():
    global stop_swipe
    stop_swipe = True
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Function to refresh device list in the dropdown
def refresh_device_list():
    devices = list_devices()
    device_menu['menu'].delete(0, 'end')
    for device in devices:
        device_menu['menu'].add_command(label=device, command=tk._setit(selected_device, device))
    if devices:
        selected_device.set(devices[0])  # Set first device as default
    else:
        selected_device.set('')  # Clear selection if no devices connected

# Initialize the GUI
root = tk.Tk()
root.title("ADB Swipe Tool")
root.geometry("200x200")
root.resizable(False, False)  # Disable resizing
selected_device = tk.StringVar()
stop_swipe = False

# Device selection dropdown
device_label = tk.Label(root, text="Select Device:")
device_label.pack(pady=5)

device_menu = tk.OptionMenu(root, selected_device, [])
device_menu.pack()

# Refresh button to update device list
refresh_button = tk.Button(root, text="Refresh Devices", command=refresh_device_list)
refresh_button.pack(pady=5)

# Start and Stop buttons for swipe action
start_button = tk.Button(root, text="Start Swiping", command=start_swiping)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Swiping", command=stop_swiping, state=tk.DISABLED)
stop_button.pack(pady=5)

# Refresh device list on startup
refresh_device_list()

# Run the GUI loop
root.mainloop()
