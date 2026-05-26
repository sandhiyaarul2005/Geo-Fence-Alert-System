import serial
import time
import json
import urllib.request
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db

# ---------------- CONFIG ----------------
GNSS_PORT = "/dev/ttyUSB0"
LTE_PORT  = "/dev/ttyUSB4"
BAUD = 115200

PHONE = "+91xxxxxxxxxx"

BROKER = "broker.hivemq.com"
PORT_MQTT = 1883
TOPIC = "gnss/tracker/ec200/live"

# ---------------- FIREBASE ----------------
cred = credentials.Certificate(
    "/home/pi/Downloads/geofence-alert-system-firebase-adminsdk-fbsvc-a6e14ea5aa.json"
)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://geofence-alert-system-default-rtdb.firebaseio.com/'
})

firebase_ref = db.reference("gps_data")

# ---------------- SERIAL ----------------
gnss_ser = serial.Serial(GNSS_PORT, BAUD, timeout=3)
lte_ser  = serial.Serial(LTE_PORT, BAUD, timeout=3)

time.sleep(2)

# ---------------- MQTT ----------------
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT_MQTT, 60)

# ---------------- AT ----------------
def send_at(ser, cmd, delay=1):
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    ser.read_all()

# ---------------- GNSS START ----------------
send_at(gnss_ser, "AT")
send_at(gnss_ser, "AT+QGPS=1", 5)

# ---------------- GEO ----------------
def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'EC200'}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode())
            return data.get("display_name", "Unknown")
    except:
        return "Unknown"

# ---------------- SMS ----------------
def send_sms(msg):
    send_at(lte_ser, "AT")
    send_at(lte_ser, "AT+CMGF=1")

    lte_ser.write(f'AT+CMGS="{PHONE}"\r'.encode())
    time.sleep(2)

    lte_ser.write(msg.encode() + b"\r")
    time.sleep(1)

    lte_ser.write(bytes([26]))
    time.sleep(5)

# ---------------- MQTT ----------------
def send_mqtt(lat, lon, place):
    data = {"lat": lat, "lon": lon, "place": place}
    mqtt_client.publish(TOPIC, json.dumps(data))

# ---------------- FIREBASE ----------------
def send_firebase(lat, lon, place):
    firebase_ref.push({
        "latitude": lat,
        "longitude": lon,
        "place": place
    })

# ---------------- GPS ----------------
def get_gps():
    while True:
        gnss_ser.write(b"AT+QGPSLOC=2\r")
        time.sleep(2)

        resp = gnss_ser.read_all().decode(errors='ignore')

        if "+QGPSLOC:" in resp:
            try:
                data = resp.split("+QGPSLOC:")[1].split(",")
                return float(data[1]), float(data[2])
            except:
                pass

        time.sleep(3)

# ---------------- MAIN LOOP ----------------
while True:
    try:
        lat, lon = get_gps()
        place = reverse_geocode(lat, lon)

        print(lat)
        print(lon)
        print(place)

        send_sms(f"{place}\nhttps://maps.google.com/?q={lat},{lon}")
        print("sms sent")

        send_mqtt(lat, lon, place)
        print("mqtt sent")

        send_firebase(lat, lon, place)
        print("cloud sent")

        time.sleep(30)

    except:
        print("error")
        time.sleep(5)
