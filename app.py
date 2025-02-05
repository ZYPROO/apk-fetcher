from flask import Flask, jsonify
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

db_password = os.getenv("DB_PASSWORD")

app = Flask(__name__)

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=db_password,
        database="apk_database"
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
    app.run(debug=True)
