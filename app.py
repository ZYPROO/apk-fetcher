from flask import Flask, jsonify
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

app = Flask(__name__)

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )

@app.route('/apps', methods=['GET'])
def get_apps():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM apps")
    apps = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(apps)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)