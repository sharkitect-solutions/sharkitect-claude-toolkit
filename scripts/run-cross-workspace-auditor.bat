@echo off
REM Cross-workspace auditor entry point. Invoked by VBS wrapper for silent exec.
REM Subprocess child calls in cross-workspace-auditor.py MUST use CREATE_NO_WINDOW
REM per the pythonw-subprocess-no-window feedback rule (2026-05-11).
"C:\Users\Sharkitect Digital\AppData\Local\Programs\Python\Python312\pythonw.exe" "%USERPROFILE%\.claude\scripts\cross-workspace-auditor.py" >> "%USERPROFILE%\.claude\.tmp\cross-workspace-auditor.log" 2>&1
