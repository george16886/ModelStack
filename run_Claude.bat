@echo off
setlocal enabledelayedexpansion
title AI Model Launcher
set "CONFIGFILE=%~dp0config.txt"
set "last_model="
set "work_dir=%~dp0"

REM Load config if exists
if exist "!CONFIGFILE!" (
    for /f "tokens=1,* delims==" %%A in (!CONFIGFILE!) do (
        if "%%A"=="last_model" set "last_model=%%B"
        if "%%A"=="work_dir" set "work_dir=%%B"
    )
)

:menu
cls
echo ========================================================
echo              AI Model Launcher
echo ========================================================
echo.

REM Feature A: Show running models
set "running="
for /f "skip=1 tokens=1,3" %%A in ('ollama ps 2^>nul') do (
    if not "%%A"=="" (
        set "running=%%A"
        echo  [*] Running: %%A
    )
)
if not defined running echo  [*] Running: (none)

REM Show working directory
echo  [^>] Work dir: !work_dir!

REM Feature E: Show last used model
if defined last_model (
    echo  [!] Last used: !last_model!  ^(Press Enter to quick launch^)
)
echo.

REM Read ollama list and build dynamic menu
echo  Installed models:
echo.
set count=0
for /f "tokens=1,3" %%A in ('ollama list 2^>nul ^| findstr /v "^NAME" ^| sort') do (
    set /a count+=1
    set "model_!count!=%%A"
    set "size_!count!=%%B"
)

if !count!==0 (
    echo   No models found.
    echo   Use option P to pull a model.
    echo.
)

REM Display model list with running tag
for /l %%i in (1,1,!count!) do (
    set "name=!model_%%i!"
    set "sz=!size_%%i!"
    set "display=!name!                         "
    set "display=!display:~0,25!"
    set "tag="
    if "!name!"=="!running!" set "tag=  *RUNNING*"
    echo   %%i. !display! ^(!sz! GB^)!tag!
)

echo.
echo   P. Pull (download) a new model
echo   D. Delete a model
echo   W. Change working directory
echo   0. Exit
echo.

set "choice="
if defined last_model (
    set /p "choice=  Select (0-!count!/P/D/W) [Enter=!last_model!]: "
) else (
    set /p "choice=  Select (0-!count!/P/D/W): "
)

REM Feature E: Quick launch on empty input
if "!choice!"=="" (
    if defined last_model (
        set "selected=!last_model!"
        goto do_launch
    )
    goto menu
)

if /i "!choice!"=="P" goto pull_model
if /i "!choice!"=="D" goto delete_model
if /i "!choice!"=="W" goto change_dir
if "!choice!"=="0" exit

REM Validate numeric input
set "valid="
for /l %%i in (1,1,!count!) do (
    if "!choice!"=="%%i" set "valid=1"
)

if not defined valid (
    echo.
    echo   Invalid choice.
    pause
    goto menu
)

REM Launch selected model
set "selected=!model_%choice%!"

:do_launch
REM Save last model and work_dir to config
echo last_model=!selected!> "!CONFIGFILE!"
echo work_dir=!work_dir!>> "!CONFIGFILE!"
set "last_model=!selected!"

echo.
echo  Launching !selected! ...
echo  Working directory: !work_dir!
echo.
cd /d "!work_dir!"
ollama launch claude --model !selected!
echo.
pause
goto menu

REM ========================================
REM Feature B: Pull new model
REM ========================================
:pull_model
cls
echo ========================================================
echo              Pull New Model
echo ========================================================
echo.
echo  Examples: gemma4, llama3.2, qwen2.5-coder, phi3, mistral
echo.
set "pullname="
set /p "pullname=  Model name (or 0 to cancel): "
if "!pullname!"=="" goto menu
if "!pullname!"=="0" goto menu
echo.
echo  Downloading !pullname! ...
echo.
ollama pull !pullname!
echo.
echo  Done.
pause
goto menu

REM ========================================
REM Feature C: Delete a model
REM ========================================
:delete_model
cls
echo ========================================================
echo              Delete Model
echo ========================================================
echo.
echo  Installed models:
echo.

set dcount=0
for /f "tokens=1,3" %%A in ('ollama list 2^>nul ^| findstr /v "^NAME" ^| sort') do (
    set /a dcount+=1
    set "dmodel_!dcount!=%%A"
    set "dsize_!dcount!=%%B"
    set "ddisp=%%A                         "
    set "ddisp=!ddisp:~0,25!"
    echo   !dcount!. !ddisp! ^(%%B GB^)
)

echo.
echo   0. Cancel
echo.
set "dchoice="
set /p "dchoice=  Select model to delete (0-!dcount!): "
if "!dchoice!"=="" goto menu
if "!dchoice!"=="0" goto menu

set "dvalid="
for /l %%i in (1,1,!dcount!) do (
    if "!dchoice!"=="%%i" set "dvalid=1"
)
if not defined dvalid (
    echo   Invalid choice.
    pause
    goto menu
)

set "delmodel=!dmodel_%dchoice%!"
echo.
set "confirm="
set /p "confirm=  Delete !delmodel!? (Y/N): "
if /i not "!confirm!"=="Y" (
    echo   Cancelled.
    pause
    goto menu
)

echo.
echo  Deleting !delmodel! ...
ollama rm !delmodel!
echo.
echo  Done.
pause
goto menu

REM ========================================
REM Feature D: Change working directory
REM ========================================
:change_dir
cls
echo ========================================================
echo              Change Working Directory
echo ========================================================
echo.
echo  Current: !work_dir!
echo.
set "newdir="
set /p "newdir=  New path (or 0 to cancel): "
if "!newdir!"=="" goto menu
if "!newdir!"=="0" goto menu

if not exist "!newdir!" (
    echo.
    echo   Directory not found: !newdir!
    pause
    goto menu
)

set "work_dir=!newdir!"
REM Save config
if defined last_model (
    echo last_model=!last_model!> "!CONFIGFILE!"
) else (
    echo.> "!CONFIGFILE!"
)
echo work_dir=!work_dir!>> "!CONFIGFILE!"
echo.
echo  Working directory changed to: !work_dir!
pause
goto menu