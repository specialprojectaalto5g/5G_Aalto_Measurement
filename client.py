import subprocess
import json
import os
import re
import requests
from datetime import datetime
import traceback

THIS_DIR = "/home/client4/Workspace"
GPS_OUT = f"{THIS_DIR}/latest_gps.txt"
FAILURE_LOG_OUT = f"{THIS_DIR}/failures.log"
SERVER_URL = "http://20.93.2.23:5000/data"  # Replace with your server IP and port
IMSI = "999408000000101"
CLIENT = "Client_1"

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
            sender_val = line.split()[-4]
            return float(sender_val)

def extract_throughput_re(iperf_output):
    for line in iperf_output.split('\n'):
        if 'receiver' in line:
            receiver_val = line.split()[-5]
            return float(receiver_val)
    return None

def extract_avg_rtt(ping_output):
    rtt_match = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms', ping_output)
    if rtt_match:
        return float(rtt_match.group(1))
    else:
        return None

def gps_val(GPS_OUT):
    try:
        with open(GPS_OUT, 'r') as f:
            lines = f.readlines()
            if lines:
                latlon = re.findall("\d+\.\d+", lines[0])
                if len(latlon) < 2:
                    return -1, -1
                else:
                    lat = float(latlon[0])/100
                    lon = float(latlon[1])/100
                    lat = dms_to_dd(lat)
                    lon = dms_to_dd(lon)
            else:
                return -1, -1
    except Exception:
        lat = -2
        lon = -2
    return lat, lon

def dms_to_dd(cor): 
    deg = int(cor)
    min1 = (cor - deg) * 100
    min = int(min1)
    sec = round((min1 - min) * 100)
    decimal_min = min / 60
    decimal_sec = sec / 3600
    DD = round((deg + decimal_min + decimal_sec), 5)
    return DD

def main():
    iperf_output = run_command(f"iperf3 -c 20.93.2.23 -p 5201")
    ping_output = run_command(f"ping -c 5 20.93.2.23")
    throughput_se = extract_throughput_se(iperf_output)
    throughput_re = extract_throughput_re(iperf_output)
    avg_rtt = extract_avg_rtt(ping_output)

    try:
        os.system(f"timeout 15s sudo gpspipe -r -n 20 | awk -F ',' '/RMC/ {{print $4, $6; exit}}' > {GPS_OUT}")
    except Exception:
        log_error()
    lat, lon = gps_val(GPS_OUT)
    
    now = datetime.now()
    time = int(now.timestamp())
    data = {
        "client": CLIENT,
        "IMSI" : IMSI,
        "timestamp": time,
        "Throughput Sender(Mbit/s)": throughput_se,
        "Throughput Reciever(Mbit/s)": throughput_re,
        "Latency (ms)": avg_rtt,
        "lat": lat,
        "lon": lon
    }
    print(data)    
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print("Data successfully sent to server.")
        else:
            print("Failed to send data to server:", response.status_code, response.text)
    except Exception as e:
        log_error()
    
    os.system(f"rm {GPS_OUT}")
    
if __name__ == "__main__":
    main()
