import os
import subprocess
import shutil
import platform
import jinja2
import base64
import tempfile
import logging

logger = logging.getLogger(__name__)

# Try to import resource_path from parent utils
try:
    from utils import resource_path
except ImportError:
    # Fallback if running directly or import fails
    import sys
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class LatexEngine:
    def __init__(self, template_dir="templates"):
        self.template_dir = resource_path(template_dir)
        self.current_process = None
        # Configure Jinja2 for LaTeX
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix=None,
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
        )

    def kill_compilation(self):
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
            return True
        return False

    def render_template(self, template_name, context):
        """Renders the Jinja2 template with context data."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise RuntimeError(f"Template rendering failed: {e}")

    def render_from_string(self, template_content, context):
        """Renders a template from a raw string."""
        try:
            template = self.env.from_string(template_content)
            return template.render(**context)
        except Exception as e:
            raise RuntimeError(f"Custom template rendering failed: {e}")

    def _ensure_pdflatex_path(self):
        """Attempts to add common LaTeX paths to environment if pdflatex is missing."""
        if shutil.which("pdflatex"):
            return True
            
        username = os.environ.get('USERNAME') or os.getlogin()
        
        # Common Paths to check
        common_paths = [
            # User specific MiKTeX (The most likely one after user install)
            r"C:\Users\{}\AppData\Local\Programs\MiKTeX\miktex\bin\x64".format(username),
            r"C:\Users\{}\AppData\Local\Programs\MiKTeX\miktex\bin".format(username),
            
            # System wide
            r"C:\Program Files\MiKTeX\miktex\bin\x64",
            r"C:\Program Files\MiKTeX 2.9\miktex\bin\x64",
            r"C:\texlive\2024\bin\windows",
            r"C:\texlive\2023\bin\windows",
            r"C:\texlive\2022\bin\windows"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                # check for exe inside
                exe_path = os.path.join(path, "pdflatex.exe")
                if os.path.exists(exe_path):
                    logger.info(f"Found pdflatex at {path}, adding to PATH...")
                    os.environ["PATH"] += os.pathsep + path
                    return True
                
        return False

    def compile_pdf(self, tex_content, output_dir=None):
        """Compiles TeX content to PDF using pdflatex. Returns path to PDF."""
        logger.info("Starting PDF Compilation...")

        # Ensure pdflatex exists
        if not self._ensure_pdflatex_path():
            raise FileNotFoundError(
                "pdflatex not found.\n"
                "Install MiKTeX (https://miktex.org) or TeX Live.\n"
                "Alternatively, download the .tex file and compile on Overleaf."
            )

        # Use local work directory to avoid temp permission/path issues
        base_work_dir = os.path.join(os.getcwd(), "work_output")
        if not os.path.exists(base_work_dir):
            os.makedirs(base_work_dir)
            
        work_dir = os.path.join(base_work_dir, "build")
        if os.path.exists(work_dir):
            try:
                shutil.rmtree(work_dir)
            except: pass # ignore if locked
        os.makedirs(work_dir, exist_ok=True)

        tex_path = os.path.join(work_dir, "resume.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)

        # Base pdflatex command
        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-output-directory",
            work_dir,
            tex_path
        ]
        
        # Enforce Path for newly installed MiKTeX
        env = os.environ.copy()
        
        logger.debug(f"Executing: {' '.join(cmd)}")
        
        def run_compilation():
            # Run twice for references
            for _ in range(2):
                 self.current_process = subprocess.Popen(
                    cmd,
                    cwd=work_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                 try:
                     stdout, stderr = self.current_process.communicate(timeout=30)
                 except subprocess.TimeoutExpired:
                     logger.error("Compilation timed out!")
                     self.current_process.terminate()
                     raise RuntimeError("Compilation timed out (30s)")
                 except Exception as e:
                     logger.error(f"Compilation Process Error: {e}")
                     raise e
                 finally:
                     # Check return code
                     rc = self.current_process.returncode if self.current_process else -1
                     self.current_process = None
                     if rc != 0:
                         logger.error(f"pdflatex returned code {rc}")
                         raise subprocess.CalledProcessError(rc, cmd, output=stdout, stderr=stderr)


        try:
            try:
                run_compilation()
            except subprocess.CalledProcessError:
                # MiKTeX First-Run/DB Issue? Try to initialize.
                # 'initexmf' is the MiKTeX configuration utility
                if shutil.which("initexmf"):
                    logger.warning("Compilation failed. Attempting MiKTeX DB refresh...")
                    subprocess.run(["initexmf", "--update-fndb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["initexmf", "--mkmaps"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    # Retry once
                    run_compilation()
                else:
                    raise

            pdf_path = os.path.join(work_dir, "resume.pdf")

            if not os.path.exists(pdf_path):
                log_path = os.path.join(work_dir, "resume.log")
                if os.path.exists(log_path):
                    with open(log_path, "r", errors="ignore") as log:
                        raise RuntimeError(
                            "PDF creation failed.\nLog tail:\n" + log.read()[-800:]
                        )
                raise RuntimeError("PDF not generated (unknown LaTeX error).")

            # Copy to output directory if requested
            final_path = pdf_path
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                final_path = os.path.join(output_dir, "resume.pdf")
                shutil.copy(pdf_path, final_path)

            return final_path, work_dir

        except subprocess.CalledProcessError as e:
            log_path = os.path.join(work_dir, "resume.log")
            error_details = []
            
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", errors="ignore") as f:
                        lines = f.readlines()
                        
                    # Scan for LaTeX errors (lines starting with !)
                    for i, line in enumerate(lines):
                        if line.strip().startswith('!'):
                            # Capture the error and the next few lines for context
                            context = lines[i:i+3] 
                            error_details.append("".join(context))
                            
                    if not error_details:
                         # No specific error found, return tail
                         error_details.append("".join(lines[-30:]))
                         
                except Exception as read_err:
                    error_details.append(f"Could not read log file: {str(read_err)}")
            else:
                error_details.append(e.stderr or "No log file produced.")

            full_error = "LaTeX Compilation Failed:\n" + "\n".join(error_details)
            raise RuntimeError(full_error)

    def generate_pdf_base64(self, template_name, context):
        """High level: render -> compile -> return base64"""
        tex_content = self.render_template(template_name, context)
        pdf_path, work_dir = self.compile_pdf(tex_content)
        
        try:
            with open(pdf_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            return b64, pdf_path
        finally:
            # Clean up temp dir? Maybe keep the last one for "Open External"
            # For now, we won't delete it immediately so Open External works, 
            # but in production we should manage this better.
            pass
