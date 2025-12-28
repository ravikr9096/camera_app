import requests
from requests.auth import HTTPDigestAuth
import sys
import termios
import tty

# --- Configuration ---
CAMERA_IP = "192.168.0.111"  # Change to your camera IP
USERNAME = "admin"
PASSWORD = "Admin@1508"
CHANNEL = 1                 # Usually 1 for single-lens cameras

def goto_preset(preset_id):
    """
    Sends a command to the Hikvision ISAPI to go to a specific preset.
    """
    url = f"http://{CAMERA_IP}/ISAPI/PTZCtrl/channels/{CHANNEL}/presets/{preset_id}/goto"

    try:
        # Hikvision uses Digest Authentication for security
        response = requests.put(url, auth=HTTPDigestAuth(USERNAME, PASSWORD), timeout=5)
        
        if response.status_code == 200:
            print(f"Successfully moved to Preset {preset_id}")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection failed: {e}")

def get_char():
    """Read a single character from stdin without requiring Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

def main():
    print(f"Connecting to Hikvision camera at {CAMERA_IP}...")
    print("Controls: Press '1'-'6' for Presets 1-6, 'q' to Quit")

    while True:
        key = get_char().lower()
        
        if key == '1':
            goto_preset(1)
        elif key == '2':
            goto_preset(2)
        elif key == '3':
            goto_preset(3)
        elif key == '4':
            goto_preset(4)
        elif key == '5':
            goto_preset(5)
        elif key == '6':
            goto_preset(6)
        elif key == 'q':
            print("\nExiting...")
            break
        else:
            print(f"\nInvalid key '{key}'. Use 1-6 or q.")

if __name__ == "__main__":
    main()