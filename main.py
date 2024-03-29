import sys
import urllib.request
import subprocess
import os
import shutil

version = sys.argv[1]
pico_url = fr"https://github.com/raspberrypi/pico-setup-windows/releases/download/{version}/pico-setup-windows-x64-standalone.exe "


def copy_file_or_folder(source, destination):
    try:
        if os.path.isfile(source):
            shutil.copy2(source, destination)
            print(f"copy '{source}' to '{destination}'")
        elif os.path.isdir(source):
            shutil.copytree(source, destination)
            print(f"copy '{source}' to '{destination}'")
        else:
            print("Unknown file")
    except Exception as e:
        print(f"error: {e}")


def copy(source_folder, target_folder, file_name):
    source_path = os.path.join(source_folder, file_name)
    target_path = os.path.join(target_folder, file_name)

    try:
        copy_file_or_folder(source_path, target_path)
    except FileNotFoundError:
        print(f"file not found '{file_name}' in '{source_folder}'")
    except Exception as e:
        print(f"error: {e}")


def download_and_extract(url, extract_path):
    # 从URL中提取文件名
    file_name = os.path.basename(url)

    # 下载ZIP文件
    urllib.request.urlretrieve(url, file_name)

    # 解压ZIP文件
    subprocess.run(rf'7z x {file_name} -o{extract_path}', check=True)


# 只需要这些就能编译，别的没用
file_list = [
    "gcc-arm-none-eabi",
    "openocd",
    "pico-sdk-tools",
    "python",
    "git",
    "pico-examples.zip",
    "cmake",
    "ninja",
    "pico-env.cmd",
    "pico-sdk",
    "picotool"
]

build_dir = "temp"
toolchain_dir = f"pico-toolchain-{version}"

download_and_extract(pico_url, build_dir)
os.mkdir(toolchain_dir)
for file in file_list:
    copy(build_dir, toolchain_dir, file)

# 在每次打开bat时候，自动生成这个ini
fix_bat = fr'''@echo off
setlocal

set PICO_SDK_VERSION={version[1:]}
set PICO_INSTALL_PATH=%~dp0
set PICO_REG_KEY=Software\Raspberry Pi\Pico SDK v%PICO_SDK_VERSION%

if "%PICO_INSTALL_PATH:~-1%"=="\" (
    set "PICO_INSTALL_PATH=%PICO_INSTALL_PATH:~0,-1%"
)

:: generate version.ini
echo [pico-setup-windows]> %~dp0version.ini
echo PICO_SDK_VERSION=%PICO_SDK_VERSION%>> %~dp0version.ini
echo PICO_INSTALL_PATH=%PICO_INSTALL_PATH%>> %~dp0version.ini
echo PICO_REG_KEY=%PICO_REG_KEY%>> %~dp0version.ini

echo version.ini generated
endlocal

'''

with open(toolchain_dir + "/pico-env.cmd", "r") as f:
    original_content = f.read()
with open(toolchain_dir + "/pico-env.cmd", "w") as f:
    f.write(fix_bat + original_content)
