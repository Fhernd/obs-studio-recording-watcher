import time
import os
import obswebsocket
from obswebsocket import obsws, events
import tkinter as tk
from tkinter import simpledialog, messagebox

# OBS WebSocket connection settings
host = "192.168.1.40"
port = 4455
password = "9c1drmdDjx75lMYv"

# Function to show a prompt to rename the file
def show_prompt_and_rename(file_path):
    root = tk.Tk()
    root.withdraw()
    new_name = simpledialog.askstring("Rename Recording", "Enter new name for the recording file (without extension):")
    root.destroy()
    
    if new_name:
        base, ext = os.path.splitext(file_path)
        new_file_path = os.path.join(os.path.dirname(file_path), new_name + ext)
        os.rename(file_path, new_file_path)
        messagebox.showinfo("File Renamed", f"Recording file has been renamed to: {new_file_path}")
    else:
        messagebox.showinfo("No Change", "Recording file name was not changed.")

# Event handler for recording stop
def on_recording_stopped(event):
    print('Recording stopped event triggered')
    # Retrieve the most recent recording file path
    try:
        rec_file = ws.call(obswebsocket.requests.GetRecordingStatus()).getRecordingFilename()
        show_prompt_and_rename(rec_file)
    except Exception as e:
        print(f"Error retrieving recording file path: {e}")

# Connect to OBS WebSocket
ws = obsws(host, port, password)
ws.connect()

# Register event handler
ws.register(on_recording_stopped, events.RecordingStopped)
print("Event handler registered for RecordingStopped")

try:
    print("Monitoring recording status...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    ws.disconnect()
    print("Disconnected from OBS WebSocket")
