import subprocess

def get_git_version():
    try:
        # Get the latest tag
        tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0']).decode('utf-8').strip()
        return tag
    except Exception:
        return "v1.0.0"

print(get_git_version())
