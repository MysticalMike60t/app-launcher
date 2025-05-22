import os
import json
import shutil
from utils import resource_path

APP_NAME = "AppLauncher"
APPDATA_PATH = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
CONFIG_PATH = os.path.join(APPDATA_PATH, "config.json")

if not os.path.exists(CONFIG_PATH):
    default_config = resource_path("config.json")
    if os.path.exists(default_config):
        shutil.copy(default_config, CONFIG_PATH)

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    # Default config with folders and apps
    return {
        "apps": [
            {"name": "Notepad", "command": "notepad.exe"},
            {"name": "Calculator", "command": "calc.exe"},
            {
                "folder": "Utilities",
                "apps": [
                    {"name": "Command Prompt", "command": "cmd.exe"}
                ]
            }
        ]
    }
    pass

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")
    pass