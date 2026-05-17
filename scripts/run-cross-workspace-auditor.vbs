' Silent launcher for cross-workspace-auditor.bat
' windowStyle=0 = hidden, bWaitOnReturn=False = fire-and-forget
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run Chr(34) & WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.claude\scripts\run-cross-workspace-auditor.bat" & Chr(34), 0, False
Set WshShell = Nothing
