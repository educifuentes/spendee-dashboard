import subprocess
import os

def get_app_version():
    # Production/Docker fallback via ENV
    env_version = os.environ.get('APP_VERSION')
    if env_version and env_version != "v1.0.0":
        return env_version

    try:
        tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0']).decode('utf-8').strip()
        return tag
    except Exception:
        return "v1.0.0"
