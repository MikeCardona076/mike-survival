@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
chcp 65001 >nul
echo [MIKE] Preparando el juego...

set "HAS_UV="
where uv >nul 2>nul && set "HAS_UV=1"

set "PY="
if defined MIKE_PYTHON (
  "%MIKE_PYTHON%" -c "import sys" >nul 2>nul && set "PY=%MIKE_PYTHON%"
)
if not defined PY (
  py -3.12 -c "import sys" >nul 2>nul && set "PY=py -3.12"
)
if not defined PY (
  python -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)" >nul 2>nul && set "PY=python"
)

if not defined PY if defined HAS_UV (
  echo [MIKE] Instalando Python 3.12 con uv...
  uv python install 3.12
  if errorlevel 1 goto :error
)

if not exist ".venv\Scripts\python.exe" (
  echo [MIKE] Creando entorno virtual...
  if defined HAS_UV (
    uv venv --seed --python 3.12 .venv
  ) else (
    if not defined PY goto :no_python
    %PY% -m venv .venv
  )
  if errorlevel 1 goto :error
)
call ".venv\Scripts\activate.bat"

echo [MIKE] Instalando dependencias...
if defined HAS_UV (
  uv pip install --python ".venv\Scripts\python.exe" -r requirements.txt
) else (
  python -m pip install --upgrade pip >nul
  python -m pip install -r requirements.txt
)
if errorlevel 1 goto :error

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo [MIKE] .env creado. Rellena DEEPSEEK_API_KEY para hablar con Mike.
)

if defined MIKE_SKIP_RUN (
  echo [MIKE] Entorno listo.
  exit /b 0
)

echo [MIKE] Iniciando juego...
python main.py
if errorlevel 1 goto :error
exit /b 0

:no_python
echo [MIKE] No se encontro Python 3.12 ni uv.
echo Instala Python 3.12 con: winget install -e --id Python.Python.3.12
pause
exit /b 1

:error
echo [MIKE] Algo fallo. Revisa el mensaje anterior.
pause
exit /b 1
