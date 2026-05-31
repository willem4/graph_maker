@echo off
SET PATH=C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\;%PATH%
setlocal

REM Create and bootstrap a local virtual environment for this project.
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%" >nul

set "VENV_DIR=.venv"
set "PYTHON_CMD="

where python >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD=python"
) else (
  where py >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
  )
)

if "%PYTHON_CMD%"=="" (
  echo [ERROR] Python executable was not found.
  echo Verify Windows Store Python is installed or add Python to PATH.
  popd >nul
  exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Creating virtual environment in %VENV_DIR%...
  %PYTHON_CMD% -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    popd >nul
    exit /b 1
  )
) else (
  echo [INFO] Virtual environment already exists in %VENV_DIR%.
)

echo [INFO] Writing PowerShell activation helper start_env.ps1...
> "start_env.ps1" (
  echo $GraphvizBin = "C:\Program Files\Graphviz\bin"
  echo $InkscapeBin = "C:\Program Files\Inkscape\bin"
  echo . "$PSScriptRoot\.venv\Scripts\Activate.ps1"
  echo if ^(Test-Path $GraphvizBin^) { $env:PATH = "$GraphvizBin;$env:PATH" }
  echo if ^(Test-Path $InkscapeBin^) { $env:PATH = "$env:PATH;$InkscapeBin" }
)

echo [INFO] Writing CMD activation helper start_env.cmd...
> "start_env.cmd" (
  echo set "GraphvizBin=C:\Program Files\Graphviz\bin"
  echo set "InkscapeBin=C:\Program Files\Inkscape\bin"
  echo call "%~dp0\.venv\Scripts\activate.bat"
  echo if exist "%GraphvizBin%" set "PATH=%GraphvizBin%;%PATH%"
  echo if exist "%InkscapeBin%" set "PATH=%PATH%;%InkscapeBin%"
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Failed to activate virtual environment.
  popd >nul
  exit /b 1
)

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip.
  popd >nul
  exit /b 1
)

echo [INFO] Installing project and dependencies (editable mode)...
python -m pip install -e .
if errorlevel 1 (
  echo [ERROR] Failed to install project dependencies.
  popd >nul
  exit /b 1
)

echo [OK] Environment is ready.
echo CMD: .\start_env.cmd
echo PowerShell: .\start_env.ps1

popd >nul
exit /b 0
