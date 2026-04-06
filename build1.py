#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from pathlib import Path

# 定义颜色类
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_RED = '\033[1;31m'

# 确保Windows终端支持ANSI颜色
def enable_windows_ansi_support():
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

# 打印带颜色的文本
def print_color(text, color=Colors.RESET):
    print(f"{color}{text}{Colors.RESET}")

# 运行命令并返回结果
def run_command(cmd, cwd=None, shell=True, check=False):
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=shell, check=check, 
                              capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        return e

# 构建Windows EXE
def build_exe():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building Windows EXE", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Checking PyInstaller...", Colors.CYAN)
    result = run_command("pip show pyinstaller", check=False)
    if result.returncode != 0:
        print_color("PyInstaller not found, installing...", Colors.YELLOW)
        result = run_command("pip install pyinstaller", check=True)
        if result.returncode != 0:
            print_color("Failed to install PyInstaller", Colors.BOLD_RED)
            input("Press Enter to continue...")
            return False

    print_color("Building scl.py...", Colors.CYAN)
    result = run_command(
        "pyinstaller --onefile --name scl --distpath dist\\exe --workpath build\\exe --specpath build\\exe scl.py",
        check=True
    )
    if result.returncode != 0:
        print_color("Failed to build scl.py", Colors.BOLD_RED)
        input("Press Enter to continue...")
        return False

    print()
    print_color("EXE build completed!", Colors.BOLD_GREEN)
    print_color("Output directory: dist\\exe", Colors.GREEN)
    print()

    print_color("Copying plugins directory...", Colors.CYAN)
    os.makedirs("dist\\exe\\plugins", exist_ok=True)
    result = run_command("xcopy /E /I /Y plugins dist\\exe\\plugins", check=False)
    print()
    input("Press Enter to continue...")
    return True

# 构建Windows EXE - 愚人节版本
def build_exe_april_fools():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building Windows EXE - April Fools Edition", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Checking PyInstaller...", Colors.CYAN)
    result = run_command("pip show pyinstaller", check=False)
    if result.returncode != 0:
        print_color("PyInstaller not found, installing...", Colors.YELLOW)
        result = run_command("pip install pyinstaller", check=True)
        if result.returncode != 0:
            print_color("Failed to install PyInstaller", Colors.BOLD_RED)
            input("Press Enter to continue...")
            return False

    if not os.path.exists("sdp_yrj.py"):
        print_color("Error: sdp_yrj.py not found", Colors.BOLD_RED)
        input("Press Enter to continue...")
        return False

    print_color("Building sdp_yrj.py...", Colors.CYAN)
    result = run_command(
        "pyinstaller --onefile --name sdp_yrj --distpath dist\\exe --workpath build\\exe --specpath build\\exe sdp_yrj.py",
        check=False
    )
    if result.returncode != 0:
        print_color("Failed to build sdp_yrj.py", Colors.BOLD_RED)
    else:
        print_color("Successfully built sdp_yrj.exe", Colors.BOLD_GREEN)

    print()
    print_color("April Fools EXE build completed!", Colors.BOLD_GREEN)
    print_color("Output directory: dist\\exe", Colors.GREEN)
    print()

    print_color("Copying plugins directory...", Colors.CYAN)
    os.makedirs("dist\\exe\\plugins", exist_ok=True)
    result = run_command("xcopy /E /I /Y plugins dist\\exe\\plugins", check=False)
    print()
    input("Press Enter to continue...")
    return True

