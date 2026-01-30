import json
from config import DEFAULT_RESUME_PROMPT, DEFAULT_FIX_PROMPT, DEFAULT_CUSTOM_FILL_PROMPT
from engine.providers import OpenAIProvider, GoogleProvider, OllamaProvider

class AIEngine:
    def __init__(self):
        self.provider = None
        self.provider_name = "openai" # Default
        self.api_key = ""
        self.model = "gpt-4o-mini"

    def configure(self, provider_name, api_key, model):
        self.provider_name = provider_name
        self.api_key = api_key
        self.model = model
        self._init_provider()

    def _init_provider(self):
        if self.provider_name == "openai":
            self.provider = OpenAIProvider(self.api_key, self.model)
        elif self.provider_name == "google":
            self.provider = GoogleProvider(self.api_key, self.model)
        elif self.provider_name == "ollama":
            self.provider = OllamaProvider(self.api_key, self.model)
        else:
            self.provider = OpenAIProvider(self.api_key, self.model) # Fallback

    def get_default_prompt(self):
        return DEFAULT_RESUME_PROMPT

    def get_default_fix_prompt(self):
        return DEFAULT_FIX_PROMPT

    def generate_resume_content(self, job_description, user_data, system_prompt_override=None):
        if not self.api_key and self.provider_name != 'ollama':
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
        
        system = system_prompt_override if system_prompt_override and system_prompt_override.strip() else DEFAULT_RESUME_PROMPT
        
        try:
            return self.provider.generate_json(system, prompt)
        except Exception as e:
            raise RuntimeError(f"AI Provider Error: {str(e)}")

    def fix_latex_content(self, latex_source, error_log, system_prompt_override=None):
        prompt = f"""
        BROKEN LATEX SOURCE:
        {latex_source}
        
        ERROR LOG:
        {error_log}
        
        Please fix the LaTeX source. Output ONLY the fixed LaTeX code.
        """
        
        system = system_prompt_override if system_prompt_override else DEFAULT_FIX_PROMPT
        
        try:
            return self.provider.generate_text(system, prompt)
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
        
        system = system_prompt_override if system_prompt_override else DEFAULT_CUSTOM_FILL_PROMPT
        
        try:
            return self.provider.generate_text(system, prompt)
        except Exception as e:
            raise RuntimeError(f"AI Provider Error: {str(e)}")
