# Security - API Key Management

## Overview

This application now supports **three secure methods** to store your API keys, preventing them from being accidentally committed to version control.

## Methods (in order of priority)

### 1. Environment Variables (Recommended for Production)

Set environment variables in your system:

**Windows (PowerShell):**
```powershell
$env:API_KEY = "your_api_key_here"
```

**Windows (CMD):**
```cmd
set API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export API_KEY="your_api_key_here"
```

**Supported variable names:**
- `API_KEY` (generic)
- `OPENAI_API_KEY` (for OpenAI)
- `GOOGLE_API_KEY` (for Google/Gemini)
- `AI_PROVIDER` (override provider: openai, google, ollama)
- `AI_MODEL` (override model name)

### 2. Secrets File (Recommended for Development)

Create a `secrets.json` file in the project root:

```json
{
    "apiKey": "your_actual_api_key_here"
}
```

This file is automatically ignored by Git and will never be committed.

**Setup:**
```powershell
# Copy the example file
Copy-Item secrets.example.json secrets.json

# Edit secrets.json with your real API key
notepad secrets.json
```

### 3. Settings File (Legacy - Not Recommended)

The `settings.json` file can still contain the API key, but:
- ⚠️ This file is now ignored by Git
- When you save settings through the UI, the API key is automatically moved to `secrets.json`
- The `settings.json` will contain `"apiKey": "YOUR_API_KEY_HERE"` as a placeholder

## Priority Order

The application loads API keys in this order (later ones override earlier):
1. `settings.json` - Base configuration
2. `secrets.json` - Overrides settings
3. Environment variables - Highest priority

## Migration Guide

If you already have an API key in `settings.json`:

1. **Backup your current settings:**
   ```powershell
   Copy-Item settings.json settings.backup.json
   ```

2. **Create secrets file:**
   ```powershell
   @{ apiKey = "your_key_from_settings.json" } | ConvertTo-Json | Out-File secrets.json
   ```

3. **Update settings.json:**
   ```powershell
   Copy-Item settings.example.json settings.json
   ```

4. **Verify it works** - Run the application and check if it can access the API

5. **Commit the changes:**
   ```powershell
   git add .gitignore settings.example.json secrets.example.json SECURITY.md
   git commit -m "Add secure API key management"
   ```

## Best Practices

✅ **DO:**
- Use `secrets.json` for local development
- Use environment variables for production/CI
- Keep `settings.example.json` updated as a template
- Share `settings.example.json` with your team

❌ **DON'T:**
- Commit `settings.json` with real API keys
- Commit `secrets.json`
- Share your `.env` file
- Hardcode API keys in source code

## Files

| File | Purpose | Commit to Git? |
|------|---------|----------------|
| `settings.example.json` | Template with placeholders | ✅ Yes |
| `settings.json` | Your actual settings (now without API key) | ❌ No (gitignored) |
| `secrets.example.json` | Template for secrets | ✅ Yes |
| `secrets.json` | Your actual API key | ❌ No (gitignored) |
| `.env.example` | Environment variable template | ✅ Yes |
| `.env` | Your actual environment variables | ❌ No (gitignored) |

## Troubleshooting

**"No API key found" error:**
1. Check if `secrets.json` exists and contains valid JSON
2. Check if environment variable is set: `echo $env:API_KEY` (PowerShell)
3. Check if `settings.json` exists (copy from `settings.example.json` if missing)

**API key still showing in settings.json:**
- The next time you save settings through the UI, it will automatically move to `secrets.json`
- Or manually move it now following the migration guide above
