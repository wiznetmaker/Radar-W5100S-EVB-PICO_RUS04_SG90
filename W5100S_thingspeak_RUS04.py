import board
import busio
import digitalio
import analogio
import time
from random import randint
from secrets import secrets
import pwmio
from adafruit_motor import servo
import adafruit_hcsr04

from adafruit_wiznet5k.adafruit_wiznet5k import *
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket

import adafruit_minimqtt.adafruit_minimqtt as MQTT

#SPI
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSn = board.GP17

#Reset
W5x00_RSTn = board.GP20

# create a PWMOut object on the control pin.
pwm = pwmio.PWMOut(board.GP0, duty_cycle=0, frequency=50)
servo = servo.Servo(pwm)

#Sonar
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP2)

print("Wiznet5k Adafruit Up&Down Link Test (DHCP)")
# Setup your network configuration below
# random MAC, later should change this value on your vendor ID
MY_MAC = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05)
IP_ADDRESS = (192, 168, 1, 100)
SUBNET_MASK = (255, 255, 255, 0)
GATEWAY_ADDRESS = (192, 168, 1, 1)
DNS_SERVER = (8, 8, 8, 8)

ethernetRst = digitalio.DigitalInOut(W5x00_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

# For Adafruit Ethernet FeatherWing
cs = digitalio.DigitalInOut(SPI0_CSn)
# For Particle Ethernet FeatherWing
# cs = digitalio.DigitalInOut(board.D5)

spi_bus = busio.SPI(SPI0_SCK, MOSI=SPI0_TX, MISO=SPI0_RX)

# Reset W5x00 first
ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

# # Initialize ethernet interface without DHCP
# eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC, debug=False)
# # Set network configuration
# eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ ADDRESS, DNS_SERVER)

# Initialize ethernet interface with DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=False)

print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))

# MQTT Topic
# Use this topic if you'd like to connect to a standard MQTT broker
sonar1 = secrets["thingspeak_sonar1"]
sonar2 = secrets["thingspeak_sonar2"]
sonar3 = secrets["thingspeak_sonar3"]
sonar4 = secrets["thingspeak_sonar4"]


# Adafruit IO-style Topic
# Use this topic if you'd like to connect to io.adafruit.com
# mqtt_topic = 'aio_user/feeds/temperature'

### Code ###


# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))


def disconnect(client, userdata, rc):
    # This method is called when the client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(client, userdata, topic, pid):
    # This method is called when the client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))

# Initialize MQTT interface with the ethernet interface
MQTT.set_socket(socket, eth)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="mqtt3.thingspeak.com",
    username=secrets["thingspeak_user"],
    password=secrets["thingspeak_pass"],
    client_id=secrets["thingspeak_id"],
    is_ssl=False,
)

# Connect callback handlers to client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish

print("Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()

mqtt_client.subscribe(sonar1)
mqtt_client.subscribe(sonar2)
mqtt_client.subscribe(sonar3)
mqtt_client.subscribe(sonar4)

result = [None] * 32
pub = [None] * 4
while True:
    #send a new message
    for i in range(32):
        servo.angle = i*5
        result[i] = sonar.distance
        print(result[i])
        time.sleep(0.08)
    for i in range(180):
        servo.angle = 180 - i
        time.sleep(0.01)
            
    pub[0] = "field1={0}&field2={1}&field3={2}&field4={3}&field5={4}&field6={5}&field7={6}&field8={7}".format(
        result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7])
    pub[1] = "field1={0}&field2={1}&field3={2}&field4={3}&field5={4}&field6={5}&field7={6}&field8={7}".format(
        result[8],result[9],result[10],result[11],result[12],result[13],result[14],result[15])
    pub[2] = "field1={0}&field2={1}&field3={2}&field4={3}&field5={4}&field6={5}&field7={6}&field8={7}".format(
        result[16],result[17],result[18],result[19],result[20],result[21],result[22],result[23])
    pub[3] = "field1={0}&field2={1}&field3={2}&field4={3}&field5={4}&field6={5}&field7={6}&field8={7}".format(
        result[24],result[25],result[26],result[27],result[28],result[29],result[30],result[31])
    mqtt_client.publish(sonar1, pub[0])
    mqtt_client.publish(sonar2, pub[1])
    mqtt_client.publish(sonar3, pub[2])
    mqtt_client.publish(sonar4, pub[3])
    time.sleep(30)
            

