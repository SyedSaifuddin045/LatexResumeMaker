"""
Migration script to move API key from settings.json to secrets.json
Run this once to secure your existing API key.
"""
import json
import os
import shutil

def migrate_api_key():
    settings_file = "settings.json"
    secrets_file = "secrets.json"
    backup_file = "settings.backup.json"
    
    # Check if settings.json exists
    if not os.path.exists(settings_file):
        print("❌ settings.json not found. Nothing to migrate.")
        return
    
    # Backup existing settings
    try:
        shutil.copy(settings_file, backup_file)
        print(f"✅ Backed up settings to {backup_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Load current settings
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except Exception as e:
        print(f"❌ Error reading settings.json: {e}")
        return
    
    # Extract API key
    api_key = settings.get('apiKey', '')
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("ℹ️  No API key found in settings.json or it's already a placeholder.")
        return
    
    # Create secrets.json with the API key
    try:
        secrets = {'apiKey': api_key}
        with open(secrets_file, 'w') as f:
            json.dump(secrets, f, indent=4)
        print(f"✅ Created {secrets_file} with your API key")
    except Exception as e:
        print(f"❌ Error creating secrets.json: {e}")
        return
    
    # Update settings.json to use placeholder
    try:
        settings['apiKey'] = 'YOUR_API_KEY_HERE'
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"✅ Updated {settings_file} with placeholder")
    except Exception as e:
        print(f"❌ Error updating settings.json: {e}")
        return
    
    print("\n✨ Migration complete!")
    print(f"   - Your API key is now in {secrets_file} (gitignored)")
    print(f"   - {settings_file} now uses a placeholder")
    print(f"   - Backup saved to {backup_file}")
    print("\n⚠️  IMPORTANT: Do NOT commit secrets.json to Git!")

if __name__ == "__main__":
    print("🔐 API Key Migration Script")
    print("=" * 50)
    migrate_api_key()
