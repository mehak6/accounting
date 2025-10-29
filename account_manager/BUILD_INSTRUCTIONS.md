# Build Instructions - Account Manager Executable

## Overview
This document explains how to build the Account Manager executable from source code.

## Prerequisites

1. **Python 3.13.7** (or Python 3.8+)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Required Python Packages**
   ```bash
   pip install customtkinter
   pip install pyinstaller
   ```

## Quick Build

### Option 1: One-Line Build (Recommended)
```bash
cd F:/accounting/account_manager
py -m PyInstaller --clean --onefile --windowed --name AccountManager main.py
```

### Option 2: Using Spec File
```bash
cd F:/accounting/account_manager
py -m PyInstaller --clean account_manager.spec
```

## Build Output

After successful build:
- **Executable Location**: `dist/AccountManager.exe`
- **Size**: ~13 MB
- **Type**: Standalone Windows executable
- **Dependencies**: None (all included)

## Build Options Explained

### PyInstaller Flags Used

- `--clean`: Remove cache and temporary files before building
- `--onefile`: Bundle everything into a single .exe file
- `--windowed`: No console window (GUI only)
- `--name AccountManager`: Name of the output executable

### Additional Options (Optional)

#### Add an Icon
```bash
py -m PyInstaller --clean --onefile --windowed --name AccountManager --icon=icon.ico main.py
```

#### With Console (for debugging)
```bash
py -m PyInstaller --clean --onefile --console --name AccountManager main.py
```

#### Without UPX Compression (faster build, larger file)
```bash
py -m PyInstaller --clean --onefile --windowed --name AccountManager --noupx main.py
```

## Build Process Steps

1. **Preparation**
   ```bash
   cd F:/accounting/account_manager
   ```

2. **Clean Previous Builds** (Optional)
   ```bash
   rmdir /s /q build
   rmdir /s /q dist
   del *.spec
   ```

3. **Run PyInstaller**
   ```bash
   py -m PyInstaller --clean --onefile --windowed --name AccountManager main.py
   ```

4. **Verify Build**
   ```bash
   ls -lh dist/
   # Should show AccountManager.exe (~13 MB)
   ```

5. **Test Executable**
   ```bash
   cd dist
   ./AccountManager.exe
   ```

## Build Artifacts

After building, you'll find:

```
account_manager/
├── build/                  # Temporary build files (can be deleted)
├── dist/                   # Output folder
│   └── AccountManager.exe  # Final executable (13 MB)
├── AccountManager.spec     # PyInstaller spec file (auto-generated)
└── main.py                 # Source code
```

## Distribution Package

To create a distribution package:

1. **Create Distribution Folder**
   ```bash
   mkdir AccountManager_v1.0.0
   cd AccountManager_v1.0.0
   ```

2. **Copy Files**
   ```bash
   copy ..\dist\AccountManager.exe .
   copy ..\dist\README.txt .
   ```

3. **Create ZIP** (Optional)
   - Right-click on the folder
   - Send to > Compressed (zipped) folder
   - Or use: `tar -a -c -f AccountManager_v1.0.0.zip AccountManager_v1.0.0`

## File Size Optimization

Current build: ~13 MB

### To Reduce Size:

1. **Use UPX Compression** (default in our build)
   - Already enabled with `upx=True` in spec file
   - Reduces size by ~30-40%

2. **Exclude Unused Modules**
   Edit `account_manager.spec`:
   ```python
   excludes=['matplotlib', 'numpy', 'pandas']
   ```

3. **Remove Debug Symbols**
   ```bash
   py -m PyInstaller --clean --onefile --windowed --strip main.py
   ```

### Current Size Breakdown:
- Python runtime: ~5 MB
- CustomTkinter + dependencies: ~3 MB
- Tkinter/Tcl/Tk: ~4 MB
- Application code: ~1 MB

## Testing the Build

### Manual Testing Checklist

