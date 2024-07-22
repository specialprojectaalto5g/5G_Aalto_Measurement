from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
import traceback
import csv
import os

app = Flask(__name__)

POSTGRESQL_URI = "postgresql://test:test@localhost:5432/test"
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
        append_to_csv(data, CSV_FILE_PATH)
        
        # Insert data into PostgreSQL
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                insert_query = sql.SQL("""
                    INSERT INTO network_metrics1 (_id, client, timestamp, throughput_sender, throughput_receiver, latency, lat, lon, imsi)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cur.execute(insert_query, (
                    data['_id'], 
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
        return jsonify({"error": error_message, "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
