@echo off
REM =====================================
REM Account Manager - Build Script
REM =====================================

echo.
echo =====================================
echo Building Account Manager Executable
echo =====================================
echo.

REM Step 1: Clean previous builds
echo [1/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AccountManager.spec del AccountManager.spec
echo       Done.
echo.

REM Step 2: Build executable
echo [2/4] Building executable with PyInstaller...
py -m PyInstaller --clean --onefile --windowed --name AccountManager main.py
echo       Done.
echo.

REM Step 3: Copy README to dist
echo [3/4] Copying documentation...
if exist dist (
    copy /Y "dist\README.txt" "dist\README.txt" >nul 2>&1 || (
        echo       README.txt not found in dist, skipping...
    )
)
echo       Done.
echo.

REM Step 4: Verify build
echo [4/4] Verifying build...
if exist dist\AccountManager.exe (
    echo.
    echo =====================================
    echo SUCCESS: Build Complete!
    echo =====================================
    echo.
    echo Executable: dist\AccountManager.exe
    dir dist\AccountManager.exe | find "AccountManager.exe"
    echo.
    echo You can now distribute the file:
    echo   F:\accounting\account_manager\dist\AccountManager.exe
    echo.
) else (
    echo.
    echo =====================================
    echo ERROR: Build Failed!
    echo =====================================
    echo.
    echo Please check the error messages above.
    echo.
    exit /b 1
)

echo Press any key to exit...
pause >nul
