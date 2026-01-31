import json
import os
import sys

class SettingsManager:
    def __init__(self, filename="settings.json", secrets_filename="secrets.json"):
        # Resolve path relative to executable or script
        if getattr(sys, 'frozen', False):
             base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.dirname(os.path.abspath(__file__))
             
        self.settings_file = os.path.join(base_path, filename)
        self.secrets_file = os.path.join(base_path, secrets_filename)
        self.settings = {}
        self.load()

    def load(self):
        # Load main settings
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = {}
        
        # Load secrets from separate file if it exists
        if os.path.exists(self.secrets_file):
            try:
                with open(self.secrets_file, 'r') as f:
                    secrets = json.load(f)
                    # Merge secrets into settings (secrets take priority)
                    self.settings.update(secrets)
            except Exception as e:
                print(f"Error loading secrets: {e}")
        
        # Override with environment variables if present (highest priority)
        # Support for common API key environment variable names
        env_api_key = os.getenv('API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if env_api_key:
            self.settings['apiKey'] = env_api_key
        
        # Allow provider override via env
        if os.getenv('AI_PROVIDER'):
            self.settings['provider'] = os.getenv('AI_PROVIDER')
        
        # Allow model override via env
        if os.getenv('AI_MODEL'):
            self.settings['model'] = os.getenv('AI_MODEL')
        
        return self.settings

    def save(self, config, save_api_key_to_secrets=True):
        """Save settings. By default, API keys are saved to secrets.json separately."""
        self.settings = config
        
        # Separate API key from other settings if requested
        settings_to_save = config.copy()
        api_key = settings_to_save.get('apiKey', '')
        
        if save_api_key_to_secrets and api_key and api_key != 'YOUR_API_KEY_HERE':
            # Save API key to secrets file
            try:
                secrets = {'apiKey': api_key}
                with open(self.secrets_file, 'w') as f:
                    json.dump(secrets, f, indent=4)
                # Remove API key from main settings file
                settings_to_save['apiKey'] = 'YOUR_API_KEY_HERE'
            except Exception as e:
                print(f"Error saving secrets: {e}")
                return False
        
        # Save non-sensitive settings
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def get_all(self):
        return self.settings
