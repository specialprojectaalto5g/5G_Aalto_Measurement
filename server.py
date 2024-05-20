from flask import Flask, request, jsonify
from pymongo import MongoClient
import traceback
import csv
import os

app = Flask(__name__)

MONGODB_URI = "mongodb+srv://specialprojectaalto5g:SpecialProjectAalto5g!@cluster0.sdel5ha.mongodb.net/"
DATABASE_NAME = "5G_SP"
COLLECTION_NAME = "5g_cmWave"
CSV_FILE_PATH = "/home/aalto/data.csv"  # Path to the CSV file

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

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
        collection.insert_one(data)
        return jsonify({"message": "Data received and inserted successfully."}), 200
    except Exception as e:
        error_message = str(e)
        return jsonify({"error": error_message, "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
