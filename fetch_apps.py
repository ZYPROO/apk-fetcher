from google_play_scraper import app
import psycopg2
import time
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Setup logging for errors
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Read package names from a file
def read_package_names(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT")
    )

# Fetch delay (default 2 seconds, can be adjusted via .env)
FETCH_DELAY = int(os.getenv("FETCH_DELAY", 2))

# Read package names from packages.txt
app_packages = read_package_names("packages.txt")

# Function to fetch and store app data
def fetch_and_store():
    db = get_db_connection()
    cursor = db.cursor()

    for index, package in enumerate(app_packages):
        try:
            # Fetch app data from Google Play
            data = app(package)
            name = data['title']
            version = data['version']
            icon_url = data['icon']
            screenshot_url = ','.join(data['screenshots'][:3])  # Store up to 3 screenshots

            # Insert or update app data in PostgreSQL
            sql = """
                INSERT INTO apps (name, package_name, version, icon_url, screenshot_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (package_name)
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    version = EXCLUDED.version, 
                    icon_url = EXCLUDED.icon_url, 
                    screenshot_url = EXCLUDED.screenshot_url
            """
            values = (name, package, version, icon_url, screenshot_url)
            cursor.execute(sql, values)

            # Commit every 5 records for efficiency
            if index % 5 == 0:
                db.commit()

            print(f"✅ Fetched and stored: {name} (Version: {version})")

            # Delay to prevent rate-limiting
            time.sleep(FETCH_DELAY)

        except Exception as e:
            error_message = f"❌ Error fetching {package}: {e}"
            print(error_message)
            logging.error(error_message)

    # Final commit to ensure all data is saved
    db.commit()

    # Close database connection
    cursor.close()
    db.close()

# Run the function
if __name__ == "__main__":
    fetch_and_store()