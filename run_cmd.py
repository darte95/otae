import tkinter as tk
import subprocess

def run_auto_py_to_exe():
    """Function to run 'auto-py-to-exe' in command prompt."""
    try:
        subprocess.run("auto-py-to-exe", shell=True)
    except Exception as e:
        print(f"Error: {e}")

# Create the main window
root = tk.Tk()
root.title("Run auto-py-to-exe")
root.geometry("300x150")  # Window size
root.resizable(False, False)  # Disable resizing

# Add a button to run the command
run_button = tk.Button(root, text="Run auto-py-to-exe", command=run_auto_py_to_exe, bg="blue", fg="white", font=("Arial", 12))
run_button.pack(pady=50)

# Start the GUI loop
root.mainloop()
