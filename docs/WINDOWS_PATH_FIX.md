# Windows PATH Detection Fix

## Problem Summary

The E-Book Maker web interface was incorrectly showing `wkhtmltopdf` and `pdflatex` as "Not Found" on Windows, even though:
- The tools were properly installed
- They were in the Windows PATH
- They worked correctly from Command Prompt
- `pandoc` was being detected correctly

## Root Cause

When running Python in a virtual environment (venv) on Windows, the `PATH` environment variable can be **truncated** to approximately 200-300 characters. This truncation causes Python's `shutil.which()` function to fail to find executables that are located in PATH directories beyond the truncation point.

**Evidence from debug output:**
```
[DEBUG] PATH: C:\Users\...\venv\Scripts;C:\WINDOWS\system32;...OpenSS...
```
Notice the `...` at the end - the PATH was cut off at ~200 characters.

## Solution

Instead of relying on the environment's PATH variable, the code now reads the **full system PATH directly from the Windows Registry** on Windows systems.

### Implementation

The fix is implemented in two files:

#### 1. `server.py` - `/api/check-dependencies` endpoint

```python
# On Windows, get the full system PATH from the registry
full_path = os.environ.get('PATH', '')
if platform.system() == 'Windows':
    try:
        import winreg
        # Get system PATH from HKEY_LOCAL_MACHINE
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
            system_path = winreg.QueryValueEx(key, 'Path')[0]

        # Get user PATH from HKEY_CURRENT_USER
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
                user_path = winreg.QueryValueEx(key, 'Path')[0]
        except:
            user_path = ''

        # Combine venv + system + user paths
        venv_scripts = os.path.join(sys.prefix, 'Scripts')
        full_path = f"{venv_scripts};{system_path};{user_path}"
    except Exception as e:
        pass  # Fall back to environment PATH
```

Then use this `full_path` when checking for commands:
```python
which_result = shutil.which(cmd, path=full_path)
```

#### 2. `check_install.py` - Dependency checker script

Similar implementation for consistency.

## Results

**Before fix:**
```
PATH length: ~200 characters (truncated)
pandoc: ✓ Found (early in PATH)
wkhtmltopdf: ✗ Not found (beyond truncation)
pdflatex: ✗ Not found (beyond truncation)
```

**After fix:**
```
PATH length: 2197 characters (full)
pandoc: ✓ Found at C:\Program Files\Pandoc\pandoc.EXE
wkhtmltopdf: ✓ Found at C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.EXE
pdflatex: ✓ Found at C:\Users\...\MiKTeX\miktex\bin\x64\pdflatex.EXE
```

## Why This Happens

1. **Windows PATH Limitation**: Windows has historically had limitations on environment variable lengths
2. **Virtual Environment**: Python venvs prepend their Scripts directory to PATH
3. **Variable Expansion**: Some processes truncate expanded PATH variables
4. **Python Behavior**: Python's `os.environ['PATH']` reflects the truncated value

## Alternative Approaches Considered

1. ❌ **Refreshing PATH from CMD**: Doesn't work because venv is already running
2. ❌ **Using WHERE command**: Still uses truncated PATH
3. ❌ **Running subprocess.run() without shutil.which**: FileNotFoundError when not in truncated PATH
4. ✅ **Reading from Registry**: Always gets the full, authoritative PATH values

## Platform Compatibility

- **Windows**: Uses registry-based PATH detection
- **Linux/macOS**: Falls back to standard `os.environ['PATH']` (no truncation issues on these platforms)

## Testing

To verify the fix works:

```bash
# Run dependency check
python check_install.py

# Start server and check web interface
python server.py
# Navigate to http://127.0.0.1:5000
# All tools should show as "✓ Installed"
```

## Related Issues

This fix also resolves potential issues with:
- Tool detection in `start.bat` setup script
- Any other Python scripts that need to find system executables
- Tools installed in non-standard locations that are in the system PATH

## References

- Windows Registry PATH locations:
  - System: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment`
  - User: `HKEY_CURRENT_USER\Environment`
- Python `winreg` module: https://docs.python.org/3/library/winreg.html
- Windows PATH length limitations: https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation
