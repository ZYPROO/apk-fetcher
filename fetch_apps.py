from google_play_scraper import app
import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

# 🔹 Read package names from file
def read_package_names(file_path):
    with open(file_path, "r") as f:
        return {line.strip() for line in f.readlines()}

# 🔹 Connect to PostgreSQL
db = psycopg2.connect(
    host=os.getenv("PGHOST"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    database=os.getenv("PGDATABASE"),
    port=os.getenv("PGPORT")
)
cursor = db.cursor()

app_packages = read_package_names("packages.txt")

# 🔹 Get existing packages from the database
cursor.execute("SELECT package_name FROM apps")
existing_packages = {row[0] for row in cursor.fetchall()}

# 🔹 Find which apps to add, update, and delete
apps_to_add_or_update = app_packages - existing_packages
apps_to_delete = existing_packages - app_packages

print(f"✅ New/Updated Apps: {len(apps_to_add_or_update)} | ❌ Apps to Delete: {len(apps_to_delete)}")

# 🔹 Delete apps that are no longer in `packages.txt`
if apps_to_delete:
    cursor.execute("DELETE FROM apps WHERE package_name = ANY(%s)", (list(apps_to_delete),))
    db.commit()
    print(f"🗑️ Deleted {len(apps_to_delete)} apps from the database.")

# 🔹 Fetch and store only new/updated apps
def fetch_and_store():
    for package in apps_to_add_or_update:
        try:
            data = app(package)
            name = data['title']
            version = data['version']
            icon_url = data['icon']
            company = data.get('developer', 'Unknown')  # Fetch company name
            screenshot_urls = ','.join(data['screenshots'])  # Store all available screenshots

            # 🔹 Insert or update app data
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

            print(f"✅ Fetched and stored: {name} (Version: {version})")

            # 🔹 Short delay to prevent blocking
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error fetching {package}: {e}")

# 🔹 Run fetch function
if apps_to_add_or_update:
    fetch_and_store()
else:
    print("✅ All apps are up to date. No changes needed.")

# 🔹 Close database connection
cursor.close()
db.close()
