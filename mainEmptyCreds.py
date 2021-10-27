import network
import time
import os
import dht
import sys
import randomJoke
from time import sleep
from umqtt.robust import MQTTClient

from machine import Pin

counter = 0

client = None  # mqtt client

# Pins
sensor = dht.DHT11(Pin(17))

# Creating empty Array for logging temp and humidity later
sensorLogs = []

credentials = {
    "ssid": "---Insert here---",
    "password": "---Insert here---",
    "ADAFRUIT_IO_URL": b"io.adafruit.com",
    "ADAFRUIT_USERNAME": b"---Insert here---",
    "ADAFRUIT_IO_KEY": b"---Insert here---",
    "ADAFRUIT_IO_PUB_FEEDNAME": b"bot_pub",
    "ADAFRUIT_IO_SUB_FEEDNAME": b"bot_sub",
}
m = ""

# returns a new random ID to the API client connector
# Tried to give Ada a new id on connection attempt
def randomId():
    return bytes("client_" + str(int.from_bytes(os.urandom(3), "little")), "utf-8")

# create a random MQTT clientID
mqtt_client_id = randomId()
ADAFRUIT_IO_URL = credentials["ADAFRUIT_IO_URL"]
ADAFRUIT_USERNAME = credentials["ADAFRUIT_USERNAME"]
ADAFRUIT_IO_KEY = credentials["ADAFRUIT_IO_KEY"]
ADAFRUIT_IO_PUB_FEEDNAME = credentials["ADAFRUIT_IO_PUB_FEEDNAME"]
ADAFRUIT_IO_SUB_FEEDNAME = credentials["ADAFRUIT_IO_SUB_FEEDNAME"]

client = MQTTClient(
    client_id=mqtt_client_id,
    server=ADAFRUIT_IO_URL,
    user=ADAFRUIT_USERNAME,
    password=ADAFRUIT_IO_KEY,
    ssl=False,
)

# format of feed name:
#   "ADAFRUIT_USERNAME/feeds/ADAFRUIT_IO_FEEDNAME"
mqtt_pub_feedname = bytes(
    "{:s}/feeds/{:s}".format(ADAFRUIT_USERNAME, ADAFRUIT_IO_PUB_FEEDNAME), "utf-8"
)
mqtt_sub_feedname = bytes(
    "{:s}/feeds/{:s}".format(ADAFRUIT_USERNAME, ADAFRUIT_IO_SUB_FEEDNAME), "utf-8"
)

# WiFi connection information
WIFI_SSID = credentials["ssid"]
WIFI_PASSWORD = credentials["password"]

# turn off the WiFi Access Point
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# the following function is the callback which is
# called when subscribed data is received
def cb(topic, msg):
    if topic == mqtt_sub_feedname:
        global m
        m = msg.decode("utf-8")
        # print (m)
        m = m.lower()
        print(m)

def connectAda():
    try:
        # Disables connection to enable it again
        client.connect(False)
        time.sleep(3)
        print("Trying to connect to Ada")
        client.client_ID = randomId()
        client.connect(True)
        client.set_callback(cb)
        client.subscribe(mqtt_sub_feedname)
    except Exception as e:
        print("could not connect to MQTT server {}{}".format(type(e).__name__, e))

def connectWifi():
    if not wifi.isconnected():
        wifi.disconnect()
        print("Connecting to network...")
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wifi.isconnected():
        pass
    print("network config: ", wifi.ifconfig())

# Runs connectWifi once
connectWifi()

# Runs once
connectAda()
print("mqtt script is done running")

while True:
    counter = counter + 1
    sensor.measure()
    temp = sensor.temperature()
    fahr = temp * (9/5) + 32.0
    hum = sensor.humidity()
    # Saves all DHT info to a var we can then use to append to our sensor list
    sensorLogFormated = " Temp: " + str(hum) + " - Fahr: " + str(fahr) + " - Humidity: " + str(hum)

    try:
        sleep(2)
        print(sensorLogFormated)
        sensorLogs.append(sensorLogFormated)
        if counter >= 500:
            # Deletes the logs in this example so we wont get memory leak of the increasing sensor log size
            sensorLogs.clear()
            counter = 0
        # Note the reason for pass is that the try can get stuck inside a while loop
        # Pass makes it so the code can continue from this point
        pass
    except OSError as e:
        print('Failed to read sensor: ', e)
        pass

    try:
        if m == "fortæl en random joke jarvis":
            #Calls the someJoke function in the randomJoke.py import file
            client.publish(topic=mqtt_pub_feedname, msg=randomJoke.someJoke())
        if m == "tilføj ny måling til listen jarvis":
            client.publish(topic=mqtt_pub_feedname, msg="Tilføjer ny måling...")
            # We append the formated sensor log variable from the start in while loop
            sensorLogs.append(sensorLogFormated)

        if m == "lav 10 temperaturmålinger jarvis":
            # Saves the last 10 logs to a new list. If it was -5 it would take last 5
            # In slicing : for start or end depending where it is -10 indexes to the end/: of the file
            # if it was a list of 1 to 5, and with 2: = 3,4,5 || :3 = 1,2,3
            # if its double :: it means it will take it from start to finish
            lastSensorLogs = sensorLogs[-10:]
            print(lastSensorLogs)
            # We make a empty variable outside the forloop scope
            logsToAda = ""
            for log in lastSensorLogs:
                #We append \n to make a new line for each log on Adafruit terminal
                logsToAda += "\n " + log

            client.publish(topic=mqtt_pub_feedname, msg=logsToAda)

        #Clears the message after the message if checks, else it will loop the same if statement
        m = ""

        # Checks for new messages
        client.check_msg()
        pass

        # Stops the program if Ctrl-C is pressed
    except KeyboardInterrupt:
        print("Ctrl-C pressed...exiting")
        client.disconnect()
        sys.exit()

