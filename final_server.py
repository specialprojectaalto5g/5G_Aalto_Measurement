from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
import traceback
import csv
import os
import logging

import logging

#for  print debug information (for troubleshoting)
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('13aug-logs.log'),
        logging.StreamHandler()  # Optional: to also see logs in console
    ]
)

app = Flask(__name__)

POSTGRESQL_URI = "postgresql://sopro:sopro@localhost:5432/database"
CSV_FILE_PATH = "/home/rahmana7/data.csv"  # Path to the CSV file

# Connect to PostgreSQL database
def get_pg_connection():
    return psycopg2.connect(POSTGRESQL_URI)

def append_to_csv(data, file_path):
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write header only if the file doesn't exist

        writer.writerow(data)  # Write the data

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")
        append_to_csv(data, CSV_FILE_PATH)

        # Define the mapping of incoming field names to expected field names
        field_mapping = {
            'client': 'client',
            'IMSI': 'imsi',
            'timestamp': 'timestamp',
            'Throughput Sender(Mbit/s)': 'throughput_sender',
            'Throughput Reciever(Mbit/s)': 'throughput_receiver',
            'Latency (ms)': 'latency',
            'lat': 'lat',
            'lon': 'lon'
        }

        # Remap fields
        data = {field_mapping.get(k, k): v for k, v in data.items()}

        # Basic validation
        required_fields = ['client', 'timestamp', 'throughput_sender', 'throughput_receiver', 'latency', 'lat', 'lon', 'imsi']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(f"Missing required data fields: {', '.join(missing_fields)}")

        # Type validation
        try:
            data['client'] = str(data['client'])
            data['timestamp'] = int(data['timestamp'])
            data['throughput_sender'] = float(data['throughput_sender'])
            data['throughput_receiver'] = float(data['throughput_receiver'])
            data['latency'] = float(data['latency'])
            data['lat'] = float(data['lat'])
            data['lon'] = float(data['lon'])
            data['imsi'] = float(data['imsi'])
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid data type") from e

        # Insert data into PostgreSQL
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                insert_query = sql.SQL("""
                    INSERT INTO network_metrics (client, timestamp, throughput_sender, throughput_receiver, latency, lat, lon, imsi)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cur.execute(insert_query, (
                    data['client'],
                    int(data['timestamp']),
                    float(data['throughput_sender']),
                    float(data['throughput_receiver']),
                    float(data['latency']),
                    float(data['lat']),
                    float(data['lon']),
                    float(data['imsi'])
                ))
                conn.commit()

        return jsonify({"message": "Data received and inserted successfully."}), 200
    except Exception as e:
        error_message = str(e)
        logging.error(f"Error occurred: {error_message}")
        logging.error(traceback.format_exc())
        return jsonify({"error": error_message, "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
