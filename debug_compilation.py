import os
import sys
import shutil
import subprocess

def run_debug():
    print("=== LATEX ENV DEBUG 2 ===")
    
    # 1. Path Setup
    username = os.environ.get('USERNAME') or os.getlogin()
    miktex_path = fr"C:\Users\{username}\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
    
    print(f"Adding to PATH: {miktex_path}")
    os.environ["PATH"] += os.pathsep + miktex_path
    
    # 2. Check Version
    print("\n--- Checking Version ---")
    try:
        res = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True)
        print("Exit Code:", res.returncode)
        print("Stdout:", res.stdout[:200]) # First 200 chars
        print("Stderr:", res.stderr)
    except FileNotFoundError:
        print("CRITICAL: pdflatex not found even after path update.")
        return
    except Exception as e:
        print(f"CRITICAL: Error running version check: {e}")
        return

    # 3. Compile Local File
    print("\n--- Compiling Local File (./debug.tex) ---")
    tex_content = r"\documentclass{article}\begin{document}Debug Success\end{document}"
    with open("debug.tex", "w") as f:
        f.write(tex_content)
        
    cmd = ["pdflatex", "-interaction=nonstopmode", "debug.tex"]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        print("Exit Code:", res.returncode)
        print("Stdout (tail):", res.stdout[-500:] if res.stdout else "EMPTY")
        print("Stderr:", res.stderr)
        
        if os.path.exists("debug.pdf"):
            print("\nSUCCESS: debug.pdf created!")
        else:
            print("\nFAILURE: debug.pdf NOT created.")
            if os.path.exists("debug.log"):
                 print("Log found. Tail:")
                 with open("debug.log", "r") as f:
                     print(f.read()[-500:])
            else:
                print("No log file found.")
    except Exception as e:
        print(f"Exception during compilation: {e}")

if __name__ == "__main__":
    run_debug()
