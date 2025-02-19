@echo off
echo Cloning pico-lib...
if exist pico-lib (
    echo Removing existing pico-lib directory...
    rmdir /s /q pico-lib
)
git clone https://gitlab.metropolia.fi/lansk/pico-lib.git
if %errorlevel% neq 0 (
    echo Failed to clone pico-lib
    exit /b %errorlevel%
)

rem Copy required files from pico-lib to lib
if not exist lib mkdir lib
if not exist lib\umqtt mkdir lib\umqtt
copy /Y pico-lib\*.py lib\
copy /Y pico-lib\*.mpy lib\
copy /Y pico-lib\umqtt\*.mpy lib\umqtt\

echo Starting installation to Pico...
rem Start web server in the current directory (project root)
start "mpremote.webserver" python -m http.server

rem Extract comport name where pico is connected
for /f "tokens=1 delims= " %%a in ('python -m mpremote connect list ^| find "2e8a:0005"') do set comport=%%a
echo Device: %comport%
timeout /t 2 /nobreak

rem Install all files according to package.json structure
python -m mpremote connect %comport% mip install --target / http://localhost:8000/

rem Terminate the web server
taskkill /fi "WINDOWTITLE eq mpremote.webserver"

rem Clean up
echo Cleaning up...
rmdir /s /q pico-lib