
from services.hostpot import setup_hotspot

# Entry Point
if __name__ == "__main__":
    # Customize the SSID and password for the hotspot and Wi-Fi connection
    hotspot_ssid = "MyPiHotspot"
    hotspot_passphrase = "123321123"
    wifi_ssid = "Working_Room"
    wifi_password = "123321123"

    setup_hotspot(hotspot_ssid, hotspot_passphrase, wifi_ssid, wifi_password)