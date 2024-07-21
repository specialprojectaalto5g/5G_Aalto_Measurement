import csv
import psycopg2

# Database connection parameters
conn = psycopg2.connect(
    dbname="test",
    user="test",
    password="test",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Open the CSV file
with open('admin.admin.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row if there is one
    for row in reader:
        try:
            # Insert the data into the PostgreSQL table
            cur.execute("""
                INSERT INTO network_metrics1 (_id, client, timestamp, rtt_client_ns, rtt_server_ns, dl_throughput_kbps, ul_throughput_kbps, lat, lon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row[0],  # _id
                row[1],  # client
                int(row[2]),  # timestamp
                int(row[3]),  # rtt_client_ns
                int(row[4]),  # rtt_server_ns
                float(row[5]),  # dl_throughput_kbps
                float(row[6]),  # ul_throughput_kbps
                float(row[7]),  # lat
                float(row[8])  # lon
            ))
            conn.commit()  # Commit the transaction after each successful insert
        except Exception as e:
            conn.rollback()  # Rollback the transaction on error
            print(f"Error inserting row: {e}")
            print(f"Problematic row: {row}")

# Close the connection
cur.close()
conn.close()
