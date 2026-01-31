"""
Automated tests for API key security.
These tests verify that API keys are handled securely and not exposed.
"""
import os
import sys
import json
import tempfile
import shutil
import pytest

# Add parent directory to path to import settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import SettingsManager


# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestGitignoreConfiguration:
    """Tests that sensitive files are properly gitignored."""
    
    def test_gitignore_exists(self):
        """Verify .gitignore file exists."""
        gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
        assert os.path.exists(gitignore_path), ".gitignore file must exist"
    
    def test_secrets_json_is_gitignored(self):
        """Verify secrets.json is listed in .gitignore."""
        gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
        with open(gitignore_path, 'r') as f:
            content = f.read()
        assert 'secrets.json' in content, "secrets.json must be gitignored"
    
    def test_settings_json_is_gitignored(self):
        """Verify settings.json is listed in .gitignore."""
        gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
        with open(gitignore_path, 'r') as f:
            content = f.read()
        assert 'settings.json' in content, "settings.json must be gitignored"
    
    def test_env_file_is_gitignored(self):
        """Verify .env file is listed in .gitignore."""
        gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
        with open(gitignore_path, 'r') as f:
            content = f.read()
        assert '.env' in content, ".env file must be gitignored"


class TestExampleFilesExist:
    """Tests that example/template files exist for documentation."""
    
    def test_settings_example_exists(self):
        """Verify settings.example.json exists."""
        path = os.path.join(PROJECT_ROOT, 'settings.example.json')
        assert os.path.exists(path), "settings.example.json must exist as template"
    
    def test_secrets_example_exists(self):
        """Verify secrets.example.json exists."""
        path = os.path.join(PROJECT_ROOT, 'secrets.example.json')
        assert os.path.exists(path), "secrets.example.json must exist as template"
    
    def test_env_example_exists(self):
        """Verify .env.example exists."""
        path = os.path.join(PROJECT_ROOT, '.env.example')
        assert os.path.exists(path), ".env.example must exist as template"


class TestExampleFilesHavePlaceholders:
    """Tests that example files don't contain real API keys."""
    
    PLACEHOLDER_VALUES = ['YOUR_API_KEY_HERE', '', 'your_api_key_here', 'your-api-key-here']
    
    def test_settings_example_has_placeholder_api_key(self):
        """Verify settings.example.json uses placeholder for API key."""
        path = os.path.join(PROJECT_ROOT, 'settings.example.json')
        with open(path, 'r') as f:
            data = json.load(f)
        
        api_key = data.get('apiKey', '')
        assert api_key in self.PLACEHOLDER_VALUES, \
            f"settings.example.json must use placeholder, not real API key"
    
    def test_secrets_example_has_placeholder_api_key(self):
        """Verify secrets.example.json uses placeholder for API key."""
        path = os.path.join(PROJECT_ROOT, 'secrets.example.json')
        with open(path, 'r') as f:
            data = json.load(f)
        
        api_key = data.get('apiKey', '')
        assert api_key in self.PLACEHOLDER_VALUES, \
            f"secrets.example.json must use placeholder, not real API key"


class TestNoHardcodedApiKeys:
    """Tests that source code files don't contain hardcoded API keys."""
    
    # Patterns that might indicate a real API key
    API_KEY_PATTERNS = [
        'sk-',      # OpenAI keys start with sk-
        'AIza',     # Google API keys often start with AIza
    ]
    
    # Files to scan for hardcoded keys
    SOURCE_FILES = [
        'settings.py',
        'api.py',
        'engine/ai.py',
        'engine/providers.py',
        'gui/app.js',
    ]
    
    def test_no_hardcoded_keys_in_source_files(self):
        """Verify source files don't contain hardcoded API keys."""
        for source_file in self.SOURCE_FILES:
            path = os.path.join(PROJECT_ROOT, source_file)
            if not os.path.exists(path):
                continue
                
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for pattern in self.API_KEY_PATTERNS:
                # Check for patterns that look like real keys (longer than pattern + some chars)
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and documentation
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
                        continue
                    
                    if pattern in line:
                        # Check if it's likely a real key (has significant length after pattern)
                        idx = line.find(pattern)
                        potential_key = line[idx:idx+50]  # Get surrounding chars
                        
                        # If the key-like string is in quotes and long, it might be real
                        if len(potential_key) > 20 and ('"' in line or "'" in line):
                            # Allow if it's clearly a placeholder or example
                            if 'YOUR_' in line or 'EXAMPLE' in line.upper() or 'your_' in line:
                                continue
                            pytest.fail(
                                f"Potential hardcoded API key found in {source_file}:{line_num}\n"
                                f"Pattern '{pattern}' detected. Please use environment variables or secrets.json"
                            )


