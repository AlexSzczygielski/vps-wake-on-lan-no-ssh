from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # app.root_path is the 'app' package directory.
    project_root = os.path.abspath(os.path.join(app.root_path, '..', '..'))
    env_file = os.path.join(project_root, ".wol_env")

    TOKEN = None
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SERVER_TOKEN="):
                    TOKEN = line.split("=", 1)[1].strip()

    if not TOKEN:
        raise Exception(f"SERVER_TOKEN not found in .wol_env at {env_file}")

    app.config['TOKEN'] = TOKEN

    from . import routes
    app.register_blueprint(routes.main)

    return app
