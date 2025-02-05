from google_play_scraper import app
import mysql.connector
import time
from dotenv import load_dotenv
import os

load_dotenv()

def read_package_names(file_path):
    with open(file_path,"r") as f:
        return [line.strip() for line in f.readlines()]
    
db_password = os.getenv("DB_PASSWORD")

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Change this if you have a different username
    password=db_password,  # Change this to your MySQL password
    database="apk_database"
)

cursor = db.cursor()

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

            # Insert data into MySQL table
            sql = "INSERT INTO apps (name, package_name, version, icon_url, screenshot_url) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE version=%s, icon_url=%s, screenshot_url=%s"
            values = (name, package, version, icon_url, screenshot_url, version, icon_url, screenshot_url)

            cursor.execute(sql, values)
            db.commit()

            print(f"✅ Fetched and stored: {name} (Version: {version})")

            # Add a short delay to prevent getting blocked
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error fetching {package}: {e}")

# Run the function
fetch_and_store()

# Close database connection
cursor.close()
db.close()
