@echo off

REM Set your API key (or set it globally in Environment Variables)
set GEMINI_API_KEY=YOUR_API_KEY

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" ^
  -H "x-goog-api-key: %GEMINI_API_KEY%" ^
  -H "Content-Type: application/json" ^
  -X POST ^
  -d "{\"contents\":[{\"parts\":[{\"text\":\"Explain how AI works in a few words\"}]}]}"
