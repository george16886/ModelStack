@echo off
setlocal enabledelayedexpansion
title AI Model Launcher

:menu
cls
echo ========================================================
echo              AI Model Launcher
echo ========================================================
echo.
echo  Installed models:
echo.

REM Read ollama list and build dynamic menu
set count=0
for /f "tokens=1,3" %%A in ('ollama list 2^>nul ^| findstr /v "^NAME" ^| sort') do (
    set /a count+=1
    set "model_!count!=%%A"
    set "size_!count!=%%B"
)

if !count!==0 (
    echo   No models found.
    echo   Please run: ollama pull [model_name]
    echo.
    pause
    exit
)

REM Display model list
for /l %%i in (1,1,!count!) do (
    set "name=!model_%%i!"
    set "sz=!size_%%i!"
    set "display=!name!                         "
    set "display=!display:~0,25!"
    echo   %%i. !display! (!sz! GB^)
)

echo.
echo   0. Exit
echo.
set "choice="
set /p "choice=  Select (0-!count!): "

if "!choice!"=="" goto menu
if "!choice!"=="0" exit

REM Validate input
set "valid="
for /l %%i in (1,1,!count!) do (
    if "!choice!"=="%%i" set "valid=1"
)

if not defined valid (
    echo.
    echo   Invalid choice. Please enter 0 to !count!.
    pause
    goto menu
)

REM Launch selected model
set "selected=!model_%choice%!"
echo.
echo  Launching !selected! ...
echo.
ollama launch claude --model !selected!
echo.
pause
goto menu