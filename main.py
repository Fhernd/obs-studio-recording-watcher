import time
import os
import obswebsocket
from obswebsocket import obsws, events, requests
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


def on_record_state_changed(event):
    """
    Event handler for RecordStateChanged event.

    This function is called whenever the recording state changes in OBS.

    Args:
        event (dict): Event data dictionary.
    """
    if event.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STOPPED':
        rec_file = event.datain['outputPath']
        show_prompt_and_rename(rec_file)


def main():
    """
    Main function to connect to OBS WebSocket and monitor recording status.

    This function connects to OBS WebSocket, registers an event handler for RecordStateChanged event, and then monitors the recording status.
    """
    ws = obsws(host, port, password)
    ws.connect()

    ws.register(on_record_state_changed, events.RecordStateChanged)
    print("Event handler registered for RecordStateChanged")

    try:
        print("Monitoring recording status...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        ws.disconnect()
        print("Disconnected from OBS WebSocket")


if __name__ == "__main__":
    main()
