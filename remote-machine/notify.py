#!/usr/bin/env python3
#notify.py
# Send notification that the designated machine has completed turning on
# to the vps.

import requests
import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)

VPS_URL_ACK_REMOTE_ON = ""
TOKEN = ""

# Notify VPS
for _ in range(5):
    try:
        notify_resp = requests.post(
            VPS_URL_ACK_REMOTE_ON,
            data={
                "token": TOKEN,
                "timestamp": datetime.datetime.now().timestamp()
            },
            timeout=5
        )

        if notify_resp.status_code == 200:
            logging.info("Remote ON ACK sent")
            break

        if notify_resp.status_code != 200:
            logging.error(f"Bad ACK response: {notify_resp.text}")

    except Exception as e:
        logging.error(f"Failed to send remote on ACK: {e}")
        time.sleep(3)