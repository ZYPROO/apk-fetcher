from flask import Flask, jsonify
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

app = Flask(__name__)

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT")
    )

@app.route('/', methods=['GET'])
def get_apps():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apps")
    apps = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert results to JSON format
    app_list = []
    for app_data in apps:
        app_list.append({
            "id": app_data[0],
            "name": app_data[1],
            "package_name": app_data[2],
            "version": app_data[3],
            "icon_url": app_data[4],
            "screenshot_url": app_data[5]
        })
    return jsonify(app_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')