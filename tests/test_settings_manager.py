"""
Tests for SettingsManager functionality.
Verifies that settings are correctly loaded, saved, and merged from multiple sources.
"""
import os
import sys
import json
import tempfile
import shutil
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import SettingsManager


class TestSettingsManagerInit:
    """Tests for SettingsManager initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default filenames."""
        sm = SettingsManager()
        assert sm.settings_file.endswith('settings.json')
        assert sm.secrets_file.endswith('secrets.json')
    
    def test_init_with_custom_filenames(self):
        """Test initialization with custom filenames."""
        sm = SettingsManager('custom_settings.json', 'custom_secrets.json')
        assert sm.settings_file.endswith('custom_settings.json')
        assert sm.secrets_file.endswith('custom_secrets.json')


class TestSettingsManagerLoad:
    """Tests for loading settings from files."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_load_settings_file(self, temp_dir):
        """Test loading settings from settings.json."""
        settings_path = os.path.join(temp_dir, 'test_settings.json')
        test_data = {'provider': 'google', 'model': 'gemini-3-flash'}
        
        with open(settings_path, 'w') as f:
            json.dump(test_data, f)
        
        sm = SettingsManager(os.path.join(temp_dir, 'test_settings.json'))
        assert sm.get('provider') == 'google'
        assert sm.get('model') == 'gemini-3-flash'
    
    def test_load_secrets_file(self, temp_dir):
        """Test loading secrets from secrets.json."""
        # Create settings file
        settings_path = os.path.join(temp_dir, 'test_settings_3.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google'}, f)
        
        # Create secrets file
        secrets_path = os.path.join(temp_dir, 'test_secrets_3.json')
        with open(secrets_path, 'w') as f:
            json.dump({'apiKey': 'secret_key_123'}, f)
        
        sm = SettingsManager(settings_path, secrets_path)
        assert sm.get('apiKey') == 'secret_key_123'
        assert sm.get('provider') == 'google'
    
    def test_load_both_files_merge(self, temp_dir):
        """Test that both files are loaded and merged correctly."""
        settings_path = os.path.join(temp_dir, 'test_settings_4.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google', 'model': 'gemini-3-flash'}, f)
        
        secrets_path = os.path.join(temp_dir, 'test_secrets_4.json')
        with open(secrets_path, 'w') as f:
            json.dump({'apiKey': 'secret_key'}, f)
        
        sm = SettingsManager(settings_path, secrets_path)
        assert sm.get('provider') == 'google'
        assert sm.get('model') == 'gemini-3-flash'
        assert sm.get('apiKey') == 'secret_key'
    
    def test_load_missing_files(self, temp_dir):
        """Test that missing files don't cause errors."""
        sm = SettingsManager(
            os.path.join(temp_dir, 'nonexistent_settings.json'),
            os.path.join(temp_dir, 'nonexistent_secrets.json')
        )
        assert sm.get('provider') is None
        assert sm.get_all() == {}
    
    def test_load_invalid_json(self, temp_dir, capsys):
        """Test handling of invalid JSON files."""
        settings_path = os.path.join(temp_dir, 'test_settings_invalid.json')
        with open(settings_path, 'w') as f:
            f.write('{ invalid json }')
        
        # The SettingsManager should handle invalid JSON gracefully
        # It should print an error but not crash
        sm = SettingsManager(settings_path)
        # After error, settings should be empty (not loaded from invalid file)
        # Note: The error is printed to console
        assert isinstance(sm.settings, dict)
    
    def test_load_env_var_api_key(self, temp_dir, monkeypatch):
        """Test loading API key from environment variable."""
        settings_path = os.path.join(temp_dir, 'test_settings_env.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google'}, f)
        
        monkeypatch.setenv('API_KEY', 'env_api_key')
        
        sm = SettingsManager(settings_path)
        assert sm.get('apiKey') == 'env_api_key'
    
    def test_load_env_var_provider_override(self, temp_dir, monkeypatch):
        """Test provider override from environment variable."""
        settings_path = os.path.join(temp_dir, 'test_settings_prov.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google'}, f)
        
        monkeypatch.setenv('AI_PROVIDER', 'openai')
        
        sm = SettingsManager(settings_path)
        assert sm.get('provider') == 'openai'
    
    def test_load_env_var_model_override(self, temp_dir, monkeypatch):
        """Test model override from environment variable."""
        settings_path = os.path.join(temp_dir, 'test_settings_model.json')
        with open(settings_path, 'w') as f:
            json.dump({'model': 'gpt-3.5-turbo'}, f)
        
        monkeypatch.setenv('AI_MODEL', 'gpt-4')
        
        sm = SettingsManager(settings_path)
        assert sm.get('model') == 'gpt-4'


