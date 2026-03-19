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
        STATUS=$(curl -s "$VPS_BASE/wol_status?token=$TOKEN")
        
        if [[ "$STATUS" == "WOL_SENT" ]]; then
            echo -e "\n${GREEN}WOL was sent from local server${RESET}"
            break
        fi

        # Print elapsed time live
        printf "\rElapsed time: %02d:%02d" $((SECONDS/60)) $((SECONDS%60))

        # Wait a bit before polling again
        sleep 2
    done
    echo "Starting AnyDesk..."
    open -a "AnyDesk" >/dev/null 2>&1 &
else
    echo -e "${RED}$RESPONSE${RESET}"
fi