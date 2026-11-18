@echo off
cd /d "%~dp0"
"%~dp0runtime\neuron827\bin\python.exe" "%~dp0dashboard_server.py" --open %*
