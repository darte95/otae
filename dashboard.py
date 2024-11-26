import tkinter as tk
import subprocess

# Function to run SPVDO-Swipe.exe
def run_spvdo_swipe():
    try:
        subprocess.run(r"C:\adb\_follow_vivo.exe", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running SPVDO-Swipe: {e}")
    except FileNotFoundError:
        print("SPVDO-Swipe.exe not found. Make sure the path is correct.")

# Function to run _live_oppo.exe
def run_live_oppo():
    try:
        subprocess.run(r"C:\adb\_follow_oppo.exe", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running _live_oppo: {e}")
    except FileNotFoundError:
        print("_live_oppo.exe not found. Make sure the path is correct.")

# Create the main Tkinter window
root = tk.Tk()
root.title("Run Files")
root.geometry("300x200")  # Adjusted size to fit two buttons
root.resizable(False, False)  # Disable resizing

# Create and place buttons
run_spvdo_button = tk.Button(root, text="Run SPVDO-Swipe", command=run_spvdo_swipe, font=("Arial", 12), bg="lightblue")
run_spvdo_button.pack(pady=10)  # Add padding for layout

run_live_oppo_button = tk.Button(root, text="Run _live_oppo", command=run_live_oppo, font=("Arial", 12), bg="lightgreen")
run_live_oppo_button.pack(pady=10)  # Add padding for layout

# Run the Tkinter event loop
root.mainloop()
