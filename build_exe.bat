@echo off
echo ==========================================
echo      Gerador de PDF - Build Script
echo ==========================================
echo.
echo 1. Instalando dependencias necessarias...
pip install -r requirements.txt

echo.
echo 2. Limpando builds anteriores...
rmdir /s /q build dist
del /q *.spec

echo.
echo 3. Gerando executavel...
echo Isso pode levar alguns minutos.
python -m PyInstaller --noconfirm --onefile --windowed --name "GeradorPDF" --icon=NONE --add-data "templates;templates" --add-data "static;static" desktop_main.py

echo.
echo ==========================================
echo              CONCLUIDO!
echo ==========================================
echo O executavel foi criado na pasta 'dist'.
echo Voce pode mover o arquivo 'GeradorPDF.exe' para onde quiser.
echo.
pause
