from google_play_scraper import app
import psycopg2
import time
from dotenv import load_dotenv
import os

load_dotenv()

def read_package_names(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

# Connect to PostgreSQL
db = psycopg2.connect(
    host=os.getenv("PGHOST"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    database=os.getenv("PGDATABASE"),
    port=os.getenv("PGPORT")
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
            screenshots = ','.join(data['screenshots'][:5])  # Store up to 5 screenshots
            
            # Insert data into PostgreSQL table
            sql = """
                INSERT INTO apps (name, package_name, version, icon_url, screenshot_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (package_name)
                DO UPDATE SET version = EXCLUDED.version, icon_url = EXCLUDED.icon_url, screenshot_url = EXCLUDED.screenshot_url
            """
            values = (name, package, version, icon_url, screenshots)
            cursor.execute(sql, values)
            db.commit()

            print(f"✅ Fetched and stored: {name} (Version: {version})")

            # Add a short delay to prevent rate-limiting
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error fetching {package}: {e}")

# Run the function
fetch_and_store()

# Close database connection
cursor.close()
db.close()