@echo off
setlocal EnableExtensions

REM === Add MiKTeX to PATH ===
set "MIKTEX_BIN=C:\Users\SyedSaifuddin\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
set "PATH=%MIKTEX_BIN%;%PATH%"

REM === CONFIG ===
set "WORK_DIR=%CD%\work"
set "TEX_FILE=%CD%\resume.tex"
set "PDF_NAME=resume.pdf"

REM === Ensure work directory exists ===
if not exist "%WORK_DIR%" mkdir "%WORK_DIR%"

REM === Run pdflatex ===
pdflatex -interaction=nonstopmode -output-directory "%WORK_DIR%" "%TEX_FILE%" ^
  > "%WORK_DIR%\pdflatex_stdout.txt" 2> "%WORK_DIR%\pdflatex_stderr.txt"

REM === Check if PDF was generated ===
if not exist "%WORK_DIR%\%PDF_NAME%" (
    echo PDF generation FAILED.

    if exist "%WORK_DIR%\resume.log" (
        call :PRINT_LOG_TAIL "%WORK_DIR%\resume.log"
    ) else (
        echo No log file found.
    )

    exit /b 1
)

echo PDF generated successfully.
echo Output: %WORK_DIR%\%PDF_NAME%
exit /b 0


:PRINT_LOG_TAIL
echo ==== Log tail (last 500 chars) ====
powershell -NoProfile -Command ^
  "$log = Get-Content '%~1' -Raw; " ^
  "if ($log.Length -gt 500) { $log.Substring($log.Length - 500) } else { $log }"
exit /b 0
