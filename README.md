# VPS-WAKE-ON-LAN-NO-SSH

Turn on remote machine, using VPS and simple local server (e.g. RaspberryPi). This project does not require port forwarding or shell tunneling to VPS.

> Bash files are prepared for RPi 4B, so other machines might need a little adjustments.

## Local Server (RaspberryPi)
1. Install fresh OS

> For RPi I recommend PiOS Lite 64bit - it's easy to set up and to use in headless mode, via ssh.

2. Make `local-server-configuration.sh` executable:

```bash
chmod +x local-server-configuration.sh
```

3. Follow the instructions. Prepare MAC address of the device you want to wake up beforehand.