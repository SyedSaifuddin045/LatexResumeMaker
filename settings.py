import json
import os
import sys

class SettingsManager:
    def __init__(self, filename="settings.json"):
        # Resolve path relative to executable or script
        if getattr(sys, 'frozen', False):
             base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.dirname(os.path.abspath(__file__))
             
        self.settings_file = os.path.join(base_path, filename)
        self.settings = {}
        self.load()

    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = {}
        return self.settings

    def save(self, config):
        self.settings = config
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def get_all(self):
        return self.settings
