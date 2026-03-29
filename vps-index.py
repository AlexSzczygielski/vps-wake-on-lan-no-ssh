#vps-index.py
from flask import Flask, request
import os
import time
import datetime

class WolState:
    # Both files hold only single record, it is deleted after each access
    FLAG_FILE = "/tmp/wol.flag"
    WOL_SENT_LOG = "/tmp/wol.sent"

    @classmethod
    def trigger_request_flag(cls):
        """Saves new request flag with time stamp. It implements debouncing to prevent request flooding."""
        now = time.time()
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                last = float(f.read().strip())
            if now - last < 10:  # 10 sec cooldown
                return  # ignore rapid triggers (flooding)
        with open(cls.FLAG_FILE, "w") as f:
            f.write(str(now))

    @classmethod
    def consume_request_flag(cls):
        """Checks if the request flag exists. Returns timestamp."""
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.FLAG_FILE)
            return time_stamp # Return timestamp of last request
        return None # no WOL request

    @classmethod
    def trigger_result_flag(cls,time_stamp):
        """Saves timestamps of successful WOL"""
        with open(cls.WOL_SENT_LOG, "w") as f:
            f.write(str(time_stamp))

    @classmethod
    def consume_result_flag(cls):
        """Checks if the last wol sent exists. Returns last wol sent timestamp."""
        if os.path.exists(cls.WOL_SENT_LOG):
            with open(cls.WOL_SENT_LOG, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.WOL_SENT_LOG)
            return time_stamp # Return timestamp of last request
        return None # no WOL request

    @classmethod
    def peek_request_flag(cls):
        """Checks if the request flag exists without consuming it."""
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                return f.read().strip()
        return None

    @classmethod
    def peek_result_flag(cls):
        """Checks the last WOL sent timestamp without consuming it."""
        if os.path.exists(cls.WOL_SENT_LOG):
            with open(cls.WOL_SENT_LOG, "r") as f:
                return f.read().strip()
        return None

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
def index():
    wol_pending_ts = WolState.peek_request_flag()
    last_wol_sent_ts = WolState.peek_result_flag()

    status = "Idle"
    if wol_pending_ts:
        try:
            status_time = datetime.datetime.fromtimestamp(float(wol_pending_ts)).strftime('%Y-%m-%d %H:%M:%S UTC')
            status = f"WOL request pending since {status_time}"
        except (ValueError, TypeError):
            status = "WOL request pending (invalid timestamp in flag file)"


    last_wol_info = "No WOL packet has been confirmed sent yet."
    if last_wol_sent_ts:
        try:
            sent_time = datetime.datetime.fromtimestamp(float(last_wol_sent_ts)).strftime('%Y-%m-%d %H:%M:%S UTC')
            last_wol_info = f"Last WOL packet was confirmed sent at {sent_time}"
        except (ValueError, TypeError):
            last_wol_info = "Last WOL packet was confirmed, but timestamp is invalid."

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WOL Service Status</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 2rem;
            background-color: #f8f9fa;
            color: #212529;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }}
        h1 {{
            color: #0d6efd;
            margin-bottom: 1.5rem;
        }}
        .status, .info {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 6px;
        }}
        .status {{
            background-color: #e9ecef;
        }}
        .info {{
            background-color: #e9ecef;
        }}
        strong {{
            color: #0d6efd;
        }}
        .footer {{
            margin-top: 2rem;
            font-size: 0.9rem;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>WOL Service Status</h1>
        <div class="status">
            <strong>Current Status:</strong><br>{status}
        </div>
        <div class="info">
            <strong>Last Confirmed WOL:</strong><br>{last_wol_info}
        </div>
        <div class="footer">
            <p>This is a read-only status page. No actions can be triggered from here.</p>
        </div>
    </div>
</body>
</html>
'''
    return html

@app.route('/wol_request')
def wol_request():
    """This function is called by user wanting to power on the machine. It sets the wol_command variable to true."""
    token = request.args.get("token")

    if token != TOKEN:
        return "Forbidden", 403

    WolState.trigger_request_flag()
    return "Request accepted", 202

@app.route('/wol_command')
def wol_command_endpoint():
    """This function is called by the local server in HTTP GET. Local server checks the return and acts accordingly"""
    token = request.args.get("token")

    if token != TOKEN:
        return "Forbidden", 403

    response = WolState.consume_request_flag() # It has to be assigned to variable as this method clears the flag, so this method can be called only one time
    if response:
        return response

    return ""

@app.route('/wol_ack', methods=['POST'])
def wol_ack():
    """Local server calls this to acknowledge WOL was sent"""
    token = request.form.get("token")
    ts = request.form.get("timestamp")  # optional: timestamp of WOL

    if token != TOKEN:
        return "Forbidden", 403

    # Save it as a flag
    WolState.trigger_result_flag(ts)

    return "ACK received", 200

@app.route('/wol_status', methods=['GET'])
def wol_status():
    """Returns info about the last WOL sent (from /wol_ack)"""
    token = request.args.get("token")
    if token != TOKEN:
        return "Forbidden", 403

    response = WolState.consume_result_flag() # It has to be assigned to variable as this method clears the flag, so this method can be called only one time
    if response:
        return "WOL_SENT", 200
    return {"status": "none", "message": "No WOL sent yet"}, 200