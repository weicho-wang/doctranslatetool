@echo off
echo ===================================
echo    MITranslateTool Setup Launcher
echo ===================================
echo.
echo This will set up your Python environment and dependencies.
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available on this system.
    echo Please install PowerShell or run the setup manually.
    pause
    exit /b 1
)

echo Starting PowerShell setup script...
echo.

REM Execute PowerShell script with execution policy bypass
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Setup script failed with exit code %ERRORLEVEL%
    echo Please check the output above for details.
) else (
    echo.
    echo Setup completed successfully!
)

echo.
echo Press any key to exit...
pause >nul 