class TestSettingsManagerSave:
    """Tests for saving settings to files."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_save_to_settings_file(self, temp_dir):
        """Test saving settings to settings.json."""
        settings_path = os.path.join(temp_dir, 'test_save_settings.json')
        
        sm = SettingsManager(settings_path)
        config = {'provider': 'google', 'model': 'gemini-3-flash'}
        sm.save(config, save_api_key_to_secrets=False)
        
        # Verify file was created
        assert os.path.exists(settings_path)
        with open(settings_path, 'r') as f:
            data = json.load(f)
        assert data['provider'] == 'google'
        assert data['model'] == 'gemini-3-flash'
    
    def test_save_separates_api_key(self, temp_dir, monkeypatch):
        """Test that saving separates API key into secrets.json."""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        settings_path = os.path.join(temp_dir, 'test_save_sep_settings.json')
        secrets_path = os.path.join(temp_dir, 'test_save_sep_secrets.json')
        
        sm = SettingsManager(settings_path, secrets_path)
        config = {
            'provider': 'google',
            'model': 'gemini-3-flash',
            'apiKey': 'my_secret_key_123'
        }
        sm.save(config, save_api_key_to_secrets=True)
        
        # Check settings.json has placeholder
        with open(settings_path, 'r') as f:
            settings_data = json.load(f)
        assert settings_data['apiKey'] == 'YOUR_API_KEY_HERE'
        assert settings_data['provider'] == 'google'
        
        # Check secrets.json has the real key
        assert os.path.exists(secrets_path)
        with open(secrets_path, 'r') as f:
            secrets_data = json.load(f)
        assert secrets_data['apiKey'] == 'my_secret_key_123'
    
    def test_save_does_not_save_placeholder_key(self, temp_dir, monkeypatch):
        """Test that placeholder API keys are not saved to secrets.json."""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            sm = SettingsManager()
            config = {
                'provider': 'google',
                'apiKey': 'YOUR_API_KEY_HERE'
            }
            sm.save(config, save_api_key_to_secrets=True)
            
            # secrets.json should not be created
            # or if it is, it shouldn't contain the placeholder
            if os.path.exists('secrets.json'):
                with open('secrets.json', 'r') as f:
                    secrets_data = json.load(f)
                # Should be empty or not contain the placeholder
                assert secrets_data.get('apiKey', '') != 'YOUR_API_KEY_HERE'
        finally:
            os.chdir(original_dir)
    
    def test_save_does_not_save_placeholder_key(self, temp_dir, monkeypatch):
        """Test that placeholder API keys are not saved to secrets.json."""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        settings_path = os.path.join(temp_dir, 'test_save_placeholder_settings.json')
        secrets_path = os.path.join(temp_dir, 'test_save_placeholder_secrets.json')
        
        sm = SettingsManager(settings_path, secrets_path)
        config = {
            'provider': 'google',
            'apiKey': 'YOUR_API_KEY_HERE'
        }
        sm.save(config, save_api_key_to_secrets=True)
        
        # secrets.json should not be created or not have the placeholder
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets_data = json.load(f)
            assert secrets_data.get('apiKey', '') != 'YOUR_API_KEY_HERE'
    
    def test_save_without_api_key_separation(self, temp_dir):
        """Test saving with save_api_key_to_secrets=False."""
        settings_path = os.path.join(temp_dir, 'test_save_no_sep_settings.json')
        
        sm = SettingsManager(settings_path)
        config = {
            'provider': 'google',
            'apiKey': 'my_key'
        }
        sm.save(config, save_api_key_to_secrets=False)
        
        # API key should remain in settings.json
        with open(settings_path, 'r') as f:
            data = json.load(f)
        assert data['apiKey'] == 'my_key'
    
    def test_save_returns_true_on_success(self, temp_dir):
        """Test that save returns True on success."""
        settings_path = os.path.join(temp_dir, 'test_save_return_settings.json')
        sm = SettingsManager(settings_path)
        config = {'provider': 'google'}
        result = sm.save(config)
        assert result is True


class TestSettingsManagerGetMethods:
    """Tests for get and get_all methods."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        
        # Create test files with unique names
        settings_path = os.path.join(temp, 'test_get_settings.json')
        with open(settings_path, 'w') as f:
            json.dump({
                'provider': 'google',
                'model': 'gemini-3-flash',
                'apiKey': 'placeholder'
            }, f)
        
        yield (temp, settings_path)
        shutil.rmtree(temp)
    
    def test_get_existing_key(self, temp_dir):
        """Test getting an existing setting."""
        temp, settings_path = temp_dir
        sm = SettingsManager(settings_path)
        assert sm.get('provider') == 'google'
    
    def test_get_missing_key_returns_none(self, temp_dir):
        """Test getting a missing setting returns None."""
        temp, settings_path = temp_dir
        sm = SettingsManager(settings_path)
        assert sm.get('nonexistent') is None
    
    def test_get_with_default(self, temp_dir):
        """Test getting a setting with a default value."""
        temp, settings_path = temp_dir
        sm = SettingsManager(settings_path)
        result = sm.get('nonexistent', 'default_value')
        assert result == 'default_value'
    
    def test_get_all(self, temp_dir):
        """Test getting all settings."""
        temp, settings_path = temp_dir
        sm = SettingsManager(settings_path)
        all_settings = sm.get_all()
        assert isinstance(all_settings, dict)
        assert 'provider' in all_settings
        assert 'model' in all_settings


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