1. **Launch Test**
   - [ ] Executable launches without errors
   - [ ] Main window appears
   - [ ] No console window appears (windowed mode)

2. **Database Test**
   - [ ] Creates data folder on first run
   - [ ] Creates financial_data.db file
   - [ ] Can add companies
   - [ ] Can add users
   - [ ] Can create transactions

3. **Feature Test**
   - [ ] Company management works
   - [ ] User management works
   - [ ] Transaction entry works
   - [ ] Reports display correctly
   - [ ] CSV export works
   - [ ] Theme toggle works

4. **Performance Test**
   - [ ] Starts in < 5 seconds
   - [ ] UI is responsive
   - [ ] Database operations are fast

## Troubleshooting Build Issues

### Issue: "Module not found" errors
**Solution**: Install missing packages
```bash
pip install customtkinter darkdetect
```

### Issue: Build fails with import errors
**Solution**: Add to hiddenimports in spec file
```python
hiddenimports=['missing_module_name']
```

### Issue: Large file size
**Solution**: Enable UPX compression
```python
upx=True  # In spec file
```

### Issue: Slow startup
**Solution**: Use --onedir instead of --onefile
```bash
py -m PyInstaller --onedir --windowed main.py
```

### Issue: Windows Defender blocks executable
**Solution**: This is normal for new .exe files
- Go to Windows Security > Virus & threat protection
- Click "Allowed threats"
- Allow the file

## Advanced: Custom Spec File

The generated `account_manager.spec` can be customized:

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Add data files here if needed
        # ('data_folder', 'data_folder'),
    ],
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'sqlite3',
    ],
    excludes=[
        # Exclude unused modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
    ],
)

exe = EXE(
    # ... configuration ...
    name='AccountManager',
    icon='icon.ico',  # Add your icon
    version_file='version.txt',  # Add version info
)
```

## Version Information File

Create `version.txt` for Windows version info:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    OS=0x40004,
    fileType=0x1,
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'Account Manager'),
          StringStruct('FileDescription', 'Financial Transaction Manager'),
          StringStruct('FileVersion', '1.0.0'),
          StringStruct('ProductName', 'Account Manager'),
          StringStruct('ProductVersion', '1.0.0'),
        ])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
```

## Automated Build Script

Create `build.bat` for automated builds:

```batch
@echo off
echo =====================================
echo Building Account Manager Executable
echo =====================================
echo.

echo Step 1: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
echo Done.
echo.

echo Step 2: Building executable...
py -m PyInstaller --clean --onefile --windowed --name AccountManager main.py
echo Done.
echo.

echo Step 3: Verifying build...
if exist dist\AccountManager.exe (
    echo SUCCESS: Executable created successfully!
    echo Location: dist\AccountManager.exe
    dir dist\AccountManager.exe
) else (
    echo ERROR: Build failed!
    exit /b 1
)
echo.

echo =====================================
echo Build Complete!
echo =====================================
pause
```

## Build Performance

- **Build Time**: 10-20 seconds
- **Output Size**: ~13 MB
- **Startup Time**: 2-3 seconds
- **Memory Usage**: ~50-100 MB

## Distribution Checklist

Before distributing:

- [ ] Test executable on clean Windows system
- [ ] Include README.txt in dist folder
- [ ] Verify all features work
- [ ] Test on different Windows versions if possible
- [ ] Create installation instructions
- [ ] Consider creating installer (optional)

## Creating an Installer (Optional)

Use Inno Setup to create a professional installer:

1. Download Inno Setup: https://jrsoftware.org/isdl.php
2. Create installer script
3. Build installer .exe

## Support

For build issues:
1. Check PyInstaller documentation
2. Verify all dependencies are installed
3. Try building with console mode first for debugging
4. Check the build log in `build/AccountManager/warn-*.txt`

---

**Last Updated**: October 2025
**Build System**: PyInstaller 6.15.0
**Target Platform**: Windows 10/11 (64-bit)
