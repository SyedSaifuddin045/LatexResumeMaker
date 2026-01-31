# Changelog

## [Unreleased]

### Security
- **Added secure API key management system**
  - Implemented multi-layer API key storage: environment variables, secrets.json, and settings.json
  - Environment variables take highest priority (production-ready)
  - `secrets.json` for local development (gitignored)
  - `settings.json` now uses placeholder "YOUR_API_KEY_HERE" by default
  - API keys are automatically separated when saving settings through the UI
  - Added support for multiple API key environment variable names: `API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`
  - Added support for provider and model overrides via environment variables

### Added
- **SettingsManager enhancements**
  - New `secrets_filename` parameter to separate sensitive from non-sensitive settings
  - Updated `save()` method with `save_api_key_to_secrets` parameter
  - Support for loading from multiple configuration sources with proper priority
  - Environment variable override support

- **Configuration files**
  - `.env.example` - Template for environment variable setup
  - `secrets.example.json` - Template for secrets file setup
  - `settings.example.json` - Template for main settings file
  - `SECURITY.md` - Comprehensive security documentation
  - `setup_secrets.ps1` - PowerShell setup script for quick configuration

- **Migration tool**
  - `migrate_api_key.py` - Migrate existing API keys from settings.json to secrets.json

- **Comprehensive test suite**
  - `tests/test_api_key_security.py` - Security validation tests (18 tests)
  - `tests/test_settings_manager.py` - SettingsManager functionality tests (16 tests)
  - `tests/test_migration.py` - Migration script tests (4 tests)
  - All tests passing: 41 tests total

### Changed
- Updated `.gitignore` to exclude `settings.json`, `secrets.json`, and `.env`
- Modified `settings.py` to support multi-source configuration loading
- Updated project README with security information

### Documentation
- Added SECURITY.md with detailed setup and best practices
- Updated README.md with security section and quick setup link
- Added comprehensive inline test documentation

### Fixed
- Improved error handling in SettingsManager for missing or invalid configuration files

## Testing
Run the test suite with:
```bash
python -m pytest tests/ -v
```

All 41 tests pass successfully, covering:
- .gitignore configuration
- Example file validation
- API key source priority
- Settings save and load operations
- Environment variable support
- Migration functionality
