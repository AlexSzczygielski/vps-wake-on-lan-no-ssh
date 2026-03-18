#!/bin/bash
#local-server-configuration.sh
# This script is responsible for preparing the local server (RPi) after fresh install

source ./cli_ui.sh

mac_address=""

print_logo

echo "This script is responsible for preparing the local server (RPi) after fresh install"

print_blue "Updating apt"

sudo apt update
sudo apt upgrade -y

print_blue "Installing required dependencies"

sudo apt install wakeonlan -y
sudo apt install git -y
sudo apt install openssl -y

# Ask user for MAC address
while true; do
    print_blue "Now provide the MAC address of the machine that is meant to be switched on using Wake-on-LAN"
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
            print_success "Saved MAC address to .wol_env"
            break
        else
            echo "Invalid MAC address format! Please use XX:XX:XX:XX:XX:XX"
        fi
    fi
done

# Ask user if dashboard and server is required
while true; do
    print_blue "Do you need a flask server with HTML dashboard for this machine? (yes/y or no/n)"
    read response
    response=${response,,}  # convert to lowercase

    if [[ "$response" == "yes" || "$response" == "y" ]]; then
        echo "Installing flask..."
        sudo apt install python3-pip -y
        sudo apt install python3-flask -y

        # systemd service setup
        DASHBOARD_SERVICE_TEMPLATE="local_server_dashboard/local-dashboard.service.template"
        DASHBOARD_SERVICE_FILE="/etc/systemd/system/local-dashboard.service"

        # Detect current user and working directory
        CURRENT_USER=$(logname)
        DASHBOARD_WORKDIR="$(pwd)/local_server_dashboard"

        echo "Setting up systemd service for the dashboard"

        # Replace placeholders and copy to systemd directory
        sudo sed "s|{{USER}}|$CURRENT_USER|g; s|{{WORKDIR}}|$DASHBOARD_WORKDIR|g" "$DASHBOARD_SERVICE_TEMPLATE" | sudo tee "$DASHBOARD_SERVICE_FILE" > /dev/null

        # Reload systemd and enable service
        sudo systemctl unmask local-dashboard.service 2>/dev/null
        sudo systemctl daemon-reload
        sudo systemctl enable local-dashboard
        sudo systemctl start local-dashboard
        print_success "Flask dashboard will now autostart on boot (port 80)"
        
        break
    elif [[ "$response" == "no" || "$response" == "n" ]]; then
        print_success "Skipping server dashboard"
        break
    else
        echo "Please answer yes/y or no/n"
    fi
done

# Command polling
print_blue "Setting up the command polling agent as a systemd service..."

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

print_success "Command polling agent will now autostart on boot."

#Key generation
# Ask user about key generation
while true; do
    CLIENT_TOKEN=""
    SERVER_TOKEN=""

    print_blue "Do you want to provide server and client TOKENS or do you want auto-generate them?"
    echo "(auto/a or provide/p)?"

    read response
    response=${response,,}  # convert to lowercase

    # Check if input is empty
    if [[ "$response" == "auto" || "$response" == "a" ]]; then
        echo "Auto generating TOKENS"
        echo "Generating your client and server authentication tokens"
        CLIENT_TOKEN=$(openssl rand -hex 32)
        SERVER_TOKEN=$(openssl rand -hex 32)
        echo "CLIENT_TOKEN=$CLIENT_TOKEN" | tee -a .wol_env
        echo "SERVER_TOKEN=$SERVER_TOKEN" | tee -a .wol_env
        print_success "TOKENS saved"
        break
    elif [[ "$response" == "provide" || "$response" == "p" ]]; then
        echo "Enter your keys"
        echo "CLIENT_TOKEN:"
        read CLIENT_TOKEN
        echo "SERVER_TOKEN:"
        read SERVER_TOKEN
        echo "CLIENT_TOKEN=$CLIENT_TOKEN" | tee -a .wol_env
        echo "SERVER_TOKEN=$SERVER_TOKEN" | tee -a .wol_env
        print_success "TOKENS saved"
        break
    else
        echo "Please answer auto/a or provide/p"
    fi
done



print_success "Installation completed, your TOKENS are available in .wol_env - you will need them to configure your VPS and CLIENT."