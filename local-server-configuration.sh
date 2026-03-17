#!/bin/bash
#local-server-configuration.sh
# This script is responsible for preparing the local server (RPi) after fresh install

mac_address=""

echo "This script is responsible for preparing the local server (RPi) after fresh install"

echo "Updating apt"

sudo apt update
sudo apt upgrade -y

echo "Installing required dependencies"

sudo apt install wakeonlan -y
sudo apt install git -y

# Ask user for MAC address
while true; do
    echo "Now provide the MAC address of the machine that is meant to be switched on using Wake-on-LAN"
    echo "E.g. 01:23:45:67:89:ab"
    read mac_address

    # Check if input is empty
    if [[ -z "$mac_address" ]]; then
        echo "You must enter a MAC address! Please try again."
    else
        # Optionally: validate MAC format (basic check)
        if [[ "$mac_address" =~ ^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$ ]]; then
            echo "MAC address accepted: $mac_address"
            echo "MAC_ADDRESS=$mac_address" > .wol_env
            echo "Saved MAC address to .wol_env"
            break
        else
            echo "Invalid MAC address format! Please use XX:XX:XX:XX:XX:XX"
        fi
    fi
done

# Ask user if dashboard and server is required
while true; do
    echo "Do you need a flask server with HTML dashboard for this machine? (yes/y or no/n)"
    read response
    response=${response,,}  # convert to lowercase

    if [[ "$response" == "yes" || "$response" == "y" ]]; then
        echo "Installing flask..."
        sudo apt install python3-pip -y
        sudo apt install python3-flask -y

        # systemd service setup
        SERVICE_TEMPLATE="local_server_dashboard/local-dashboard.service.template"
        SERVICE_FILE="/etc/systemd/system/local-dashboard.service"

        # Detect current user and working directory
        CURRENT_USER="$USER"
        WORKDIR="$(pwd)/local_server_dashboard"

        echo "Setting up systemd service..."

        # Replace placeholders and copy to systemd directory
        sudo sed "s|{{USER}}|$CURRENT_USER|g; s|{{WORKDIR}}|$WORKDIR|g" "$SERVICE_TEMPLATE" | sudo tee "$SERVICE_FILE" > /dev/null

        # Reload systemd and enable service
        sudo systemctl unmask local-dashboard.service 2>/dev/null
        sudo systemctl daemon-reload
        sudo systemctl enable local-dashboard
        sudo systemctl start local-dashboard

        echo "Flask dashboard will now autostart on boot (port 80)"
        
        break
    elif [[ "$response" == "no" || "$response" == "n" ]]; then
        echo "Skipping server dashboard"
        break
    else
        echo "Please answer yes/y or no/n"
    fi
done

echo "Generating your user and local-server authentication tokens (NOT READY)"
echo "User token:"
echo openssl rand -hex 16
echo "local-server token:"
echo openssl rand -hex 16

echo "Starting local-command-polling"
nohup python3 ~/vps-wake-on-lan-no-ssh/wol_agent.py &

echo "Installation completed"