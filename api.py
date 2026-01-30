import json
import os
import sys
import subprocess
import base64
from engine.ai import AIEngine
from engine.latex import LatexEngine

class Bridge:
    def __init__(self):
        self.ai = AIEngine()
        self.latex = LatexEngine()
        self.last_pdf_path = None
        
        # Resolve settings path reliably
        if getattr(sys, 'frozen', False):
             # Running as compiled exe
             base_path = os.path.dirname(sys.executable)
        else:
             # Running from source
             base_path = os.path.dirname(os.path.abspath(__file__))
             
        self.settings_file = os.path.join(base_path, "settings.json")
        self.settings = {}
        self.cancelled = False
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
                self.ai.configure(
                    self.settings.get('provider', 'openai'), 
                    self.settings.get('apiKey', ''), 
                    self.settings.get('model', 'gpt-4o-mini')
                )
        return self.settings

    def cancel_generation(self):
        self.cancelled = True
        return True

    def save_settings(self, config):
        """
        config: { provider, apiKey, model, system_prompt }
        """
        self.settings = config
        with open(self.settings_file, 'w') as f:
            json.dump(config, f)
            
        # apply config
        self.ai.configure(
            config.get('provider'), 
            config.get('apiKey'), 
            config.get('model')
        )
        return {"success": True}

    def get_default_prompt(self):
        return self.ai.get_default_prompt()

    def get_default_fix_prompt(self):
        return self.ai.get_default_fix_prompt()

    def fix_latex(self, payload):
        """
        payload: { source: str, error: str }
        """
        try:
            self.cancelled = False # Reset flag on start
            source = payload.get('source')
            error = payload.get('error')
            
            # Use saved fix prompt if available
            fix_prompt = self.settings.get('system_prompt_fix')
            
            # AI Call (blocking)
            fixed_content = self.ai.fix_latex_content(source, error, system_prompt_override=fix_prompt)
            
            if self.cancelled:
                return {"success": False, "error": "Cancelled by user"}
                
            return {"success": True, "fixed_content": fixed_content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_latex_source(self, payload):
        """
        payload: { job_description, template_name, user_data (json string), custom_template_content }
        """
        try:
            self.cancelled = False # Reset flag
            jd = payload.get('job_description')
            template = payload.get('template_name')
            raw_user_data = payload.get('user_data', '{}')
            custom_content = payload.get('custom_template_content')
            
            # 1. Parse User Data
            user_data = {}
            if raw_user_data and raw_user_data.strip():
                try:
                    user_data = json.loads(raw_user_data)
                except:
                    return {"success": False, "error": "Invalid User Data JSON"}
            
            if self.cancelled: return {"success": False, "error": "Cancelled"}

            # Use saved system prompt if available
            system_prompt = self.settings.get('system_prompt')
            
            # BRANCH: Custom Template (Direct Fill)
            if template == 'custom' and custom_content:
                tex_content = self.ai.fill_custom_latex(custom_content, jd, user_data, system_prompt_override=system_prompt)
                
                if self.cancelled: return {"success": False, "error": "Cancelled"}
                
                return {"success": True, "tex_content": tex_content}
            
            # BRANCH: Standard Template (JSON -> Jinja)
            
            # 2. AI Generation (Blocking)
            optimized_content = self.ai.generate_resume_content(jd, user_data, system_prompt_override=system_prompt)
            
            if self.cancelled: return {"success": False, "error": "Cancelled"}
            
            # 3. Render Latex Template (Do not compile yet)
            tex_content = self.latex.render_template(template, optimized_content)
                
            return {"success": True, "tex_content": tex_content}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def compile_pdf(self, tex_content):
        try:
            pdf_path, work_dir = self.latex.compile_pdf(tex_content)
            self.last_pdf_path = pdf_path
            
            # Read Base64
            with open(pdf_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            return {"success": True, "pdf_base64": pdf_b64}
            
        except FileNotFoundError as e:
            return {
                "success": False, 
                "error": str(e), 
                "tex_content": tex_content,
                "no_latex": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_current_pdf(self):
        if self.last_pdf_path and os.path.exists(self.last_pdf_path):
             # Cross-platform open
             if os.name == 'nt':
                 os.startfile(self.last_pdf_path)
             else:
                 subprocess.call(('xdg-open', self.last_pdf_path))
             return True
        return False
        
    def open_url(self, url):
        if os.name == 'nt':
            os.startfile(url)
        return True
