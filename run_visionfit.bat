@echo off
title VisionFit AI — Multimodal Recipe & Workout Generator
echo ========================================================
echo        VisionFit AI — Launching Multimodal Platform
echo ========================================================
echo.
echo Starting Streamlit Web Application at http://localhost:8501 ...
echo Press Ctrl+C in this terminal window to stop the server anytime.
echo.
cd /d "%~dp0visionfit-ai"
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause

