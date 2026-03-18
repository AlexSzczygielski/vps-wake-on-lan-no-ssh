# VPS-WAKE-ON-LAN-NO-SSH

Turn on remote machine, using VPS and simple local server (e.g. RaspberryPi). This project does not require port forwarding or shell tunneling to VPS.

> Bash files are prepared for RPi 4B, so other machines might need a little adjustments.

### `Local, VPS` are the words determining which side of the project given file/script is responsible for

---

### How does this work?
0. **Always remember to use `HTTPS` communication, to prevent `TOKEN` leak.**

1. Sent request to VPS ([start_windows.sh](user-machine/start_windows.sh)), authorized by token you set up. 
```bash
curl "https://frog02-YOUR_PORT.wykr.es/wol_request?token=YOUR_TOKEN"
Request Accepted
```
2. Server on your local network polls the VPS endpoint. When endpoint returns the command, the magic packet is sent.

3. Dashboard on local server provides full log of sent WOL packets.

## Local Server (RaspberryPi)

### Usage
1. Install fresh OS

> For RPi I recommend PiOS Lite 64bit - it's easy to set up and to use in headless mode, via ssh.

2. Make `local-server-configuration.sh` executable and run it:

```bash
chmod +x local-server-configuration.sh
./local-server-configuration.sh
```

3. Follow the instructions. Prepare MAC address of the device you want to wake up beforehand.

---
To reload dashboard web page (in order to see some changes) use:

```bash
sudo systemctl restart local-dashboard
```

Local server is responsible for monitoring VPS for request to turn on the comptuer. Local server polls ([local-command-polling.py](local-command-polling.py)) the VPS `wol_command_endpoint` every 20 seconds, waiting for a return code `WOL_START`. When curl command returns the required phrase, the magic packet is sent and computer is powered on.

Additionally local server utilizes a simple dashboard ([index.py](local_server_dashboard/index.py)) with a button that allows to send magic packet, when we are logged to the home network. This simplifies the process that beforehand required using a terminal and remembering a MAC address.
---

## VPS (MIKRUS, 5 PLN TIER)
### Usage
1. Setup [Mikrus FROG VPS](https://frog.mikr.us/)

2. Log into your VPS and `git clone` this repository

3. Run automatic configuration **for vps** bash file:

```bash
chmod +x vps-configuration.sh
sudo ./vps-configuration.sh
```

VPS is based on flask for a webpage and gunicore to activate it as a daemon. To remotely start your PC you should use `curl "http://frog02.mikr.us:YOUR_PORT/wol_request?token=YOUR_TOKEN"`. This shouuld return `Request Accepted`. If request was accpeted then `wol_command_endpoint` returns `WOL_START` (this is polled by your server on local network - RPi).

> Remeber to log into your Mikrus VPS every 3 months, as it is shut off for users that don't do that.

### TODO:
- add separate tokens for RPi and Caller (User)
- add ssh configuration to bash files
- Remove TOKEN from Query String (move to HTTP header)
- add simple authentication on private server dashboard (prevents malicious local devices from access)
- change vps flask from gunicorn to proper daemon service
- add port configuration to [local-command-polling](local-command-polling.py)