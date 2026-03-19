#local-command-polling.py
import requests
import subprocess
import os
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "local_server_dashboard/wol_log.txt")
env_file = os.path.join(BASE_DIR, ".wol_env")

# Load environment variables from .wol_env
env_vars = {}
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key] = value

MAC_ADDRESS = env_vars.get("MAC_ADDRESS")
TOKEN = env_vars.get("SERVER_TOKEN")

if not MAC_ADDRESS or not TOKEN:
    raise Exception("MAC_ADDRESS or SERVER_TOKEN not found in .wol_env")

VPS_URL = f"https://frog02-20432.wykr.es/wol_command?token={TOKEN}"

# get last timestamp from log
def last_wol_time():
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE) as f:
        lines = f.readlines()
    if not lines:
        return 0
    # parse last timestamp from first 19 chars (datetime format)
    last_line = lines[-1]
    try:
        dt_str = last_line.split(" - ")[0]
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
        return dt.timestamp()
    except:
        return 0

while True:
    try:
        r = requests.get(VPS_URL, timeout=5)
        logging.info(f"Requesting API {VPS_URL}")
        logging.info(f"received code: {r.status_code}")

        if r.status_code == 200:
            logging.info("Received status 200 OK")
            data = r.text.strip()
            
            if data:
                logging.info("Received data")
                # VPS returns Unix timestamp of last WOL request
                vps_ts = float(data)
                last_ts = last_wol_time()
                if vps_ts > last_ts:
                    # send magic packet
                    print("Sending WOL...")
                    for _ in range(5):
                        subprocess.run(["wakeonlan", MAC_ADDRESS])
                    # log locally
                    with open(LOG_FILE, "a") as f:
                        f.write(f"{datetime.now()} - WoL sent to {MAC_ADDRESS}\n")
            
            """
            if data == "WOL_START":
                # send magic packet
                print("Sending WOL...")
                for _ in range(5):
                    subprocess.run(["wakeonlan", MAC_ADDRESS])
                # log locally
                with open(LOG_FILE, "a") as f:
                    f.write(f"[REMOTE] {datetime.now()} - WoL sent to {MAC_ADDRESS}\n")
            """

    except Exception as e:
        print("Error contacting VPS:", e)

    import time
    time.sleep(20)  # poll every 20 sec