' Silent launcher for Claude-Orphan-Cleanup-Hourly
' Wraps run-orphan-cleanup.bat with WindowStyle=0 to prevent cmd.exe flash.
' Source: wr-sentinel-2026-05-10-004 (Sentinel routed-task to Skill Hub)
' Target install location: C:\Users\Sharkitect Digital\.claude\scripts\silent-runners\run-orphan-cleanup.vbs
Set sh = CreateObject("WScript.Shell")
batPath = "C:\Users\Sharkitect Digital\.claude\scripts\run-orphan-cleanup.bat"
sh.Run """" & batPath & """", 0, False
