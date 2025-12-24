from pyrogram import Client
from datetime import datetime, timezone
import time
import os
import sys
import platform
import urllib.request
import zipfile
import shutil
import logging

# =================================
version = "1.0"
log_id = -1003669488656
token = ""
main_link_subs = "https://etoneya.a9fm.site/1"
test_link_subs = "https://etoneya.a9fm.site/test"
args = "--timeout 10 --threads 3 --t2kill 5"
sleep_time = 500
# =================================

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO
)


if platform.system() == "Windows":
    XRAY_PATH = os.path.join("bin", "xray.exe")
else:
    XRAY_PATH = os.path.join("bin", "xray")

os.makedirs("bin", exist_ok=True)

def get_arch():
    machine = platform.machine().lower()
    if machine in ("i386", "i686"):
        return "32"
    elif machine in ("x86_64", "amd64"):
        return "64"
    elif "armv5" in machine:
        return "arm32-v5"
    elif "armv6" in machine:
        return "arm32-v6"
    elif machine in ("armv7l", "armv7"):
        return "arm32-v7a"
    elif machine in ("aarch64", "arm64"):
        return "arm64-v8a"
    elif "riscv64" in machine:
        return "riscv64"
    elif "ppc64le" in machine:
        return "ppc64le"
    elif "ppc64" in machine:
        return "ppc64"
    elif "s390x" in machine:
        return "s390x"
    else:
        raise OSError(f"Unsupported architecture: {machine}")

def download_xray():
    arch = get_arch()
    url = f"https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-{arch}.zip"
    if platform.system() == "Windows":
        url = f"https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-{arch}.zip"

    logging.info(f"Downloading Xray for {arch} from {url}")
    try:
        zip_path = os.path.join("bin", "xray_temp.zip")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            binary_name = "xray.exe" if platform.system() == "Windows" else "xray"
            zf.extract(binary_name, "bin")
            os.chmod(os.path.join("bin", binary_name), 0o755)

        os.remove(zip_path)
        logging.info("Xray installed successfully.")
    except Exception as e:
        logging.error(f"Failed to download or extract Xray: {e}")
        raise RuntimeError("Xray installation failed") from e

if not os.path.isfile(XRAY_PATH):
    logging.warning("Xray binary not found. Downloading...")
    download_xray()

try:
    import subprocess
    result = subprocess.run([XRAY_PATH, "-version"], capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError("Xray binary is not working")
    logging.info(f"Xray version: {result.stdout.strip()}")
except Exception as e:
    logging.error(f"Xray verification failed: {e}")
    sys.exit(1)

while True:
    try:
        # MAIN
        if platform.system() == "Windows":
            python_var = "python"
        else:
            python_var = "python3"
        os.system(f"{python_var} v2rayChecker.py -u {main_link_subs} {args}")
        namefile = f"result_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        os.rename("sortedProxy.txt", namefile)

        app = Client("bot", api_id=2860432, api_hash="2fde6ca0f8ae7bb58844457a239c7214", bot_token=token)
        with app:
            app.send_document(log_id, document=namefile, caption=f"MAIN\nС аргументами: {args.replace('--', '-')}\nТеперь спать на {sleep_time}сек")
        os.remove(namefile)

        # TEST
        os.system(f"{python_var} v2rayChecker.py -u {test_link_subs} {args}")
        namefile = f"result_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        os.rename("sortedProxy.txt", namefile)

        app = Client("bot", api_id=2860432, api_hash="2fde6ca0f8ae7bb58844457a239c7214", bot_token=token)
        with app:
            app.send_document(log_id, document=namefile, caption=f"TEST\nС аргументами: {args.replace('--', '-')}\nТеперь спать на {sleep_time}сек")
        os.remove(namefile)

        logging.info(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)

    except Exception as e:
        logging.exception("Unexpected error in main loop")
        time.sleep(60)  # пауза перед повтором
