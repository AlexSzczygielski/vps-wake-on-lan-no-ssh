#!/bin/bash
#vps-configuration.sh
# This script is responsible for preparing the vps (alpine linux)

echo "Updating apt"

sudo apk update
sudo apk upgrade

echo "Installing required dependencies"

apk add py3-flask
apk add py3-gunicorn

echo "start gunicore flask auto service"

gunicorn -b 0.0.0.0:20432 index:app