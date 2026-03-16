# VPS-WAKE-ON-LAN-NO-SSH

Turn on remote machine, using VPS and simple local server (e.g. RaspberryPi). This project does not require port forwarding or shell tunneling to VPS.

> Bash files are prepared for RPi 4B, so other machines might need a little adjustments.

### `Local, VPS` are the words determining which side of the project given file/script is responsible for

---

## Local Server (RaspberryPi)

### Usage
1. Install fresh OS

> For RPi I recommend PiOS Lite 64bit - it's easy to set up and to use in headless mode, via ssh.

2. Make `local-server-configuration.sh` executable:

```bash
chmod +x local-server-configuration.sh
```

3. Follow the instructions. Prepare MAC address of the device you want to wake up beforehand.

---
To reload dashboard web page (in order to see some changes) use:

```bash
sudo systemctl restart local-dashboard
```

Local server is responsible for monitoring VPS for request to turn on the comptuer. VPS updates one of it's files when user requests it. Local server fetches this file using `curl`, waiting for a specific command in this file. When curl command returns required phrase, the magic packet is sent and computer is powered on.

Additionally local server utilizes a simple dashboard with a button that allows to send magic packet, when we are logged to the home network. This simplifies the process that beforehand required using a terminal and remembering a MAC address.
---

## VPS (MIKRUS, 5 PLN TIER)
1. Setup MIKR.US

2. `git clone` this repository

3.  
```bash
chmod +x vps-configuration.sh
sudo ./vps-configuration.sh
```

VPS is based on flask for a webpage and gunicore to activate it as a daemon.