import requests
import time
from datetime import datetime
import pytz

def send_data():
    # Configurations
    SERVER_URL = "http://192.168.15.24:5000/data"  # Change if server is remote

    # Example values (you could adjust these to vary over time)
    voltage = 220.0  # Volts
    current = 1.5    # Amps

    # Send data in a loop
    while True:
        # Create synthetic data payload
        data_payload = {"tensao": voltage, "corrente": current}

        print(f"Sending synthetic data at {datetime.now(pytz.timezone('America/Sao_Paulo')).isoformat()}: {data_payload}")

        # Send data
        try:
            response = requests.post(SERVER_URL, json=data_payload)

            # Handle response
            print("Response status:", response.status_code)
            print("Response body:", response.text)
        except Exception as e:
            print(f"Error sending synthetic data: {e}")

        # Adjust voltage and current for next iteration
        voltage += 0.1
        current += 0.05

        # Wait for a fixed interval before sending the next packet (e.g., 1 second)
        time.sleep(1)

if __name__ == "__main__":
    print("Starting to send synthetic data in real-time...")
    send_data()
