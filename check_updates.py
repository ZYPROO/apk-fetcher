import os
import json
import requests
from google_play_scraper import app
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Discord webhook URL from .env
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def read_package_names(file_path="packages.txt"):
    """Reads package names from packages.txt file."""
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: {file_path} not found!")
        return []

def get_app_version(package_name):
    """Fetches the latest version of the app from the Play Store."""
    try:
        result = app(package_name)
        return result["version"]
    except Exception as e:
        print(f"Error fetching {package_name}: {e}")
        return None

def send_discord_notification(package_name, version):
    """Sends a notification to Discord when an app updates."""
    if not WEBHOOK_URL:
        print("Error: Discord Webhook URL not found!")
        return

    message = f"🔔 **{package_name}** has been updated to version **{version}**! 🚀"
    data = {"content": message}

    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"✅ Notification sent for {package_name}!")
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

def check_for_updates():
    """Checks for app updates and notifies Discord if a new version is found."""
    package_names = read_package_names()

    # Load stored versions or create a new file if missing
    try:
        with open("versions.json", "r") as file:
            stored_versions = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        stored_versions = {}

    for package_name in package_names:
        new_version = get_app_version(package_name)

        if new_version and (package_name not in stored_versions or stored_versions[package_name] != new_version):
            send_discord_notification(package_name, new_version)
            stored_versions[package_name] = new_version  # Update stored version

    # Save updated versions back to versions.json
    with open("versions.json", "w") as file:
        json.dump(stored_versions, file, indent=4)

if __name__ == "__main__":
    check_for_updates()
