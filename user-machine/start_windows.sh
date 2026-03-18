#!/bin/bash
# Automation script - call wakeonlan directly from your computer. 
#Replace TOKEN and port with your data

TOKEN=""
PORT=""

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
RESPONSE=$(curl -s "https://frog02-$PORT.wykr.es/wol_request?token=$TOKEN")

# Check response and print in color
if [[ "$RESPONSE" == "Request accepted" ]]; then
    echo -e "${GREEN}$RESPONSE${RESET}"
else
    echo -e "${RED}$RESPONSE${RESET}"
fi