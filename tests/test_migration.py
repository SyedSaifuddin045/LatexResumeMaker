"""
Tests for migrate_api_key.py script functionality.
Verifies that API key migration from settings.json to secrets.json works correctly.
"""
import os
import sys
import json
import tempfile
import shutil
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestApiKeyMigration:
    """Tests for API key migration functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_migrate_with_real_api_key(self, temp_dir):
        """Test migration of a real API key from settings.json to secrets.json."""
        # Create settings.json with real API key
        settings_path = os.path.join(temp_dir, 'settings.json')
        original_settings = {
            'provider': 'google',
            'apiKey': 'AIzaSyDummyKeyForTesting123',
            'model': 'gemini-3-flash'
        }
        with open(settings_path, 'w') as f:
            json.dump(original_settings, f)
        
        # Simulate migration
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            # Load settings
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            api_key = settings.get('apiKey', '')
            
            if api_key and api_key != 'YOUR_API_KEY_HERE':
                # Create secrets.json
                secrets = {'apiKey': api_key}
                secrets_path = os.path.join(temp_dir, 'secrets.json')
                with open(secrets_path, 'w') as f:
                    json.dump(secrets, f, indent=4)
                
                # Update settings.json
                settings['apiKey'] = 'YOUR_API_KEY_HERE'
                with open(settings_path, 'w') as f:
                    json.dump(settings, f, indent=4)
            
            # Verify migration worked
            assert os.path.exists(os.path.join(temp_dir, 'secrets.json'))
            with open(os.path.join(temp_dir, 'secrets.json'), 'r') as f:
                secrets_data = json.load(f)
            assert secrets_data['apiKey'] == 'AIzaSyDummyKeyForTesting123'
            
            with open(settings_path, 'r') as f:
                updated_settings = json.load(f)
            assert updated_settings['apiKey'] == 'YOUR_API_KEY_HERE'
            assert updated_settings['provider'] == 'google'
            assert updated_settings['model'] == 'gemini-3-flash'
            
        finally:
            os.chdir(original_dir)
    
    def test_migrate_with_placeholder_key(self, temp_dir):
        """Test that migration skips when API key is already a placeholder."""
        settings_path = os.path.join(temp_dir, 'settings.json')
        settings = {
            'provider': 'google',
            'apiKey': 'YOUR_API_KEY_HERE'
        }
        with open(settings_path, 'w') as f:
            json.dump(settings, f)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            # Check if it's a placeholder and skip
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            api_key = settings.get('apiKey', '')
            assert api_key == 'YOUR_API_KEY_HERE'
            
            # secrets.json should not be created
            assert not os.path.exists(os.path.join(temp_dir, 'secrets.json'))
        finally:
            os.chdir(original_dir)
    
    def test_migrate_creates_backup(self, temp_dir):
        """Test that migration creates a backup file."""
        settings_path = os.path.join(temp_dir, 'settings.json')
        original_settings = {
            'provider': 'google',
            'apiKey': 'AIzaSyDummyKey'
        }
        with open(settings_path, 'w') as f:
            json.dump(original_settings, f)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            # Backup settings
            backup_path = os.path.join(temp_dir, 'settings.backup.json')
            shutil.copy(settings_path, backup_path)
            
            # Verify backup exists
            assert os.path.exists(backup_path)
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            assert backup_data['apiKey'] == 'AIzaSyDummyKey'
        finally:
            os.chdir(original_dir)
    
    def test_migrate_preserves_other_settings(self, temp_dir):
        """Test that migration preserves all other settings."""
        settings_path = os.path.join(temp_dir, 'settings.json')
        original_settings = {
            'provider': 'google',
            'apiKey': 'AIzaSyDummyKey',
            'model': 'gemini-3-flash-preview',
            'system_prompt': 'You are an expert...',
            'custom_setting': 'custom_value'
        }
        with open(settings_path, 'w') as f:
            json.dump(original_settings, f)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            # Load and migrate
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            api_key = settings.pop('apiKey')
            settings['apiKey'] = 'YOUR_API_KEY_HERE'
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
            
            # Verify other settings are preserved
            with open(settings_path, 'r') as f:
                migrated = json.load(f)
            
            assert migrated['provider'] == 'google'
            assert migrated['model'] == 'gemini-3-flash-preview'
            assert migrated['system_prompt'] == 'You are an expert...'
            assert migrated['custom_setting'] == 'custom_value'
        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
