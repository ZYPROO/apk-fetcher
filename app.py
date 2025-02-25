from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT")
    )

# Route to get all apps
@app.route('/apps', methods=['GET'])
def get_apps():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT a.id, a.name, a.package_name, a.version, a.icon_url, a.screenshot_url, a.company, a.game_page,
               dl.link1, dl.link2, dl.link3, dl.link4
        FROM apps a
        LEFT JOIN download_links dl ON a.id = dl.app_id
    """
    cursor.execute(query)
    apps = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert results to JSON
    app_list = []
    for app_data in apps:
        app_list.append({
            "id": app_data[0],
            "name": app_data[1],
            "package_name": app_data[2],
            "version": app_data[3],
            "icon_url": app_data[4],
            "screenshot_url": app_data[5].split(',')[:10],
            "company": app_data[6],
            "game_page": app_data[7],
            "download_links": {
                "1": app_data[8],
                "2": app_data[9],
                "3": app_data[10],
                "4": app_data[11]
            }
        })
    return jsonify(app_list)

# Route to get a specific app by package name
@app.route('/apps/<package_name>', methods=['GET'])
def get_app_by_package_name(package_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT a.id, a.name, a.package_name, a.version, a.icon_url, a.screenshot_url, a.company, a.game_page,
               dl.link1, dl.link2, dl.link3, dl.link4
        FROM apps a
        LEFT JOIN download_links dl ON a.id = dl.app_id
        WHERE a.package_name = %s
    """
    cursor.execute(query, (package_name,))
    app_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if app_data:
        app_details = {
            "id": app_data[0],
            "name": app_data[1],
            "package_name": app_data[2],
            "version": app_data[3],
            "icon_url": app_data[4],
            "screenshot_url": app_data[5].split(',')[:10],
            "company": app_data[6],
            "game_page": app_data[7],
            "download_links": {
                "1": app_data[8],
                "2": app_data[9],
                "3": app_data[10],
                "4": app_data[11]
            }
        }
        return jsonify(app_details)
    else:
        return jsonify({"error": "App not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')