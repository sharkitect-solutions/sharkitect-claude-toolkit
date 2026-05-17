@echo off
REM Scheduled hourly (minute :47) via Windows Task Scheduler.
REM Task name: Claude-Orphan-Cleanup-Hourly
REM Safety: --force is safe here -- Task Scheduler context has no active
REM Claude session to protect. --threshold-hours 4 prevents killing
REM fresh sessions or recent cron fires.
REM Source: 2026-04-21 -- eliminates orphan buildup from CronCreate fires.
REM 2026-05-09 retrofit: pythonw.exe instead of python.exe per Silent Execution
REM Protocol -- prevents console window flash. Source: rt-sentinel-2026-05-09-orphan-cleanup-silent-execution-retrofit.
"C:\Users\Sharkitect Digital\AppData\Local\Programs\Python\Python312\pythonw.exe" "C:\Users\Sharkitect Digital\.claude\scripts\kill-orphan-claude-processes.py" --execute --force --quiet --threshold-hours 4