# 构建Linux DEB - SCL Full Package (via WSL)
def build_deb():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building Linux DEB via WSL", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Checking WSL...", Colors.CYAN)
    result = run_command("wsl echo 'WSL OK'", check=False)
    if result.returncode != 0:
        print_color("WSL is not installed or not available", Colors.BOLD_RED)
        print_color("Please install WSL first:", Colors.YELLOW)
        print_color("  wsl --install", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print_color("WSL found. Preparing build environment...", Colors.GREEN)

    # 获取当前目录的WSL路径
    result = run_command("wsl wslpath '%cd%'", check=True)
    wsl_path = result.stdout.strip()
    print_color(f"WSL path: {wsl_path}", Colors.BLUE)

    print_color("Creating dist directory...", Colors.CYAN)
    os.makedirs("dist", exist_ok=True)

    print_color("Copying build script to WSL...", Colors.CYAN)
    result = run_command(f"wsl cp '{wsl_path}/build_deb_wsl.sh' /tmp/build_deb_wsl.sh", check=True)
    result = run_command("wsl chmod +x /tmp/build_deb_wsl.sh", check=True)

    print_color("Building DEB package in WSL...", Colors.CYAN)
    result = run_command(f"wsl /tmp/build_deb_wsl.sh '{wsl_path}'", check=True)
    if result.returncode != 0:
        print()
        print_color("Failed to build DEB package", Colors.BOLD_RED)
        print_color("Make sure dpkg-deb is available in WSL", Colors.YELLOW)
        print_color("Run: wsl sudo apt update ^&^& wsl sudo apt install dpkg-dev", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print()
    print_color("DEB build completed!", Colors.BOLD_GREEN)
    print_color("Output file: dist\\scl-1.0.0.deb", Colors.GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 构建Linux DEB - SDP Only (via WSL)
def build_sdp_deb():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building Linux DEB - SDP Only (via WSL)", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Checking WSL...", Colors.CYAN)
    result = run_command("wsl echo 'WSL OK'", check=False)
    if result.returncode != 0:
        print_color("WSL is not installed or not available", Colors.BOLD_RED)
        print_color("Please install WSL first:", Colors.YELLOW)
        print_color("  wsl --install", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print_color("WSL found. Preparing build environment...", Colors.GREEN)

    # 获取当前目录的WSL路径
    result = run_command("wsl wslpath '%cd%'", check=True)
    wsl_path = result.stdout.strip()
    print_color(f"WSL path: {wsl_path}", Colors.BLUE)

    print_color("Creating dist directory...", Colors.CYAN)
    os.makedirs("dist", exist_ok=True)

    print_color("Copying build script to WSL...", Colors.CYAN)
    result = run_command(f"wsl cp '{wsl_path}/build_sdp_deb.sh' /tmp/build_sdp_deb.sh", check=True)

    print_color("Building SDP DEB package in WSL...", Colors.CYAN)
    result = run_command(f"wsl /tmp/build_sdp_deb.sh '{wsl_path}'", check=True)
    if result.returncode != 0:
        print()
        print_color("Failed to build SDP DEB package", Colors.BOLD_RED)
        print_color("Make sure dpkg-deb is available in WSL", Colors.YELLOW)
        print_color("Run: wsl sudo apt update ^&^& wsl sudo apt install dpkg-dev", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print()
    print_color("SDP DEB build completed!", Colors.BOLD_GREEN)
    print_color("Output file: dist\\scl-sdp-1.0.0.deb", Colors.GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 构建Linux DEB - SDP April Fools Edition (via WSL)
def build_sdp_deb_april_fools():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building Linux DEB - SDP April Fools Edition (via WSL)", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    if not os.path.exists("sdp_yrj.py"):
        print_color("Error: sdp_yrj.py not found", Colors.BOLD_RED)
        input("Press Enter to continue...")
        return False

    print_color("Checking WSL...", Colors.CYAN)
    result = run_command("wsl echo 'WSL OK'", check=False)
    if result.returncode != 0:
        print_color("WSL is not installed or not available", Colors.BOLD_RED)
        print_color("Please install WSL first:", Colors.YELLOW)
        print_color("  wsl --install", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print_color("WSL found. Preparing build environment...", Colors.GREEN)

    # 获取当前目录的WSL路径
    result = run_command("wsl wslpath '%cd%'", check=True)
    wsl_path = result.stdout.strip()
    print_color(f"WSL path: {wsl_path}", Colors.BLUE)

    print_color("Creating dist directory...", Colors.CYAN)
    os.makedirs("dist", exist_ok=True)

    # 创建愚人节版本的构建脚本
    print_color("Creating April Fools build script...", Colors.CYAN)
    sdp_yrj_deb_script = '''#!/bin/bash
set -e

WSL_PATH="$1"
VERSION="1.0.0"

cd "$WSL_PATH"

# 创建临时目录
mkdir -p deb_temp/usr/local/bin
mkdir -p deb_temp/DEBIAN

# 复制sdp_yrj.py
echo "Copying sdp_yrj.py..."
cp sdp_yrj.py deb_temp/usr/local/bin/sdp_yrj
chmod +x deb_temp/usr/local/bin/sdp_yrj

# 复制插件目录
echo "Copying plugins directory..."
mkdir -p deb_temp/usr/local/lib/scl/plugins
cp -r plugins/* deb_temp/usr/local/lib/scl/plugins/

# 创建DEBIAN控制文件
echo "Creating DEBIAN control file..."
cat > deb_temp/DEBIAN/control << 'EOF'
Package: scl-sdp-yrj
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Depends: python3
Maintainer: SCL Team
Description: SCL Package Manager - April Fools Edition
EOF

# 构建DEB包
echo "Building DEB package..."
dpkg-deb --build deb_temp "$WSL_PATH/dist/scl-sdp-yrj-1.0.0.deb"

# 清理
echo "Cleaning up..."
rm -rf deb_temp

echo "SDP April Fools DEB build completed!"
echo "Output: $WSL_PATH/dist/scl-sdp-yrj-1.0.0.deb"
'''

    # 写入构建脚本
    with open("build_sdp_yrj_deb.sh", "w") as f:
        f.write(sdp_yrj_deb_script)
    
    # 为脚本添加执行权限
    os.chmod("build_sdp_yrj_deb.sh", 0o755)

    print_color("Copying build script to WSL...", Colors.CYAN)
    result = run_command(f"wsl cp '{wsl_path}/build_sdp_yrj_deb.sh' /tmp/build_sdp_yrj_deb.sh", check=True)
    result = run_command("wsl chmod +x /tmp/build_sdp_yrj_deb.sh", check=True)

    print_color("Building SDP April Fools DEB package in WSL...", Colors.CYAN)
    result = run_command(f"wsl /tmp/build_sdp_yrj_deb.sh '{wsl_path}'", check=True)
    if result.returncode != 0:
        print()
        print_color("Failed to build SDP April Fools DEB package", Colors.BOLD_RED)
        print_color("Make sure dpkg-deb is available in WSL", Colors.YELLOW)
        print_color("Run: wsl sudo apt update ^&^& wsl sudo apt install dpkg-dev", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print()
    print_color("SDP April Fools DEB build completed!", Colors.BOLD_GREEN)
    print_color("Output file: dist\\scl-sdp-yrj-1.0.0.deb", Colors.GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 构建Linux DEB - Editor Only (via WSL)
def build_editor_deb():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building Linux DEB - Editor Only (via WSL)", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Checking WSL...", Colors.CYAN)
    result = run_command("wsl echo 'WSL OK'", check=False)
    if result.returncode != 0:
        print_color("WSL is not installed or not available", Colors.BOLD_RED)
        print_color("Please install WSL first:", Colors.YELLOW)
        print_color("  wsl --install", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print_color("WSL found. Preparing build environment...", Colors.GREEN)

    # 获取当前目录的WSL路径
    result = run_command("wsl wslpath '%cd%'", check=True)
    wsl_path = result.stdout.strip()
    print_color(f"WSL path: {wsl_path}", Colors.BLUE)

    print_color("Creating dist directory...", Colors.CYAN)
    os.makedirs("dist", exist_ok=True)

    print_color("Copying build script to WSL...", Colors.CYAN)
    result = run_command(f"wsl cp '{wsl_path}/build_editor_deb.sh' /tmp/build_editor_deb.sh", check=True)

    print_color("Building Editor DEB package in WSL...", Colors.CYAN)
    result = run_command(f"wsl /tmp/build_editor_deb.sh '{wsl_path}'", check=True)
    if result.returncode != 0:
        print()
        print_color("Failed to build Editor DEB package", Colors.BOLD_RED)
        print_color("Make sure dpkg-deb is available in WSL", Colors.YELLOW)
        print_color("Run: wsl sudo apt update ^&^& wsl sudo apt install dpkg-dev", Colors.GREEN)
        input("Press Enter to continue...")
        return False

    print()
    print_color("Editor DEB build completed!", Colors.BOLD_GREEN)
    print_color("Output file: dist\\scl-editor-1.0.0.deb", Colors.GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 生成macOS Build Script (Mach-O)
def generate_macos_script():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Generating macOS Build Script", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Creating macOS build script...", Colors.CYAN)
    script_content = '''#!/bin/bash
set -e

echo "Building SCL for macOS (Mach-O)..."

VERSION="1.0.0"
BUILD_DIR="build/macos"
DIST_DIR="dist/macos"

echo "Checking PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller found"
else
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

echo "Creating build directories..."
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

echo "Building scl..."
pyinstaller --onefile --name scl --distpath "$DIST_DIR" --workpath "$BUILD_DIR" --specpath "$BUILD_DIR" scl.py

echo "Building sdp..."
pyinstaller --onefile --name sdp --distpath "$DIST_DIR" --workpath "$BUILD_DIR" --specpath "$BUILD_DIR" sdp.py

echo "Building scl_editor_linux..."
pyinstaller --onefile --name scl_editor --distpath "$DIST_DIR" --workpath "$BUILD_DIR" --specpath "$BUILD_DIR" scl_editor_linux.py

echo "Creating DMG package..."
mkdir -p "$DIST_DIR/SCL.app/Contents/MacOS"
mkdir -p "$DIST_DIR/SCL.app/Contents/Resources"

echo "Copying executables..."
cp "$DIST_DIR/scl" "$DIST_DIR/SCL.app/Contents/MacOS/"
cp "$DIST_DIR/sdp" "$DIST_DIR/SCL.app/Contents/MacOS/"
cp "$DIST_DIR/scl_editor" "$DIST_DIR/SCL.app/Contents/MacOS/"

echo "Creating Info.plist..."
cat < "$DIST_DIR/SCL.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>scl</string>
    <key>CFBundleIdentifier</key>
    <string>com.scl.lang</string>
    <key>CFBundleName</key>
    <string>SCL</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
</dict>
</plist>
EOF

echo "Building DMG..."
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "SCL" -srcfolder "$DIST_DIR/SCL.app" -ov -format UDZO "$DIST_DIR/SCL-$VERSION.dmg"
    echo "DMG created: $DIST_DIR/SCL-$VERSION.dmg"
else
    echo "hdiutil not found, skipping DMG creation"
    echo "App bundle created: $DIST_DIR/SCL.app"
fi

echo "Build completed!"
echo "Output: $DIST_DIR/"
'''

    with open("build_macos.sh", "w") as f:
        f.write(script_content)

    # 为脚本添加执行权限
    os.chmod("build_macos.sh", 0o755)

    print()
    print_color("macOS build script created: build_macos.sh", Colors.BOLD_GREEN)
    print()
    print_color("Instructions:", Colors.BOLD_YELLOW)
    print_color("1. Copy build_macos.sh to a macOS system", Colors.GREEN)
    print_color("2. Make it executable: chmod +x build_macos.sh", Colors.GREEN)
    print_color("3. Run it: ./build_macos.sh", Colors.GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 生成SDP macOS Build Script
def generate_sdp_macos_script():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Generating SDP macOS Build Script", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Creating SDP macOS build script...", Colors.CYAN)
    script_content = '''#!/bin/bash
set -e

echo "Building SDP for macOS (Mach-O)..."

VERSION="1.0.0"
BUILD_DIR="build/sdp-macos"
DIST_DIR="dist/sdp-macos"

echo "Checking PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
else
    echo "PyInstaller found"
fi

echo "Creating build directories..."
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR"

echo "Building SDP..."
pyinstaller --onefile --name sdp --distpath "$DIST_DIR" --workpath "$BUILD_DIR" --specpath "$BUILD_DIR" sdp.py

echo "Creating SDP App Bundle..."
APP_DIR="$DIST_DIR/SDP.app"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

echo "Copying executable..."
cp "$DIST_DIR/sdp" "$APP_DIR/Contents/MacOS/"

echo "Creating Info.plist..."
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>sdp</string>
    <key>CFBundleIdentifier</key>
    <string>com.scl.sdp</string>
    <key>CFBundleName</key>
    <string>SDP</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
</dict>
</plist>
EOF

echo "Building SDP DMG..."
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "SDP" -srcfolder "$APP_DIR" -ov -format UDZO "$DIST_DIR/SDP-$VERSION.dmg"
    echo "DMG created: $DIST_DIR/SDP-$VERSION.dmg"
else
    echo "hdiutil not found, skipping DMG creation"
    echo "App bundle created: $APP_DIR"
fi

echo "SDP build completed!"
echo "Output: $DIST_DIR/"
'''

    with open("build_sdp_macos.sh", "w") as f:
        f.write(script_content)

    # 为脚本添加执行权限
    os.chmod("build_sdp_macos.sh", 0o755)

    print()
    print_color("SDP macOS build script created: build_sdp_macos.sh", Colors.BOLD_GREEN)
    print()
    print_color("Instructions:", Colors.BOLD_YELLOW)
    print_color("1. Copy build_sdp_macos.sh to a macOS system", Colors.GREEN)
    print_color("2. Make it executable: chmod +x build_sdp_macos.sh", Colors.GREEN)
    print_color("3. Run it: ./build_sdp_macos.sh", Colors.GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 构建所有 (EXE + DEB)
def build_all():
    print_color("\n========================================", Colors.BOLD_CYAN)
    print_color("Building All Packages (EXE + DEB)", Colors.BOLD_YELLOW)
    print_color("========================================", Colors.BOLD_CYAN)
    print()

    print_color("Starting Windows EXE build...", Colors.CYAN)
    print()
    if not build_exe():
        return False

    print_color("Starting Linux DEB build...", Colors.CYAN)
    print()
    if not build_deb():
        return False

    print()
    print_color("All builds completed!", Colors.BOLD_GREEN)
    print()
    input("Press Enter to continue...")
    return True

# 显示菜单
def show_menu():
    while True:
        print_color("========================================", Colors.BOLD_CYAN)
        print_color("SCL Build Tool", Colors.BOLD_YELLOW)
        print_color("========================================", Colors.BOLD_CYAN)
        print()

        print_color("Please select build type:", Colors.BOLD_YELLOW)
        print_color("[1] Build Windows EXE", Colors.GREEN)
        print_color("[2] Build Linux DEB - SCL Full Package (via WSL)", Colors.GREEN)
        print_color("[3] Build Linux DEB - SDP Only (via WSL)", Colors.GREEN)
        print_color("[4] Build Linux DEB - Editor Only (via WSL)", Colors.GREEN)
        print_color("[5] Generate macOS Build Script (Mach-O)", Colors.GREEN)
        print_color("[6] Generate SDP macOS Build Script", Colors.GREEN)
        print_color("[7] Build All (EXE + DEB)", Colors.GREEN)
        print_color("[8] Build Windows EXE - April Fools Edition", Colors.GREEN)
        print_color("[9] Build Linux DEB - SDP April Fools Edition (via WSL)", Colors.GREEN)
        print_color("[10] Exit", Colors.GREEN)
        print()

        try:
            choice = input(f"{Colors.BOLD_CYAN}Enter option (1-10):{Colors.RESET} ")
            print()
            
            if choice == "1":
                build_exe()
            elif choice == "2":
                build_deb()
            elif choice == "3":
                build_sdp_deb()
            elif choice == "4":
                build_editor_deb()
            elif choice == "5":
                generate_macos_script()
            elif choice == "6":
                generate_sdp_macos_script()
            elif choice == "7":
                build_all()
            elif choice == "8":
                build_exe_april_fools()
            elif choice == "9":
                build_sdp_deb_april_fools()
            elif choice == "10":
                break
            else:
                print_color("Invalid option, please try again", Colors.BOLD_RED)
                print()
        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print_color(f"An error occurred: {e}", Colors.BOLD_RED)
            print()

    print_color("\nThank you for using SCL Build Tool!", Colors.BOLD_YELLOW)
    print()
    input("Press Enter to exit...")

# 主函数
if __name__ == "__main__":
    enable_windows_ansi_support()
    show_menu()