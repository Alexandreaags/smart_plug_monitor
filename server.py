from flask import Flask, request, jsonify
import sqlite3
import signal
import sys

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect("power_data.db", check_same_thread=False)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS power_log (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        power_watts REAL
    )
""")
conn.commit()

# Handle incoming data from ESP32
@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    power = data.get("power")

    if power is not None:
        cursor.execute("INSERT INTO power_log (power_watts) VALUES (?)", (power,))
        conn.commit()
        return jsonify({"message": "Data received successfully!"}), 200
    else:
        return jsonify({"error": "Missing 'power' field in request"}), 400

# Clean shutdown on Ctrl+C
def handle_exit(sig, frame):
    print("\nShutting down server safely...")
    conn.commit()
    conn.close()
    sys.exit(0)

# Bind Ctrl+C (SIGINT) to safe exit
signal.signal(signal.SIGINT, handle_exit)

# Start the Flask server
if __name__ == "__main__":
    print("Server running. Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=5000)
