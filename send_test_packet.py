import requests
import struct
import time
from datetime import datetime
import pytz

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

def create_packet(voltage: float, current: float) -> bytes:
    # Format voltage and current to "000,00" (with comma)
    voltage_str = f"{voltage:06.2f}".replace('.', ',')  # Always 6 characters
    current_str = f"{current:06.2f}".replace('.', ',')

    # Build payload
    payload = bytearray()
    payload.append(0xAA)                  # Identifier
    payload.extend(b'T:')                  # T:
    payload.extend(voltage_str.encode())   # Voltage value
    payload.extend(b'C:')                  # C:
    payload.extend(current_str.encode())   # Current value

    # Calculate CRC
    crc = calculate_crc16(payload)
    payload.extend(struct.pack('<H', crc)) # Little endian CRC

    return payload

def send_data():
    # Configurations
    SERVER_URL = "http://localhost:5000/data"  # Change if server is remote

    # Example values (you could adjust these to vary over time)
    voltage = 220.0  # Volts
    current = 1.5    # Amps

    # Send data in a loop
    while True:
        packet = create_packet(voltage, current)

        print(f"Sending packet at {datetime.now(pytz.timezone('America/Sao_Paulo')).isoformat()}: {packet.hex()}")

        # Send packet
        try:
            response = requests.post(SERVER_URL, data=packet)

            # Handle response
            print("Response status:", response.status_code)
            print("Response body:", response.text)
        except Exception as e:
            print(f"Error sending packet: {e}")

        # Optionally adjust voltage and current for next iteration
        voltage += 0.1  # Increment voltage
        current += 0.05  # Increment current

        # Wait for a fixed interval before sending the next packet (e.g., 5 seconds)
        time.sleep(1)

if __name__ == "__main__":
    print("Starting to send data in real-time...")
    send_data()
