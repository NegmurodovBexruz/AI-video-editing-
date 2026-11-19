@echo off
setlocal
rem Montaj dashbordi: http://127.0.0.1:8050
rem Local PC uses Claude subscription login; Docker keeps API mode.
cd /d "%~dp0"
rem Clear inherited gateway credentials only in this launcher and its children.
for /f "tokens=1 delims==" %%V in ('set ANTHROPIC_ 2^>nul') do set "%%V="
set "CLAUDE_CODE_OAUTH_TOKEN="
set "CLAUDE_CODE_USE_BEDROCK="
set "CLAUDE_CODE_USE_VERTEX="
set "CLAUDE_CODE_USE_FOUNDRY="
set DASH_CLAUDE_AUTH=auto
call claude.cmd auth status >nul 2>&1
if errorlevel 1 (
    echo Claude akkauntiga brauzerda kiring.
    call claude.cmd auth login --claudeai
    if errorlevel 1 exit /b 1
)
if not defined DASH_AUTH if exist "..\projects\auth\users.json" set DASH_AUTH=1
rem If the server stops (crash, killed for memory), start it again: a run it was doing is resumed once by itself.
rem Close this window to stop the dashboard for good.
:serve
python -I -u server.py %*
echo.
echo Server to'xtadi (kod %errorlevel%). 5 soniyadan keyin qayta ishga tushadi. To'xtatish uchun oynani yoping.
ping -n 6 127.0.0.1 >nul
goto serve
