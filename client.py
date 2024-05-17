import subprocess
import json
import os
import re
import pymongo
from datetime import datetime
import random

# MongoDB connection details
MONGODB_URI = "mongodb+srv://specialprojectaalto5g:SpecialProjectAalto5g!@cluster0.sdel5ha.mongodb.net/"
DATABASE_NAME = "5G_SP"
COLLECTION_NAME = "5g_cmWave"
THIS_DIR = "/home/client1/Workspace"
GPS_OUT = f"{THIS_DIR}/latest_gps.txt"
FAILURE_LOG_OUT = f"{THIS_DIR}/failures.log"


def log_error():
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    with open(FAILURE_LOG_OUT, 'a+') as f:
        f.write(f"{now_str}\n{traceback.format_exc()}\n")
        
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def extract_throughput_se(iperf_output):
    for line in iperf_output.split('\n'):
        if 'sender' in line:
            sender_val=line.split()[-4]
            #print(sender_val)
            return float(sender_val)


def extract_throughput_re(iperf_output):
    throughput_re_match = re.search(r'(\d+\.\d+)\s*Mbits/sec\s*receiver', iperf_output)
    if throughput_re_match:
        return float(throughput_re_match.group(1))  # Convert throughput to float
    else:
        return None
def extract_avg_rtt(ping_output):
    rtt_match = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms', ping_output)
    if rtt_match:
        return float(rtt_match.group(1))  # Convert RTT to float
    else:
        return None

def gps_val(GPS_OUT):
    # Parse GPS results
    try:
        with open(GPS_OUT, 'r') as f:
            lines = f.readlines()
            if lines:  # Check if lines is not empty
                latlon = re.findall("\d+\.\d+", lines[0])
                if len(latlon) < 2:
                    return -1,-1
                else:
                    lat = float(latlon[0])/100
                    lon = float(latlon[1])/100
                    lat = dms_to_dd(lat)
                    lon = dms_to_dd(lon)
            else:
                # Handle the case where lines is empty
                return -1,-1
    except Exception:
        lat = -2
        lon = -2
    return lat,lon

def dms_to_dd(cor): 
    deg=int(cor) #get degrees
    min1=(cor-deg)*100
    min=int(min1)   #get minutes
    sec = round((min1-min)*100) #get seconds
    # transform from DMS to coordinates
    decimal_min = min / 60  
    decimal_seg= sec / 3600
    DD = round((deg + decimal_min + decimal_seg),5)
    return DD

def main():

    # Run iperf command to measure throughput
    # Change the port number for the client 
    # 5201 = Client 1
    # 5202 = Client 2
    # 5203 = Client 3 so on
    iperf_output = run_command(f"iperf3 -c 20.93.2.23 -p 5201")

    # Run ping command to measure latency
    ping_output = run_command(f"ping -c 5 20.93.2.23")

    # Extract relevant information
    throughput_se = extract_throughput_se(iperf_output)
    throughput_re = extract_throughput_re(iperf_output)
    avg_rtt = extract_avg_rtt(ping_output)

    try:
    # Run GPS
        os.system(f"timeout 15s sudo gpspipe -r -n 20 | awk -F ',' '/RMC/ {{print $4, $6; exit}}' > {GPS_OUT}")
    except Exception:
        log_error()
    lat,lon=gps_val(GPS_OUT)
    
    now=datetime.now()
    time= int(now.timestamp())
    # Prepare data
    data = {
        "client": "Client_2",
        "timestamp": time,  # Convert datetime to Unix time
        "Throughput Sender(Mbit/s)": throughput_se,
        "Throughput Reciever(Mbit/s)": throughput_re,
        "Latency (ms)": avg_rtt,
        "lat": lat,
        "lon": lon
    }

    # Print data
    print("Data:", data)
    # Connect to MongoDB
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Insert data into MongoDB
    collection.insert_one(data)
    
    # Clean up so we don't use stale files next time
    os.system(f"rm {GPS_OUT}")
    
if __name__ == "__main__":
    main()
