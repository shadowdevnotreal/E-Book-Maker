# E-Book Maker Setup Troubleshooting Guide

## Overview

The `start.bat` script now includes intelligent setup detection to avoid the infinite loop issue where it continuously tries to install PATH requirements.

## How the Fixed Setup Works

### State Tracking

The script uses a `.setup_state` file to track the setup progress:

- **`not_started`** - Initial state, no setup has been run
- **`setup_running`** - Setup is currently in progress
- **`setup_needs_reboot`** - Setup completed, but system reboot is required
- **`setup_complete`** - Setup is fully complete and tools are accessible

### Improved Flow

1. **First Run**: Script checks if pandoc is accessible
2. **If Not Found**: Offers to run automatic PATH setup
3. **After Setup**: Creates a completion flag and requests reboot
4. **After Reboot**: Checks state and verifies tools are accessible
5. **Smart Detection**: Won't re-run setup if already completed

## Common Issues and Solutions

### Issue 1: Script Keeps Asking to Run Setup

**Cause**: Pandoc is not actually installed, or is in a non-standard location

**Solution**:
1. Verify pandoc is installed: Check `C:\Program Files\Pandoc` or `%LOCALAPPDATA%\Pandoc`
2. If not installed, download from: https://pandoc.org/installing.html
3. After installation, run `start.bat` again

### Issue 2: "Setup complete but pandoc not found"

**Cause**: PATH changes haven't taken effect yet

**Solutions**:
- **Option 1** (Recommended): Reboot your computer
- **Option 2**: Close ALL command prompt windows and open a fresh one
- **Option 3**: Delete `.setup_state` file and run setup again after rebooting

### Issue 3: Setup Runs But Nothing Changes

**Cause**: PowerShell script requires Administrator privileges

**Solution**:
1. Click "Yes" when Windows asks for admin permission
2. If you clicked "No", delete `.setup_state` and try again
3. Make sure to approve the admin prompt

### Issue 4: Want to Reset Setup Process

**Steps**:
1. Close all command prompts
2. Delete the `.setup_state` file from the E-Book-Maker directory
3. Delete the `.setup_completed` file if it exists
4. Run `start.bat` again

## Manual Setup

If automatic setup doesn't work, you can configure PATH manually:

### Windows 10/11 Manual PATH Setup

1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", find and select "Path"
5. Click "Edit"
6. Click "New" and add these paths (if they exist):
   - `C:\Program Files\Pandoc`
   - `C:\Program Files\wkhtmltopdf\bin`
   - `C:\Program Files\MiKTeX\miktex\bin\x64`
7. Click "OK" on all dialogs
8. **Reboot your computer**
9. Run `start.bat`

## Verification Commands

To manually verify your setup, run these commands in a **new** command prompt:

```cmd
# Check Python
python --version

# Check Pandoc
pandoc --version

# Check wkhtmltopdf (optional)
wkhtmltopdf --version

# Check pdflatex (optional)
pdflatex --version
```

## When to Reboot

You **MUST** reboot after:
- Running the automatic PATH setup for the first time
- Manually changing PATH environment variables
- Installing new tools (pandoc, wkhtmltopdf, etc.)

You **DON'T** need to reboot if:
- You just closed and reopened your command prompt
- Tools were already in PATH and no changes were made

## Getting Help

If you're still having issues:

1. Run `check_install.py` to see detailed dependency status:
   ```cmd
   python check_install.py
   ```

2. Check the `.setup_state` file to see current state:
   ```cmd
   type .setup_state
   ```

3. Verify PATH manually:
   ```cmd
   echo %PATH%
   ```

4. Try the verification script:
   ```cmd
   cd "win files"
   VERIFY-SETUP.bat
   ```

## Quick Reset

If everything is stuck, try this:

```cmd
# Delete state files
del .setup_state
del .setup_completed

# Reboot computer
shutdown /r /t 0

# After reboot, run start.bat
start.bat
```
