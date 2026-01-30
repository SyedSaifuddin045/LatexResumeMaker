import requests
import json
import os
import google.generativeai as genai

class AIEngine:
    def __init__(self):
        self.provider = "openai"
        self.api_key = ""
        self.model = "gpt-4o-mini"
        self.api_base = "https://api.openai.com/v1"

    def configure(self, provider, api_key, model):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        if provider == "google":
            genai.configure(api_key=api_key)

    def get_default_prompt(self):
        return """You are an expert Resume Writer and ATS Optimization Specialist.
Your goal is to rewrite the user's resume content to perfectly match the Job Description (JD).
Output MUST be valid JSON matching the structure below.

CRITICAL INSTRUCTION FOR LATEX:
- You are generating content for a LaTeX template.
- You MUST escape strict LaTeX special characters in your text fields.
- Replace '%' with '\%'
- Replace '&' with '\&'
- Replace '$' with '\$'
- Replace '#' with '\#'
- Replace '_' with '\_'
- Do not use markdown bold/italic (** or *) inside the strings, use LaTeX commands like \\textbf{} if absolutely necessary, but prefer plain text.

JSON Structure:
{
    "name": "Full Name",
    "contact_info": "Phone | Email | LinkedIn",
    "summary": "3-5 sentence professional summary optimized for the JD keywords.",
    "skills": ["Skill 1", "Skill 2", "Skill 3"],
    "experience": [
        {
            "role": "Job Title",
            "company": "Company Name",
            "dates": "Date Range",
            "description": ["Action verb bullet 1...", "Bullet 2..."]
        }
    ],
    "education": [
        {
            "degree": "Degree Name",
            "institution": "University Name",
            "year": "Year"
        }
    ]
}"""

    def generate_resume_content(self, job_description, user_data, system_prompt_override=None):
        if not self.api_key:
             # Return dummy data if no key (for testing/demo)
             return {
                 "name": "Jane Doe",
                 "summary": "This is a placeholder summary. Please configure an API Key in settings.",
                 "skills": ["Python", "Java", "C++"],
                 "experience": [],
                 "education": []
             }
             
        prompt = f"""
        JOB DESCRIPTION:
        {job_description}
        
        USER'S RAW DATA (Use this as base, but tailor to JD):
        {json.dumps(user_data)}
        
        Generate the JSON resume content.
        """
        
        system_rules = system_prompt_override if system_prompt_override and system_prompt_override.strip() else self.get_default_prompt()
        
        try:
            if self.provider == "openai":
                return self._call_openai(system_rules, prompt)
            elif self.provider == "google":
                return self._call_google(system_rules, prompt)
            elif self.provider == "ollama":
                return self._call_ollama(system_rules, prompt)
        except Exception as e:
            raise RuntimeError(f"AI Provider Error: {str(e)}")
        
        return {}

    def get_default_fix_prompt(self):
        return """You are a LaTeX Debugging Expert.
Your goal is to FIX the broken LaTeX code based on the provided error log.
OUTPUT ONLY THE FIXED LATEX CODE. NO MARKDOWN. NO EXPLANATIONS.

Rules:
1. Identify the error from the log (e.g., undefined control sequence, missing bracket).
2. Fix strictly the error. Do not rewrite the whole resume unless necessary.
3. Ensure all special characters (%, &, $, #, _) are escaped causing the issue.
4. Return the complete, compilable LaTeX file content.
"""

    def fix_latex_content(self, latex_source, error_log, system_prompt_override=None):
        prompt = f"""
        BROKEN LATEX SOURCE:
        {latex_source}
        
        ERROR LOG:
        {error_log}
        
        Please fix the LaTeX source. Output ONLY the fixed LaTeX code.
        """
        
        system_rules = system_prompt_override if system_prompt_override else self.get_default_fix_prompt()
        
        try:
            if self.provider == "openai":
                return self._call_openai_text(system_rules, prompt)
            elif self.provider == "google":
                return self._call_google_text(system_rules, prompt)
            elif self.provider == "ollama":
                # Ollama call is same structure
                return self._call_ollama(system_rules, prompt, format_json=False)
        except Exception as e:
            raise RuntimeError(f"AI Provider Error: {str(e)}")
            
    def fill_custom_latex(self, latex_template, job_description, user_data, system_prompt_override=None):
        prompt = f"""
        JOB DESCRIPTION:
        {job_description}
        
        USER DATA (JSON):
        {json.dumps(user_data)}
        
        TARGET LATEX TEMPLATE:
        {latex_template}
        
        INSTRUCTIONS:
        1. Use the "TARGET LATEX TEMPLATE" structure exactly.
        2. Replace all placeholder content (e.g., "Job Bullet Point", "Skill 1", "John Doe") with the provided "USER DATA".
        3. Tailor the bullet points and summary to match the "JOB DESCRIPTION".
        4. Escape all LaTeX special characters (%, &, $, #, _) in the injected content.
        5. Output ONLY the filled LaTeX code. Do not output markdown or explanations.
        """
        
        default_system = "You are an expert Resume Writer and LaTeX Specialist. Your goal is to fill the provided LaTeX template with the user's data, optimized for the Job Description."
        system_rules = system_prompt_override if system_prompt_override else default_system
        
        try:
            if self.provider == "openai":
                return self._call_openai_text(system_rules, prompt)
            elif self.provider == "google":
                return self._call_google_text(system_rules, prompt)
            elif self.provider == "ollama":
                return self._call_ollama(system_rules, prompt, format_json=False)
        except Exception as e:
            raise RuntimeError(f"AI Provider Error: {str(e)}")
            
        return ""

    def _call_openai(self, system, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        return json.loads(content)

    def _call_openai_text(self, system, prompt):
        # Text based call (not JSON forced)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _call_google(self, system, prompt):
        model = genai.GenerativeModel(self.model)
        full_prompt = f"{system}\n\n{prompt}"
        
        # Force JSON constraint in prompt since Gemini 1.5 Flash supports it better via mime_type
        response = model.generate_content(full_prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)

    def _call_google_text(self, system, prompt):
        model = genai.GenerativeModel(self.model)
        full_prompt = f"{system}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text

    def _call_ollama(self, system, prompt, format_json=True):
        url = "http://localhost:11434/api/generate"
        data = {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False
        }
        if format_json:
            data["format"] = "json"
            
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['response']
        return json.loads(content) if format_json else content
