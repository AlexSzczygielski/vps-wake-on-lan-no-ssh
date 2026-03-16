from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Absolute path to this script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(BASE_DIR, "wol_log.txt")

# Ensure log file exists
if not os.path.exists(log_file):
    open(log_file, "w").close()


@app.route("/")
def index():
    with open(log_file, "r") as f:
        logs = f.read()

    return render_template_string("""
    <html>
    <head>
        <title>WoL Log</title>
        <!-- <meta http-equiv="refresh" content="5"> -->
    </head>
    <body>
        <h1>Wake-on-LAN Log</h1>
        <pre>{{ logs }}</pre>
    </body>
    </html>
    """, logs=logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)