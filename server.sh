#!usr/bin

# Serving Client 1
iperf3 -s -p 5201 -B 0.0.0.0 -D --logfile iperf3_server1.log 

# Serving Client 2
iperf3 -s -p 5202 -B 0.0.0.0 -D --logfile iperf3_server2.log

# Serving Client 3
iperf3 -s -p 5203 -B 0.0.0.0 -D --logfile iperf3_server3.log

#Running Server to capture the messages from Clients and sent to MongoDB
python3 final_server.py > server.log 2>&1 &
