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
            # Create .wol_env and add MAC_ADDRESS
            echo "MAC_ADDRESS=$mac_address" > .wol_env
            break
        else
            echo "Invalid MAC address format! Please use XX:XX:XX:XX:XX:XX"
        fi
    fi
done

# Ask user for TOKEN
while true; do
    echo "Please provide the authentication TOKEN for the VPS:"
    read token
    if [[ -z "$token" ]]; then
        echo "You must enter a TOKEN! Please try again."
    else
        echo "TOKEN accepted."
        # Append TOKEN to .wol_env
        echo "TOKEN=$token" >> .wol_env
        echo "Saved MAC address and TOKEN to .wol_env"
        break
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

        # systemd service setup for dashboard
        DASHBOARD_SERVICE_TEMPLATE="local_server_dashboard/local-dashboard.service.template"
        DASHBOARD_SERVICE_FILE="/etc/systemd/system/local-dashboard.service"
        DASHBOARD_WORKDIR="$(pwd)/local_server_dashboard"

        echo "Setting up systemd service for the dashboard..."
        sudo sed "s|{{USER}}|$USER|g; s|{{WORKDIR}}|$DASHBOARD_WORKDIR|g" "$DASHBOARD_SERVICE_TEMPLATE" | sudo tee "$DASHBOARD_SERVICE_FILE" > /dev/null
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

echo "Setting up the command polling agent as a systemd service..."

# systemd service setup for polling agent
POLLING_SERVICE_TEMPLATE="local-polling.service.template"
POLLING_SERVICE_FILE="/etc/systemd/system/local-polling.service"
PROJECT_WORKDIR="$(pwd)"

# Replace placeholders and copy to systemd directory
sudo sed "s|{{USER}}|$USER|g; s|{{WORKDIR}}|$PROJECT_WORKDIR|g" "$POLLING_SERVICE_TEMPLATE" | sudo tee "$POLLING_SERVICE_FILE" > /dev/null

# Reload systemd and enable service
sudo systemctl unmask local-polling.service 2>/dev/null
sudo systemctl daemon-reload
sudo systemctl enable local-polling
sudo systemctl start local-polling

echo "Command polling agent will now autostart on boot."
echo "Installation completed"