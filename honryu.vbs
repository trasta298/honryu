Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "uv run main.py", 0, False
Set WshShell = Nothing
