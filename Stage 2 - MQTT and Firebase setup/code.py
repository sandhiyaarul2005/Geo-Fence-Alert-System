import serial
import time
import urllib.request
import json
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db

# ---------------- MQTT CONFIG ----------------
BROKER = "broker.hivemq.com"
PORT_MQTT = 1883
TOPIC = "gnss/data"

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT_MQTT, 60)

# ---------------- FIREBASE CONFIG ----------------
cred = credentials.Certificate("/home/pi/Downloads/geofence-alert-system-firebase-adminsdk-fbsvc-405c605639.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://geofence-alert-system-default-rtdb.firebaseio.com/'
})

# ---------------- GNSS CONFIG ----------------
PORT = "/dev/ttyUSB0"
BAUD = 115200

def send_at(ser, cmd, wait=2):
    ser.write((cmd + '\r\n').encode())
    time.sleep(wait)
    return ser.read_all().decode(errors='ignore')

def nmea_to_decimal(value):
    direction = value[-1]
    value = value[:-1]

    dot = value.index('.')
    degrees = float(value[:dot-2])
    minutes = float(value[dot-2:])
    decimal = degrees + minutes / 60

    if direction in ('S', 'W'):
        decimal = -decimal
    return decimal

def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'RaspberryPi-GPS'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('display_name', 'Place not found')
    except Exception as e:
        return f"Geocoding failed: {e}"

# ---------------- MQTT SEND ----------------
def send_to_mqtt(lat, lon, place):
    data = {
        "latitude": lat,
        "longitude": lon,
        "location": place,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    payload = json.dumps(data)
    mqtt_client.publish(TOPIC, payload)
    print("  MQTT Sent :", payload)

# ---------------- FIREBASE SEND ----------------
def send_to_firebase(lat, lon, place):
    ref = db.reference("gps_data")

    data = {
        "latitude": lat,
        "longitude": lon,
        "location": place,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    ref.push(data)
    print("  Firebase Sent :", data)

# ---------------- MAIN ----------------
ser = serial.Serial(PORT, BAUD, timeout=3)

print("Enabling GNSS...")
send_at(ser, "AT")
send_at(ser, "AT+QGPS=1", 3)
print("Waiting for GPS fix...\n")

while True:
    resp = send_at(ser, "AT+QGPSLOC=0", 2)

    if "+QGPSLOC:" in resp:
        try:
            data = resp.split("+QGPSLOC:")[1].strip().split(",")

            lat = nmea_to_decimal(data[1])
            lon = nmea_to_decimal(data[2])

            print(f"[{time.strftime('%H:%M:%S')}]")
            print(f"  Latitude   : {lat:.6f}")
            print(f"  Longitude  : {lon:.6f}")

            place = reverse_geocode(lat, lon)
            print(f"  Location   : {place}")

            # SEND DATA
            send_to_mqtt(lat, lon, place)
            send_to_firebase(lat, lon, place)

        except Exception as e:
            print(f"  Error: {e}")

    else:
        print(f"[{time.strftime('%H:%M:%S')}] No fix yet... waiting")

    print()
    time.sleep(15)
