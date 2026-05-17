@echo off
title Genesis Optimizer
echo.
echo  =========================================
echo    GENESIS OPTIMIZER - Iniciando...
echo  =========================================
echo.

cd /d "%~dp0"

pip install -r requirements.txt -q

echo.
echo  Abrindo no navegador em http://localhost:8501
echo  Pressione Ctrl+C para encerrar.
echo.

streamlit run app.py --server.headless false --browser.gatherUsageStats false
pause
