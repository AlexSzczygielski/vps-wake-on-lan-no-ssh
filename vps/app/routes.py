from flask import Blueprint, request, current_app, render_template
import datetime
from .models import WolState, RemoteMachineStatus
import os

main = Blueprint('main', __name__)

@main.route('/')
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

    # Read last 20 lines of the WOL log and reverse them
    log_lines = []
    log_file = WolState.WOL_LOG
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                log_lines = f.readlines()[-20:]  # last 20 lines
            log_lines.reverse()  # newest first
        except Exception as e:
            log_lines = [f"Failed to read log: {e}\n"]

    return render_template(
        'index.html',
        status=status,
        last_wol_info=last_wol_info,
        log_lines=log_lines
    )


@main.route('/wol_request')
def wol_request():
    """This function is called by user wanting to power on the machine. It sets the wol_command variable to true."""
    token = request.args.get("token")

    if token != current_app.config['TOKEN']:
        return "Forbidden", 403

    WolState.trigger_request_flag()
    return "Request accepted", 202

@main.route('/wol_command')
def wol_command_endpoint():
    """This function is called by the local server in HTTP GET. Local server checks the return and acts accordingly"""
    token = request.args.get("token")

    if token != current_app.config['TOKEN']:
        return "Forbidden", 403

    response = WolState.consume_request_flag()
    if response:
        return response

    return ""

@main.route('/wol_ack', methods=['POST'])
def wol_ack():
    """Local server calls this to acknowledge WOL was sent"""
    token = request.form.get("token")
    ts = request.form.get("timestamp")

    if token != current_app.config['TOKEN']:
        return "Forbidden", 403

    WolState.trigger_result_flag(ts)
    return "ACK received", 200

@main.route('/wol_status', methods=['GET'])
def wol_status():
    """Returns info about the last WOL sent (from /wol_ack)"""
    token = request.args.get("token")
    if token != current_app.config['TOKEN']:
        return "Forbidden", 403

    response = WolState.consume_result_flag()
    if response:
        return "WOL_SENT", 200
    return {"status": "none", "message": "No WOL sent yet"}, 200

@main.route('/remote_machine_ack', methods=['POST'])
def remote_machine_ack():
    """Remote machine calls this to raise flag it is up and running."""
    token = request.form.get("token")
    ts = request.form.get("timestamp")

    if token != current_app.config['TOKEN']:
        return "Forbidden", 403

    RemoteMachineStatus.save_log(ts)
    return "ACK received", 200

@main.route('/remote_machine_status', methods=['GET'])
def remote_machine_status():
    """User calls this to check if the remote machine is up."""
    token = request.args.get("token")

    if token != current_app.config['TOKEN']:
        return "Forbidden", 403

    response = RemoteMachineStatus.consume_request_flag()
    if response:
        return "REMOTE_ON", 200
    return {"status": "none", "message": "REMOTE_DOWN"}, 200