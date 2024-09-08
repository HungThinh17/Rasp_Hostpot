import subprocess
import os

def run_command(command):
    """Utility function to run shell commands."""
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Command executed: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command '{command}': {e}")
        raise  # Raise the exception to propagate it

def configure_dnsmasq():
    """Configure dnsmasq for DHCP and DNS redirection."""
    print("Configuring dnsmasq...")
    dnsmasq_conf = """
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
"""
    with open('/etc/dnsmasq.conf', 'w') as f:
        f.write(dnsmasq_conf)
    run_command("systemctl restart dnsmasq")

def setup_web_server():
    """Set up a simple web server with a default HTML page."""
    print("Setting up the web server...")
    # Create the HTML file
    html_file_path = '/var/www/html/index.html'
    os.makedirs('/var/www/html', exist_ok=True)
    # Write HTML content to a separate file
    with open(html_file_path, 'w') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Raspberry Pi Hotspot</title>
</head>
<body>
    <h1>Welcome to the Raspberry Pi Hotspot!</h1>
    <p>This is a support portal for connected devices.</p>
</body>
</html>
""")
    run_command("systemctl start lighttpd")
    run_command("systemctl enable lighttpd")

def configure_iptables():
    """Configure iptables for HTTP redirection."""
    print("Configuring iptables for HTTP redirection...")
    run_command("iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 80 -j DNAT --to-destination 192.168.4.1:80")
    run_command("iptables -A FORWARD -p tcp -d 192.168.4.1 --dport 80 -j ACCEPT")
    run_command("apt install iptables-persistent -y")
    run_command("iptables-save > /etc/iptables/rules.v4")

def rollback_setup():
    """Rollback the setup by restoring original configurations."""
    print("Rolling back the setup...")
    
    # Remove dnsmasq configuration
    if os.path.exists('/etc/dnsmasq.conf'):
        os.remove('/etc/dnsmasq.conf')
    
    # Stop and disable services
    run_command("systemctl stop dnsmasq")
    run_command("systemctl stop lighttpd")
    
    # Remove web server files
    if os.path.exists('/var/www/html/index.html'):
        os.remove('/var/www/html/index.html')
    
    # Clear iptables rules
    run_command("iptables -t nat -F")
    run_command("iptables -F")
    run_command("iptables-save > /etc/iptables/rules.v4")

    print("Rollback completed.")

def clean_setup():
    """Clean the setup by removing configurations."""
    print("Cleaning up previous configurations...")
    rollback_setup()
    print("Clean setup completed.")

def setup_portal():
    """Main function to set up the captive portal."""
    try:
        configure_dnsmasq()
        setup_web_server()
        configure_iptables()
        print("Captive portal setup complete. Connect a device to the hotspot to test.")
    except Exception as e:
        print(f"An error occurred during the setup: {e}")
        rollback_setup()  # Rollback if an error occurs
