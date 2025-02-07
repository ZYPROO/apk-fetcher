from google_play_scraper import app
import mysql.connector
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def read_package_names(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

# Connect to MySQL database using Railway credentials
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

# Create the 'apps' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    package_name VARCHAR(255) UNIQUE,
    version VARCHAR(50),
    icon_url TEXT,
    screenshot_url TEXT
)
""")
db.commit()

app_packages = read_package_names("packages.txt")

# Function to fetch and store app data
def fetch_and_store():
    for package in app_packages:
        try:
            data = app(package)
            name = data['title']
            version = data['version']
            icon_url = data['icon']
            screenshot_url = ','.join(data['screenshots'][:3])  # Store up to 3 screenshots

            # Insert or update app data in the database
            sql = """
            INSERT INTO apps (name, package_name, version, icon_url, screenshot_url)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                version=%s, icon_url=%s, screenshot_url=%s
            """
            values = (name, package, version, icon_url, screenshot_url, version, icon_url, screenshot_url)

            cursor.execute(sql, values)
            db.commit()

            print(f"✅ Fetched and stored: {name} (Version: {version})")
            time.sleep(2)  # Add delay to avoid rate-limiting

        except Exception as e:
            print(f"❌ Error fetching {package}: {e}")

# Run the function
fetch_and_store()

# Close the database connection
cursor.close()
db.close()