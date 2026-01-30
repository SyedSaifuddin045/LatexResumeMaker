import json
import os
import base64
import subprocess
import shutil
import webview
import logging
from settings import SettingsManager
from engine.ai import AIEngine
from engine.latex import LatexEngine

logger = logging.getLogger(__name__)

class Bridge:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.ai = AIEngine()
        self.latex = LatexEngine()
        self.last_pdf_path = None
        self.cancelled = False
        self.window = None
        
        # Initialize AI with loaded settings
        self.apply_settings()

    def set_window(self, window):
        self.window = window

    def save_pdf(self):
        if not self.last_pdf_path or not os.path.exists(self.last_pdf_path):
             return {"success": False, "error": "No PDF generated yet."}
             
        if not self.window:
             return {"success": False, "error": "Window not initialized."}
             
        try:
            logger.info("Opening Save File Dialog...")
            # Handle pywebview deprecation
            try:
                dialog_type = webview.FileDialog.SAVE
            except AttributeError:
                dialog_type = webview.SAVE_DIALOG
                
            file_types = ('PDF Files (*.pdf)', 'All files (*.*)')
            result = self.window.create_file_dialog(dialog_type, save_filename='resume.pdf', file_types=file_types)
            
            if result:
                # result is usually a string or tuple/list depending on OS/version
                target_path = result if isinstance(result, str) else result[0]
                shutil.copy(self.last_pdf_path, target_path)
                logger.info(f"PDF saved to: {target_path}")
                return {"success": True, "path": target_path}
                
            logger.info("Save dialog cancelled.")
            return {"success": False, "error": "Cancelled"}
        except Exception as e:
            logger.error(f"Save PDF Error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def apply_settings(self):
        settings = self.settings_manager.get_all() if hasattr(self.settings_manager, 'get_all') else self.settings_manager.settings
        self.ai.configure(
            settings.get('provider', 'openai'), 
            settings.get('apiKey', ''), 
            settings.get('model', 'gpt-4o-mini')
        )
        return settings

    def load_settings(self):
        return self.settings_manager.load()

    def save_settings(self, config):
        if self.settings_manager.save(config):
            self.apply_settings()
            return {"success": True}
        return {"success": False, "error": "Failed to save settings"}

    def cancel_generation(self):
        self.cancelled = True
        self.latex.kill_compilation()
        return True

    def get_default_prompt(self):
        return self.ai.get_default_prompt()

    def get_default_fix_prompt(self):
        return self.ai.get_default_fix_prompt()

    def fix_latex(self, payload):
        try:
            self.cancelled = False
            source = payload.get('source')
            error = payload.get('error')
            fix_prompt = self.settings_manager.get('system_prompt_fix')
            
            fixed_content = self.ai.fix_latex_content(source, error, system_prompt_override=fix_prompt)
            
            if self.cancelled: return {"success": False, "error": "Cancelled by user"}
            return {"success": True, "fixed_content": fixed_content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_latex_source(self, payload):
        try:
            self.cancelled = False
            jd = payload.get('job_description')
            template = payload.get('template_name')
            raw_user_data = payload.get('user_data', '{}')
            custom_content = payload.get('custom_template_content')
            
            user_data = {}
            if raw_user_data and raw_user_data.strip():
                try:
                     user_data = json.loads(raw_user_data)
                except:
                     return {"success": False, "error": "Invalid User Data JSON"}

            if self.cancelled: return {"success": False, "error": "Cancelled"}

            system_prompt = self.settings_manager.get('system_prompt')

            # Branch 1: Custom Template (Direct Fill)
            if template == 'custom' and custom_content:
                tex_content = self.ai.fill_custom_latex(custom_content, jd, user_data, system_prompt_override=system_prompt)
                if self.cancelled: return {"success": False, "error": "Cancelled"}
                return {"success": True, "tex_content": tex_content}

            # Branch 2: Standard Template
            optimized_content = self.ai.generate_resume_content(jd, user_data, system_prompt_override=system_prompt)
            if self.cancelled: return {"success": False, "error": "Cancelled"}
            
            tex_content = self.latex.render_template(template, optimized_content)
            return {"success": True, "tex_content": tex_content}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def compile_pdf(self, tex_content):
        try:
            pdf_path, _ = self.latex.compile_pdf(tex_content)
            self.last_pdf_path = pdf_path
            
            with open(pdf_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
            return {"success": True, "pdf_base64": pdf_b64}
            
        except FileNotFoundError as e:
            return {"success": False, "error": str(e), "tex_content": tex_content, "no_latex": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_current_pdf(self):
        if self.last_pdf_path and os.path.exists(self.last_pdf_path):
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
