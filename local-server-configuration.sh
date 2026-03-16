#!/bin/bash
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
            echo "MAC_ADDRESS=$mac_address" > ~/.wol_env
            echo "Saved MAC address to ~/.wol_env"
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

        echo "Starting Flask dashboard in the background..."
        cd local_server_dashboard || exit
        nohup python3 index.py &
        echo "Flask dashboard running at http://<raspberry_pi_ip>:5000/"
        break
    elif [[ "$response" == "no" || "$response" == "n" ]]; then
        echo "Skipping server dashboard"
        break
    else
        echo "Please answer yes/y or no/n"
    fi
done



echo "Installation completed"