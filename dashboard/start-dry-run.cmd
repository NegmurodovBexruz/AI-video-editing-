@echo off
rem Sinov rejimi: soxta agent, Claude Code va Higgsfield chaqirilmaydi, kredit sarflanmaydi.
cd /d "%~dp0"
set DASH_DRY_RUN=1
python server.py %*
