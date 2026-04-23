@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title AI Model Launcher

:menu
cls
echo ========================================================
echo             AI 模型啟動器 (AI Model Launcher)
echo ========================================================
echo.
echo  偵測到以下已安裝的模型：
echo.

:: 讀取 ollama list 並動態建立選單
set count=0
for /f "skip=1 tokens=1,3 delims= " %%A in ('ollama list 2^>nul') do (
    set /a count+=1
    set "model_!count!=%%A"
    set "size_!count!=%%B"
)

if %count%==0 (
    echo   [!] 未偵測到任何已安裝的模型。
    echo       請先使用 ollama pull ^<model_name^> 安裝模型。
    echo.
    pause
    exit
)

:: 顯示模型清單
for /l %%i in (1,1,%count%) do (
    set "name=!model_%%i!"
    set "sz=!size_%%i!"
    :: 格式化模型名稱，補空白對齊
    set "display=!name!                         "
    set "display=!display:~0,25!"
    echo   %%i. !display! ^(!sz! GB^)
)

echo.
echo   0. 退出 (Exit)
echo.
set choice=
set /p choice="  請輸入您的選擇 (0-%count%): "

if "%choice%"=="" goto menu
if "%choice%"=="0" exit

:: 驗證輸入是否為有效數字
set "valid="
for /l %%i in (1,1,%count%) do (
    if "%choice%"=="%%i" set "valid=1"
)
if not defined valid (
    echo.
    echo   無效的選擇，請輸入 0 到 %count% 之間的數字。
    pause
    goto menu
)

:: 取得選中的模型名稱並啟動
set "selected=!model_%choice%!"
echo.
echo  正在啟動 %selected% ...
echo.
ollama launch claude --model %selected%
echo.
pause
goto menu
