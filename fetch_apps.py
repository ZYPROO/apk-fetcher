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

# Step 1: Remove outdated data (apps not in packages.txt)
cursor.execute("DELETE FROM apps WHERE package_name NOT IN %s", (tuple(app_packages),))
db.commit()

# Step 2: Fetch and store the latest data
def fetch_and_store():
    for package in app_packages:
        try:
            data = app(package)

            name = data['title']
            version = data['version']
            icon_url = data['icon']
            company = data.get('developer', 'Unknown')  # Fetch company name
            screenshot_urls = ','.join(data['screenshots'])  # Store all available screenshots

            # Insert or update the database
            sql = """
                INSERT INTO apps (name, package_name, version, icon_url, screenshot_url, company)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (package_name)
                DO UPDATE SET 
                    version = EXCLUDED.version, 
                    icon_url = EXCLUDED.icon_url, 
                    screenshot_url = EXCLUDED.screenshot_url,
                    company = EXCLUDED.company
            """
            values = (name, package, version, icon_url, screenshot_urls, company)

            cursor.execute(sql, values)
            db.commit()

            print(f"✅ Updated: {name} (Version: {version})")

            # Short delay to prevent rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error fetching {package}: {e}")

# Run the function
fetch_and_store()

# Close database connection
cursor.close()
db.close()
