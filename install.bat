@echo off
echo installing Python depencenies...
pip install PyQt5 speechrecognition pyaudio requests python-dotenv PyPDF2 python-docx pdfplumber
if %errorlevel% neq 0 (
    echo failed! check network.
    pause
    exit /b 1
)
echo install complete!
pause