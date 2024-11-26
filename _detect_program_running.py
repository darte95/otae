import psutil
import time
import pyautogui
from datetime import datetime

def detect_process(target_processes):
    """
    Detect if any of the specified processes are running.

    Args:
        target_processes (list): List of process names to check.

    Returns:
        dict: A dictionary with process names and their running status.
    """
    running_processes = {proc.name(): proc for proc in psutil.process_iter(['name'])}
    detected = {process: process in running_processes for process in target_processes}
    return detected

# List of programmer-related processes to check with their screen positions
programming_tools = {
    "_live_oppo.exe": (1860, 36),  # Replace with the screen position for the double-click
    "_live_vivo.exe": (1860, 238)   # Replace with the screen position for the double-click
}

if __name__ == "__main__":
    while True:  # Infinite loop to repeatedly check for processes
        print(f"\n[INFO] Checking processes at {datetime.now()}")
        process_status = detect_process(programming_tools.keys())
        
        for process, is_running in process_status.items():
            if is_running:
                print(f"{process}: Running")
            else:
                print(f"{process}: Not Running. Starting the program...")
                try:
                    # Get the screen position for the process
                    x, y = programming_tools[process]
                    # Move the mouse to the position and double-click
                    pyautogui.moveTo(x, y)
                    pyautogui.doubleClick()
                    print(f"[INFO] Successfully started {process} with double-click.")
                except Exception as e:
                    print(f"[ERROR] Failed to start {process}. Reason: {e}")
        
        print("Waiting for 10 seconds before the next check...")
        time.sleep(10)  # Pause for 10 seconds
