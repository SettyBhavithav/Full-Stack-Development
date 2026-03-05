' DevVerse AI - Silent One-Click Launcher
' Double-click this file to start everything with no terminal windows

Dim shell, root, indexPath
Set shell = CreateObject("WScript.Shell")

' Get the folder where this vbs file lives
root = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

' ---- 1. Start Docker silently ----
shell.Run "cmd /c cd /d """ & root & "docker"" && docker compose up -d", 0, True

' ---- 2. Wait for DB ----
WScript.Sleep 10000

' ---- 3. Start Node.js backend silently ----
shell.Run "cmd /c start /min powershell -WindowStyle Minimized -Command ""Set-Location '" & root & "backend'; node server.js""", 0, False

' ---- 4. Start background worker silently ----
shell.Run "cmd /c start /min powershell -WindowStyle Minimized -Command ""Set-Location '" & root & "workers'; node queue_worker.js""", 0, False

' ---- 5. Start Python AI Service silently ----
shell.Run "cmd /c start /min powershell -WindowStyle Minimized -Command ""Set-Location '" & root & "python-services'; .\venv\Scripts\activate; python app.py""", 0, False

' ---- 6. Wait a moment then open the frontend ----
WScript.Sleep 4000
indexPath = root & "frontend\index.html"
shell.Run "explorer """ & indexPath & """", 1, False

Set shell = Nothing
