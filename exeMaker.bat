title exeMaker
pyinstaller --onefile oszRedown.py
del /f /q oszRedown.spec oszRedown.exe
copy dist\oszRedown.exe oszRedown.exe
rd /s /q __pycache__ && rd /s /q build && rd /s /q dist
pause