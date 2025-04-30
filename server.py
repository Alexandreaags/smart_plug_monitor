# server.py
from flask import Flask, request, jsonify
import sqlite3
import signal
import sys
from datetime import datetime
import pytz

app = Flask(__name__)

# Timezone setup
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

# Connect to the SQLite database
conn = sqlite3.connect("power_data.db", check_same_thread=False)
cursor = conn.cursor()

# Create the table with timestamp in UTC
cursor.execute("""
    CREATE TABLE IF NOT EXISTS power_log (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        power_watts REAL,
        current_a REAL,
        voltage_v REAL
    )
""")
conn.commit()

# CRC-16 calculation (polynomial 0xA001)
def calculate_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if (crc & 0x0001):
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

@app.route("/data", methods=["POST"])
def receive_data():
    try:
        data = request.get_json()

        if not data or "tensao" not in data or "corrente" not in data:
            return jsonify({"error": "Campos 'tensao' e 'corrente' são obrigatórios."}), 400

        voltage = float(data["tensao"])
        current = float(data["corrente"])
        power = voltage * current

        # Mensagem no console indicando que os dados foram recebidos
        print(f"Dados recebidos da ESP: tensão={voltage}V, corrente={current}A, potência={power}W")

        # Get current Brazil timezone time
        brazil_time = datetime.now(BRAZIL_TZ)

        # Store with Brazil timezone timestamp
        cursor.execute("""
            INSERT INTO power_log (timestamp, power_watts, current_a, voltage_v)
            VALUES (?, ?, ?, ?)
        """, (brazil_time, power, current, voltage))
        conn.commit()

        return jsonify({
            "message": "Dados recebidos com sucesso!",
            "timestamp": brazil_time.isoformat(),
            "values": {
                "voltage_v": voltage,
                "current_a": current,
                "power_watts": power
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_exit(sig, frame):
    print("\nShutting down server safely...")
    conn.commit()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    print("Server running. Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=5000)