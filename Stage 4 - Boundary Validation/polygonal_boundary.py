import serial
import time
import json
import math
import urllib.request
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db
import RPi.GPIO as GPIO
from shapely.geometry import Point, Polygon

# =========================================================
# CONFIGURATION
# =========================================================
GNSS_PORT = "/dev/ttyAMA0"
LTE_PORT = "/dev/ttyUSB4"
BAUD_GNSS = 9600
BAUD_LTE = 115200

PHONE = "+91xxxxxxxxxx"

BROKER = "broker.hivemq.com"
PORT_MQTT = 1883
TOPIC = "geofence/polygon/alert"

# =========================================================
# FIREBASE
# =========================================================
cred = credentials.Certificate(
    "/home/pi/Downloads/geofence-alert-system-firebase-adminsdk.json"
)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://geofence-alert-system-default-rtdb.firebaseio.com/'
})

firebase_ref = db.reference("polygon_gps_data")

# =========================================================
# POLYGON BOUNDARY (CEG CAMPUS)
# =========================================================
BOUNDARY_POLYGON = [
    (80.2331, 13.0085),
    (80.2328, 13.0112),
    (80.2357, 13.0137),
    (80.2401, 13.0125),
    (80.2382, 13.0098),
    (80.2363, 13.0083),
]

polygon = Polygon(BOUNDARY_POLYGON)

# =========================================================
# GPIO BUZZER
# =========================================================
BUZZER_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def buzzer_on():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzzer_off():
    GPIO.output(BUZZER_PIN, GPIO.LOW)

# =========================================================
# SERIAL
# =========================================================
gnss_ser = serial.Serial(GNSS_PORT, BAUD_GNSS, timeout=1)
lte_ser = serial.Serial(LTE_PORT, BAUD_LTE, timeout=3)

time.sleep(2)

# =========================================================
# MQTT
# =========================================================
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT_MQTT, 60)
mqtt_client.loop_start()

# =========================================================
# AT COMMAND
# =========================================================
def send_at(ser, cmd, delay=1):
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    return ser.read_all().decode(errors='ignore')

# =========================================================
# REVERSE GEOCODING
# =========================================================
def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'EC200-GNSS'})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode())
            return data.get("display_name", "Unknown Location")
    except:
        return "Unknown Location"

# =========================================================
# DISTANCE FROM BOUNDARY
# =========================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def distance_from_boundary(lat, lon, polygon):
    point = Point(lon, lat)
    nearest = polygon.boundary.interpolate(polygon.boundary.project(point))
    return haversine(lat, lon, nearest.y, nearest.x)

# =========================================================
# SMS FUNCTION (LTE EC200)
# =========================================================
def send_sms(lat, lon, place, status, distance):
    msg = (
        f"{status}\n"
        f"Dist: {distance:.1f} m\n"
        f"{place[:60]}\n"
        f"https://maps.google.com/?q={lat},{lon}"
    )

    send_at(lte_ser, "AT")
    send_at(lte_ser, "AT+CMGF=1")
    send_at(lte_ser, 'AT+CSCS="GSM"')

    lte_ser.write(f'AT+CMGS="{PHONE}"\r'.encode())
    time.sleep(2)

    lte_ser.write(msg.encode())
    time.sleep(1)

    lte_ser.write(bytes([26]))  # CTRL+Z
    time.sleep(6)

    print("SMS SENT")

# =========================================================
# MQTT
# =========================================================
def send_mqtt(lat, lon, place, status, distance):
    data = {
        "latitude": lat,
        "longitude": lon,
        "place": place,
        "status": status,
        "distance": distance
    }
    mqtt_client.publish(TOPIC, json.dumps(data))

# =========================================================
# FIREBASE
# =========================================================
def send_firebase(lat, lon, place, status, distance):
    firebase_ref.push({
        "latitude": lat,
        "longitude": lon,
        "place": place,
        "status": status,
        "distance": distance
    })

# =========================================================
# GPS READ
# =========================================================
def get_gps():
    while True:
        gnss_ser.write(b"AT+QGPSLOC=2\r")
        time.sleep(2)

        resp = gnss_ser.read_all().decode(errors='ignore')

        if "+QGPSLOC:" in resp:
            try:
                data = resp.split("+QGPSLOC:")[1].split(",")
                lat = float(data[1])
                lon = float(data[2])
                return lat, lon
            except:
                pass
        time.sleep(2)

# =========================================================
# MAIN LOOP
# =========================================================
while True:
    try:
        lat, lon = get_gps()
        place = reverse_geocode(lat, lon)

        point = Point(lon, lat)

        if polygon.contains(point):
            status = "INSIDE BOUNDARY"
            buzzer_off()
        else:
            status = "OUTSIDE BOUNDARY"
            buzzer_on()

        dist = distance_from_boundary(lat, lon, polygon)

        print("LAT:", lat)
        print("LON:", lon)
        print("STATUS:", status)
        print("DIST:", dist)
        print("PLACE:", place)

        send_sms(lat, lon, place, status, dist)
        send_mqtt(lat, lon, place, status, dist)
        send_firebase(lat, lon, place, status, dist)

        time.sleep(30)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
