#index.py
from flask import Flask, render_template, redirect, url_for
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
log_file = os.path.join(BASE_DIR, "wol_log.txt")
env_file = os.path.join(PROJECT_ROOT, ".wol_env")

if not os.path.exists(log_file):
    open(log_file, "w").close()

MAC_ADDRESS = None
try:
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("MAC_ADDRESS="):
                    MAC_ADDRESS = line.strip().split("=")[1]
    else:
        raise Exception("MAC_ADDRESS not found in file")

except Exception as e:
    print(f"Reading MAC_ADDRESS failed: {e}")



@app.route("/")
def index():
    with open(log_file) as f:
        logs = f.read()
    return render_template("index.html", logs=logs)


@app.route("/wake", methods=["POST"])
def wake():
    try:
        if MAC_ADDRESS:
            subprocess.run(["wakeonlan", MAC_ADDRESS])
            with open(log_file, "a") as f:
                f.write(f"{datetime.now()} - WoL sent to {MAC_ADDRESS}\n")
        else:
            raise Exception("No MAC_ADDRESS")
    
    except Exception as e:
        print(f"Magic packet failed: {e}")
    
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)