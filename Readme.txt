For Configuring Server & Client
------------------
Server	
------------------
Run the following commands on a fresh Ubuntu VM

sudo apt-get update
sudo apt-get upgrade -y
sudo apt install iperf3

After running these commands execute the "server.sh" file with admin privileges to run three instances for 3 clients.

-------------------
Client
-------------------
Run the following commands on a rPI before executing the "client.py" file.

sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip
sudo pip3 install pymongo
sudo apt install -y iperf3

---------------------
# For Setting Up GPS
---------------------
sudo apt install -y gpsd gpsd-clients
sudo apt install -y gpspipe


Additional Steps for GPS Configuration
You may need to configure gpsd to work with your GPS device. Here’s a basic guide:

Identify your GPS device:
ls /dev/tty*

Configure gpsd:
Edit the GPSD default configuration file:
sudo nano /etc/default/gpsd

Update the configuration to include your GPS device, for example:

START_DAEMON="true"
GPSD_OPTIONS="-n"
DEVICES="/dev/ttyUSB0"
USBAUTO="true"

Restart gpsd:
sudo systemctl restart gpsd
