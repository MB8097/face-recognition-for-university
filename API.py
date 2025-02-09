import re
from flask import Flask, jsonify, request
import sqlite3
import base64

app = Flask(__name__)

DATABASE = "access_log.db"

# Fetch logs from the database with regex date filtering
def fetch_logs_with_regex(table_name, date_regex=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if date_regex:
        # Filter logs where the timestamp matches the regex
        cursor.execute(f"SELECT name, timestamp, image FROM {table_name}")
        rows = cursor.fetchall()
        logs = [
            {
                "name": row[0],
                "timestamp": row[1],
                "image": base64.b64encode(row[2]).decode('utf-8') if row[2] else None
            }
            for row in rows if re.match(date_regex, row[1])
        ]
    else:
        # Fetch all logs if no date filter is provided
        cursor.execute(f"SELECT name, timestamp, image FROM {table_name}")
        rows = cursor.fetchall()
        logs = [
            {
                "name": row[0],
                "timestamp": row[1],
                "image": base64.b64encode(row[2]).decode('utf-8') if row[2] else None
            }
            for row in rows
        ]
    conn.close()
    return logs

# Endpoint for unauthorized logs
@app.route('/logs', methods=['GET'])
def fetch_unauthorized_logs():
    date = request.args.get('date')
    date_regex = rf"^{date}.*" if date else None  # Match timestamps starting with the specified date
    logs = fetch_logs_with_regex("unauthorized_logs", date_regex)
    return jsonify(logs)

# Endpoint for authorized logs
@app.route('/authorized_logs', methods=['GET'])
def fetch_authorized_logs():
    date = request.args.get('date')
    date_regex = rf"^{date}.*" if date else None  # Match timestamps starting with the specified date
    logs = fetch_logs_with_regex("authorized_logs", date_regex)
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