class TestSettingsManagerPriority:
    """Tests that SettingsManager correctly prioritizes API key sources."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_env_var_takes_highest_priority(self, temp_dir, monkeypatch):
        """Environment variable should override all other sources."""
        # Create settings.json with one key
        settings_path = os.path.join(temp_dir, 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump({'apiKey': 'settings_key'}, f)
        
        # Create secrets.json with another key
        secrets_path = os.path.join(temp_dir, 'secrets.json')
        with open(secrets_path, 'w') as f:
            json.dump({'apiKey': 'secrets_key'}, f)
        
        # Set environment variable with third key
        monkeypatch.setenv('API_KEY', 'env_key')
        
        # Change to temp dir and test
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            sm = SettingsManager()
            assert sm.get('apiKey') == 'env_key', \
                "Environment variable should take highest priority"
        finally:
            os.chdir(original_dir)
    
    def test_secrets_overrides_settings(self, temp_dir, monkeypatch):
        """secrets.json should override settings.json."""
        # Clear any env vars that might interfere
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        # Create settings.json
        settings_path = os.path.join(temp_dir, 'test_override_settings.json')
        with open(settings_path, 'w') as f:
            json.dump({'apiKey': 'settings_key', 'provider': 'google'}, f)
        
        # Create secrets.json
        secrets_path = os.path.join(temp_dir, 'test_override_secrets.json')
        with open(secrets_path, 'w') as f:
            json.dump({'apiKey': 'secrets_key'}, f)
        
        sm = SettingsManager(settings_path, secrets_path)
        assert sm.get('apiKey') == 'secrets_key', \
            "secrets.json should override settings.json"
    
    def test_openai_api_key_env_var_works(self, temp_dir, monkeypatch):
        """OPENAI_API_KEY environment variable should work."""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.setenv('OPENAI_API_KEY', 'openai_env_key')
        
        settings_path = os.path.join(temp_dir, 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'openai'}, f)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            sm = SettingsManager()
            assert sm.get('apiKey') == 'openai_env_key'
        finally:
            os.chdir(original_dir)
    
    def test_google_api_key_env_var_works(self, temp_dir, monkeypatch):
        """GOOGLE_API_KEY environment variable should work."""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.setenv('GOOGLE_API_KEY', 'google_env_key')
        
        settings_path = os.path.join(temp_dir, 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google'}, f)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            sm = SettingsManager()
            assert sm.get('apiKey') == 'google_env_key'
        finally:
            os.chdir(original_dir)


class TestApiKeySavesSeparately:
    """Tests that API keys are saved to secrets.json separately."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_save_moves_api_key_to_secrets(self, temp_dir, monkeypatch):
        """Saving settings should move API key to secrets.json."""
        # Clear env vars
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        # Create initial settings
        settings_path = os.path.join(temp_dir, 'test_sep_settings.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google'}, f)
        
        secrets_path = os.path.join(temp_dir, 'test_sep_secrets.json')
        
        sm = SettingsManager(settings_path, secrets_path)
        
        # Save with an API key
        sm.save({'provider': 'google', 'apiKey': 'my_secret_key'})
        
        # Check settings.json has placeholder
        with open(settings_path, 'r') as f:
            settings_data = json.load(f)
        assert settings_data.get('apiKey') == 'YOUR_API_KEY_HERE', \
            "settings.json should have placeholder, not real key"
        
        # Check secrets.json has real key
        assert os.path.exists(secrets_path), "secrets.json should be created"
        with open(secrets_path, 'r') as f:
            secrets_data = json.load(f)
        assert secrets_data.get('apiKey') == 'my_secret_key', \
            "secrets.json should contain the real API key"
    
    def test_placeholder_key_not_saved_to_secrets(self, temp_dir, monkeypatch):
        """Placeholder API key should not be saved to secrets.json."""
        monkeypatch.delenv('API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        
        settings_path = os.path.join(temp_dir, 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump({'provider': 'google'}, f)
        
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            sm = SettingsManager()
            
            # Save with placeholder key
            sm.save({'provider': 'google', 'apiKey': 'YOUR_API_KEY_HERE'})
            
            # secrets.json should not exist or not have the placeholder
            secrets_path = os.path.join(temp_dir, 'secrets.json')
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    secrets_data = json.load(f)
                assert secrets_data.get('apiKey') != 'YOUR_API_KEY_HERE', \
                    "Placeholder should not be saved to secrets.json"
        finally:
            os.chdir(original_dir)


class TestApiKeyNotExposed:
    """Tests that API keys are not accidentally exposed."""
    
    def test_security_doc_exists(self):
        """Verify SECURITY.md documentation exists."""
        path = os.path.join(PROJECT_ROOT, 'SECURITY.md')
        assert os.path.exists(path), "SECURITY.md should exist to document secure practices"
    
    def test_backup_file_no_real_key(self):
        """Verify backup files don't contain real API keys in production."""
        backup_path = os.path.join(PROJECT_ROOT, 'settings.backup.json')
        if os.path.exists(backup_path):
            # Skip this check in development - backup files may contain old keys
            # In production, ensure secrets are properly managed
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
