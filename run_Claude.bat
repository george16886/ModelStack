@echo off
chcp 65001 >nul
title AI Model Launcher

:menu
cls
echo ========================================================                                                                                                    
echo                 AI 模型啟動器 (AI Model Launcher)                                                                                                    
echo ========================================================                                                                                                    
echo.
echo 請根據您的需求選擇要運行的模型：                                                                                                    
echo.
echo  1. Gemma            - [全能感知] Google 的口袋特務，能看能聽又開源，是處理日常雜事的貼心小助手。                                                                                                    
echo  2. Llama 3.2        - [邏輯推理] Meta 派來的邏輯戰神，專門對付那些能讓你大腦當機的硬核燒腦難題。                                                                                                    
echo  3. Qwen 2.5 Coder   - [程式開發] 阿里出的爆肝碼農，從寫 Code 到自動重構，它甚至比你還想趕快收工。                                                                                                    
echo.
echo  0. 退出 (Exit)                                                                                                    
echo.
set choice=
set /p choice="請輸入您的選擇 (0-3): "

if "%choice%"=="" goto menu
if "%choice%"=="1" goto run_gemma
if "%choice%"=="2" goto run_llama
if "%choice%"=="3" goto run_qwen
if "%choice%"=="0" exit

echo.
echo 無效的選擇，請輸入 0 到 3 之間的數字。                                                                                                    
pause
goto menu

:run_gemma
echo.
echo 正在啟動 Gemma... 
echo.
echo.                                                                                                   
call "d:\Claude Code\bat\gemma4.bat"
echo.
pause
goto menu

:run_llama
echo.
echo 正在啟動 Llama 3.2...  
echo.
echo.                                                                                                  
call "d:\Claude Code\bat\llama3.2.bat"
echo.
pause
goto menu

:run_qwen
echo.
echo 正在啟動 Qwen 2.5 Coder...  
echo.
echo.                                                                                                  
call "d:\Claude Code\bat\qwen2.5-coder.bat"
echo.
pause
goto menu
