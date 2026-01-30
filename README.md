# ATS Resume Genius

A production-quality desktop application that uses AI to generate ATS-optimized resumes from LaTeX templates.

## Features
- **Job Description Analysis**: AI extracts keywords and rewrites content to match the job.
- **LaTeX Rendering**: Uses a real LaTeX engine for professional PDF output.
- **Live Preview**: See changes instantly in the app.
- **AI Choice**: Use Cloud (OpenAI) or Local (Ollama) models.
- **Privacy Focused**: Your API keys are stored locally.

## Setup Instructions

### Prerequisites
1. **Python 3.10+**: Make sure Python is installed and added to your PATH.
2. **LaTeX Distribution**: You need `pdflatex` to generate PDFs.
   - **Recommended**: [TeX Live](https://www.tug.org/texlive/) or [MiKTeX](https://miktex.org/).
   - Verify by running `pdflatex --version` in your terminal.

### Installation
1. Open this folder in a terminal.
2. Run `pip install -r requirements.txt`.

### Running the App
Double-click `run.bat` OR run:
```bash
python main.py
```

## How to Use
1. **Settings**: Go to the Settings tab first.
   - Select **OpenAI** and enter your API Key.
   - OR select **Local (Ollama)** if you have Ollama running locally (`llama3` or similar model recommended).
2. **Generate**:
   - Paste the **Job Description** in the text area.
   - (Optional) Paste your raw resume data in JSON format in the "Personal Data" box. If left empty, the AI will generate a sample resume based on the job.
   - Click **Generate PDF**.
3. **Export**:
   - The PDF preview will appear on the right.
   - Click "Open External" to open the PDF in your default viewer to save/print.

## Troubleshooting
- **"pdflatex not found"**: Ensure you installed TeX Live or MiKTeX and restarted your computer.
- **AI Error**: Check your API key or ensure Ollama is running (`ollama serve`).

## Project Structure
- `gui/`: HTML/CSS/JS frontend code.
- `engine/`: Python logic for AI and LaTeX.
- `templates/`: LaTeX templates (Jinja2 format).
- `api.py`: Connects the GUI to the backend.
