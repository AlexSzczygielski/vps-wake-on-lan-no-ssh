#!/bin/bash
# Automation script - call wakeonlan directly from your computer. 
# Replace TOKEN, PORT and VPS_BASE with your data

TOKEN=""
PORT=""
VPS_BASE="https://frog02-$PORT.wykr.es"

# Colors
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"   # resets color


echo -e "${CYAN} ▗▄▄▖▗▄▄▄▖▗▄▖ ▗▄▄▖▗▄▄▄▖    ▗▖ ▗▖▗▄▄▄▖▗▖  ▗▖▗▄▄▄  ▗▄▖ ▗▖ ▗▖ ▗▄▄▖
▐▌     █ ▐▌ ▐▌▐▌ ▐▌ █      ▐▌ ▐▌  █  ▐▛▚▖▐▌▐▌  █▐▌ ▐▌▐▌ ▐▌▐▌   
 ▝▀▚▖  █ ▐▛▀▜▌▐▛▀▚▖ █      ▐▌ ▐▌  █  ▐▌ ▝▜▌▐▌  █▐▌ ▐▌▐▌ ▐▌ ▝▀▚▖
▗▄▄▞▘  █ ▐▌ ▐▌▐▌ ▐▌ █      ▐▙█▟▌▗▄█▄▖▐▌  ▐▌▐▙▄▄▀▝▚▄▞▘▐▙█▟▌▗▄▄▞▘
                                                               
                                                               
                                                               ${RESET}"

echo "Sending request with TOKEN: $TOKEN"

# Get the response
RESPONSE=$(curl -s "$VPS_BASE/wol_request?token=$TOKEN")

# Check response and print in color
if [[ "$RESPONSE" == "Request accepted" ]]; then
    echo -e "${GREEN}$RESPONSE${RESET}"

    echo -e "${CYAN}Waiting for WOL to be sent...${RESET}"
    # Start timer
    SECONDS=0
    while true; do
        # Poll every 2 seconds
        if (( SECONDS % 2 == 0 )); then
            STATUS_WOL_PACKET=$(curl -s "$VPS_BASE/wol_status?token=$TOKEN")
        
            if [[ "$STATUS_WOL_PACKET" == "WOL_SENT" ]]; then
                echo -e "\n${GREEN}WOL was sent from local server${RESET}"
                break
            fi

            if [[ $SECONDS -gt 40 ]]; then
                echo -e "\n${RED}Request timed out${RESET}"
                break
            fi
        fi

        # Print elapsed time live
        printf "\rElapsed time: %02d:%02d" $((SECONDS/60)) $((SECONDS%60))

        # Wait a bit before polling again
        sleep 1
    done

    echo -e "${CYAN}Waiting for remote machine to turn on...${RESET}"
    # Start timer
    SECONDS=0
    while true; do
        #Poll every 2 seconds
        if (( SECONDS % 2 == 0 )); then
            STATUS_REMOTE_MACHINE=$(curl -s "$VPS_BASE/remote_machine_status?token=$TOKEN")
            
            if [[ "$STATUS_REMOTE_MACHINE" == "REMOTE_ON" ]]; then
                echo -e "\n${GREEN}Remote machine is UP${RESET}"

                echo "Starting AnyDesk..."
                open -a "AnyDesk" >/dev/null 2>&1 &
                break
            fi

            if [[ $SECONDS -gt 180 ]]; then
                echo -e "\n${RED}Request timed out${RESET}"
                break
            fi
        fi

        # Print elapsed time live
        printf "\rElapsed time: %02d:%02d" $((SECONDS/60)) $((SECONDS%60))

        # Wait a bit before polling again
        sleep 1
    done
else
    echo -e "${RED}$RESPONSE${RESET}"
fi