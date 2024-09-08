import subprocess
import os

def run_command(command):
    """Utility function to run shell commands."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command '{command}': {e}")

def check_setup_completed():
    """Check if the setup has already been completed."""
    return os.path.exists('/etc/hostapd/hostapd.conf')

def rollback_setup():
    """Rollback the setup by restoring original configurations."""
    print("Rolling back the setup...")
    if os.path.exists('/etc/dnsmasq.conf.orig'):
        run_command("sudo mv /etc/dnsmasq.conf.orig /etc/dnsmasq.conf")
    if os.path.exists('/etc/hostapd/hostapd.conf'):
        os.remove('/etc/hostapd/hostapd.conf')
    if os.path.exists('/etc/default/hostapd'):
        with open('/etc/default/hostapd', 'r') as f:
            lines = f.readlines()
        with open('/etc/default/hostapd', 'w') as f:
            for line in lines:
                if 'DAEMON_CONF' not in line:
                    f.write(line)
    run_command("sudo systemctl restart dnsmasq")
    run_command("sudo systemctl restart hostapd")
    print("Rollback completed.")

def clean_setup():
    """Clean the setup by removing configurations."""
    print("Cleaning up previous configurations...")
    if os.path.exists('/etc/dnsmasq.conf'):
        os.remove('/etc/dnsmasq.conf')
    if os.path.exists('/etc/hostapd/hostapd.conf'):
        os.remove('/etc/hostapd/hostapd.conf')
    if os.path.exists('/etc/wpa_supplicant/wpa_supplicant.conf'):
        os.remove('/etc/wpa_supplicant/wpa_supplicant.conf')
    run_command("sudo systemctl stop dnsmasq")
    run_command("sudo systemctl stop hostapd")
    print("Clean setup completed.")

def configure_static_ip():
    """Step 2: Configure static IP for wlan0."""
    print("Configuring static IP...")
    with open('/etc/dhcpcd.conf', 'a') as f:
        f.write("\ninterface wlan0\n"
                "static ip_address=192.168.4.1/24\n"
                "nohook wpa_supplicant\n")
    run_command("sudo systemctl restart dhcpcd")
    print("Static IP configured.")

def configure_dnsmasq():
    """Step 3: Configure dnsmasq for DHCP."""
    print("Configuring dnsmasq...")
    if os.path.exists("/etc/dnsmasq.conf"):
        run_command("sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig")
    with open('/etc/dnsmasq.conf', 'w') as f:
        f.write("interface=wlan0\n"
                "dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\n")
    run_command("sudo systemctl restart dnsmasq")
    print("dnsmasq configured.")

def configure_hostapd(ssid, passphrase):
    """Step 4: Configure hostapd."""
    print("Configuring hostapd...")
    with open('/etc/hostapd/hostapd.conf', 'w') as f:
        f.write(f"interface=wlan0\n"
                "driver=nl80211\n"
                f"ssid={ssid}\n"
                "hw_mode=g\n"
                "channel=7\n"
                "wmm_enabled=0\n"
                "macaddr_acl=0\n"
                "auth_algs=1\n"
                "ignore_broadcast_ssid=0\n"
                "wpa=2\n"
                f"wpa_passphrase={passphrase}\n"
                "wpa_key_mgmt=WPA-PSK\n"
                "rsn_pairwise=CCMP\n")
    with open('/etc/default/hostapd', 'a') as f:
        f.write("\nDAEMON_CONF=\"/etc/hostapd/hostapd.conf\"\n")
    run_command("sudo systemctl restart hostapd")
    print("hostapd configured.")

def configure_wpa_supplicant(wifi_ssid, wifi_password):
    """Step 5: Configure connection to available Wi-Fi."""
    print(f"Configuring Wi-Fi connection to {wifi_ssid}...")
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
        f.write(f"\nnetwork={{\n"
                f"    ssid=\"{wifi_ssid}\"\n"
                f"    psk=\"{wifi_password}\"\n"
                "}\n")
    run_command("sudo systemctl restart wpa_supplicant")
    print("Wi-Fi connection configured.")

def enable_ip_forwarding():
    """Step 6: Enable IP forwarding and NAT."""
    print("Enabling IP forwarding...")
    run_command("sudo sysctl -w net.ipv4.ip_forward=1")
    # Persist the IP forwarding setting
    with open('/etc/sysctl.conf', 'r') as file:
        data = file.readlines()
    for i, line in enumerate(data):
        if line.strip() == '#net.ipv4.ip_forward=1':
            data[i] = 'net.ipv4.ip_forward=1\n'
            break
    with open('/etc/sysctl.conf', 'w') as file:
        file.writelines(data)
    # Set up NAT (Network Address Translation)
    run_command("sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE")
    run_command("sudo iptables-save > /etc/iptables/rules.v4")
    print("IP forwarding enabled.")

def setup_hotspot(ssid, passphrase, wifi_ssid, wifi_password):
    """Main function to run all setup steps."""
    if check_setup_completed():
        print("Setup has already been completed. Rolling back to clean state.")
        rollback_setup()
        clean_setup()

    try:
        configure_static_ip()
        configure_dnsmasq()
        configure_hostapd(ssid, passphrase)
        configure_wpa_supplicant(wifi_ssid, wifi_password)
        enable_ip_forwarding()
        print("Raspberry Pi hotspot setup complete. You can now connect devices.")
    except Exception as e:
        print(f"An error occurred during the hotspot setup: {e}")
        rollback_setup()