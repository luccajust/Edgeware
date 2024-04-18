@echo off
color 5d
pushd %~dp0
if exist hid_time.dat (
    echo Nice try cutie~
    pause
) else (
    taskkill /F /IM python3.11.exe
    pause
)