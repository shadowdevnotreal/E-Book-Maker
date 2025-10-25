@echo off
REM E-Book Maker - One-Click Start (with auto-setup)
SETLOCAL EnableDelayedExpansion

echo ================================================================
echo E-Book Maker - Starting...
echo ================================================================
echo.

REM Initialize setup state file if not exists
IF NOT EXIST .setup_state (
    echo not_started > .setup_state
)

REM Read current setup state
SET /P SETUP_STATE=<.setup_state

REM Check if setup was just completed - if so, try refreshing PATH
IF "!SETUP_STATE!"=="setup_complete" (
    echo [INFO] Previous setup detected as complete
    goto :check_tools
)

IF "!SETUP_STATE!"=="setup_needs_reboot" (
    echo ================================================================
    echo REBOOT REMINDER
    echo ================================================================
    echo.
    echo Previous setup completed but requires a system reboot.
    echo.
    SET /P SKIP_CHECK="Did you already reboot? (Y/N): "
    IF /I "!SKIP_CHECK!"=="Y" (
        echo Refreshing environment...
        REM Try to refresh PATH from registry
        powershell -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')"
        echo setup_complete > .setup_state
        goto :check_tools
    ) ELSE (
        echo.
        echo Please reboot your computer and run start.bat again.
        SET /P REBOOT_NOW="Reboot now? (Y/N): "
        IF /I "!REBOOT_NOW!"=="Y" (
            echo Rebooting in 10 seconds... Press Ctrl+C to cancel
            shutdown /r /t 10
        )
        pause
        exit /b 1
    )
)

:check_tools
REM Check Python first
echo Checking dependencies...
WHERE python >nul 2>&1
IF !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.7+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   [OK] Python found

REM Check for pandoc
WHERE pandoc >nul 2>&1
SET PANDOC_OK=!ERRORLEVEL!

IF !PANDOC_OK! EQU 0 (
    echo   [OK] Pandoc found
    echo setup_complete > .setup_state
    goto :start_app
)

REM Pandoc not found - check if we already tried setup
IF "!SETUP_STATE!"=="setup_complete" (
    echo.
    echo [WARNING] Setup was marked complete, but pandoc is still not accessible.
    echo This might mean:
    echo   1. Pandoc is not installed
    echo   2. You haven't rebooted after PATH update
    echo   3. Pandoc is installed in a non-standard location
    echo.
    SET /P RETRY_SETUP="Try running setup again? (Y/N): "
    IF /I NOT "!RETRY_SETUP!"=="Y" (
        echo.
        echo Cannot proceed without pandoc. Exiting.
        echo.
        echo Manual installation: https://pandoc.org/installing.html
        pause
        exit /b 1
    )
    echo not_started > .setup_state
)

REM Pandoc not found and setup not completed - offer to run setup
echo.
echo ================================================================
echo SETUP REQUIRED
echo ================================================================
echo.
echo E-Book Maker requires pandoc, which is not in your PATH.
echo.
echo This setup will:
echo   1. Scan for installed tools (pandoc, wkhtmltopdf, pdflatex)
echo   2. Add their locations to Windows PATH automatically
echo   3. May require a system REBOOT to take effect
echo.
echo NOTE: If you just installed these tools, a reboot may help.
echo.
SET /P SETUP_CONFIRM="Run automatic PATH setup? (Y/N): "

IF /I NOT "!SETUP_CONFIRM!"=="Y" (
    echo.
    echo Setup cancelled. Cannot start without pandoc.
    echo.
    echo To install manually:
    echo   - Pandoc: https://pandoc.org/installing.html
    echo   - wkhtmltopdf (optional): https://wkhtmltopdf.org/
    echo.
    echo Or run: "win files\SETUP-WINDOWS.bat"
    echo.
    pause
    exit /b 1
)

echo.
echo Running PATH setup...
echo setup_running > .setup_state

REM Run PowerShell setup script with admin rights
powershell -Command "Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0win files\setup-path.ps1\"' -Verb RunAs -Wait"

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ERROR] Setup script failed or was cancelled.
    echo Please try running manually from "win files" folder.
    pause
    exit /b 1
)

REM Check if setup made changes
IF EXIST ".setup_completed" (
    echo.
    echo [SUCCESS] PATH has been updated!
    echo.
    echo ================================================================
    echo NEXT STEPS
    echo ================================================================
    echo.
    echo For PATH changes to take effect, you have two options:
    echo.
    echo   Option 1: REBOOT your computer (recommended)
    echo   Option 2: Close ALL command prompts and open a new one
    echo.
    echo After that, run start.bat again.
    echo.
    echo setup_needs_reboot > .setup_state
    del .setup_completed

    SET /P REBOOT_NOW="Reboot now? (Y/N): "
    IF /I "!REBOOT_NOW!"=="Y" (
        echo Rebooting in 10 seconds... Press Ctrl+C to cancel
        shutdown /r /t 10
        exit /b 0
    ) ELSE (
        echo.
        echo Remember to reboot or restart your command prompt!
        pause
        exit /b 0
    )
) ELSE (
    echo.
    echo [INFO] No PATH changes were needed.
    echo Tools might already be in PATH, or not installed.
    echo.
    echo Checking again...
    WHERE pandoc >nul 2>&1
    IF !ERRORLEVEL! EQU 0 (
        echo [OK] Pandoc is now accessible!
        echo setup_complete > .setup_state
        goto :start_app
    ) ELSE (
        echo.
        echo [ERROR] Pandoc still not found.
        echo.
        echo Possible issues:
        echo   1. Pandoc is not installed - Install from: https://pandoc.org/
        echo   2. Pandoc is installed but in a non-standard location
        echo   3. You need to reboot for PATH changes to take effect
        echo.
        pause
        exit /b 1
    )
)

:start_app
REM Tools are accessible - proceed with normal startup
echo [OK] All dependencies ready

REM Check if virtual environment exists
IF NOT EXIST "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    IF !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
CALL venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Installing Python dependencies...
echo (Flask, Pillow, PyPDF2, reportlab, python-docx)
echo.
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo [WARNING] Some packages may have failed to install
    echo Try running manually: pip install -r requirements.txt
    echo.
    pause
)

REM Start the server
echo.
echo ================================================================
echo Starting E-Book Maker Web Server...
echo ================================================================
echo.
echo Server will open at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python server.py

REM Deactivate on exit
CALL venv\Scripts\deactivate.bat
