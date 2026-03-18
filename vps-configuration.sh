#!/bin/bash
#vps-configuration.sh
# This script is responsible for preparing the vps (alpine linux)

source ./cli_ui.sh

port=""
CLIENT_TOKEN=""
SERVER_TOKEN=""

print_logo

echo "Updating apt"

sudo apk update
sudo apk upgrade

echo "Installing required dependencies"

apk add py3-flask
apk add py3-gunicorn

echo "Provide your port to configure gunicorn (e.g. 10201)"
read port

echo "Provide your Client authorization token, generated during local server setup: (NOT READY)"
read CLIENT_TOKEN

echo "Provide your local server (RPi) authorization token, generated during local server setup: (NOT READY):"
read SERVER_TOKEN

echo "start gunicorn - flask auto service"

gunicorn -b 0.0.0.0:"$port" index:app &