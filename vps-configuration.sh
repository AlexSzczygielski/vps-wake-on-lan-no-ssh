#!/bin/bash
#vps-configuration.sh
# This script is responsible for preparing the vps (alpine linux)

port=""
user_token=""
local_server_token=""

echo "Updating apt"

sudo apk update
sudo apk upgrade

echo "Installing required dependencies"

apk add py3-flask
apk add py3-gunicorn

echo "Provide your port to configure gunicorn (e.g. 10201)"
read port

echo "Provide your User authorization token, generated during local server setup: (NOT READY)"
read user_token

echo "Provide your local server (RPi) authorization token, generated during local server setup: (NOT READY):"
read local_server_token

echo "start gunicorn - flask auto service"

gunicorn -b 0.0.0.0:"$port" index:app &