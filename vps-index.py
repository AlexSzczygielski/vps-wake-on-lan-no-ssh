#vps-index.py
from flask import Flask, request
import os
import time

class WolState:
    FLAG_FILE = "/tmp/wol.flag"

    @classmethod
    def trigger(cls):
        with open(cls.FLAG_FILE, "w") as f:
            f.write(str(time.time()))

    @classmethod
    def consume(cls):
        if os.path.exists(cls.FLAG_FILE):
            os.remove(cls.FLAG_FILE)
            return True
        return False

app = Flask(__name__)

# Load TOKEN from .wol_env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(BASE_DIR, ".wol_env")

TOKEN = None
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("SERVER_TOKEN="):
                TOKEN = line.split("=", 1)[1].strip()

if not TOKEN:
    raise Exception("SERVER_TOKEN not found in .wol_env")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/wol_request')
def wol_request():
    """This function is called by user wanting to power on the machine. It sets the wol_command variable to true."""
    token = request.args.get("token")

    if token != TOKEN:
        return "Forbidden", 403

    WolState.trigger()
    return "Request accepted", 202

@app.route('/wol_command')
def wol_command_endpoint():
    """This function is called by the local server in HTTP GET. Local server checks the return and acts accordingly"""
    token = request.args.get("token")

    if token != TOKEN:
        return "Forbidden", 403

    if WolState.consume():
        return "WOL_START"

    return ""