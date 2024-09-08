import sys
import os

# =============================================
# For debugging ...
# =============================================
if '--debug' in sys.argv:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()
    debugpy.breakpoint()
    print("Debugger is attached!")
# =============================================

# =============================================
# For changing cwd ... 
# =============================================
try:
    os.chdir(os.path.dirname(__file__))
    print(f"Current working directory changed to {os.getcwd()}")
except OSError as e:
    print(f"Error: {e}")
# =============================================

from services.portal import setup_portal
from services.hostpot import setup_hotspot

# Entry Point
if __name__ == "__main__":
    # Customize the SSID and password for the hotspot and Wi-Fi connection
    hotspot_ssid = "MyPiHotspot"
    hotspot_passphrase = "123321123"
    wifi_ssid = "Working_Room"
    wifi_password = "123321123"

    setup_hotspot(hotspot_ssid, hotspot_passphrase, wifi_ssid, wifi_password)
    setup_portal()

    print("Setup completed successfully.")
    while True:
        pass