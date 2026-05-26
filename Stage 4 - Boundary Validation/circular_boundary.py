import serial 
import time 
import json 
import math 
import urllib.request 
import paho.mqtt.client as mqtt 
import firebase_admin 
from firebase_admin import credentials, db 
from datetime import datetime 
# ========================================================= 
# CONFIGURATION 
# ========================================================= 
PORT = "/dev/ttyUSB4" 
BAUD = 115200 
PHONE = "+919786112205" 
BROKER = "broker.hivemq.com" 
PORT_MQTT = 1883 
TOPIC = "geofence_alert" 
# ========================================================= 
# CIRCULAR GEOFENCE 
# ========================================================= 
# Center Coordinate 
REF_LAT = 13.0106565 
REF_LON = 80.2349905 
# Radius in meters 
BOUNDARY_RADIUS = 100 
# ========================================================= 
# FIREBASE 
# ========================================================= 
cred = credentials.Certificate( 
    "/home/pi/Downloads/geofence-alert-system-firebase-adminsdk-fbsvc-f50526cb0e.json" 
) 
firebase_admin.initialize_app(cred, { 
    'databaseURL': 'https://geofence-alert-system-default-rtdb.firebaseio.com/' 
}) 
firebase_ref = db.reference("gps_data") 
# ========================================================= 
# SERIAL CONNECTION 
# ========================================================= 
print("Opening EC200 Port...\n") 
 
ser = serial.Serial(PORT, BAUD, timeout=3) 
time.sleep(2) 
print("EC200 Connected\n") 
# ========================================================= 
# MQTT CONNECTION 
# ========================================================= 
mqtt_client = mqtt.Client() 
mqtt_client.connect(BROKER, PORT_MQTT, 60) 
mqtt_client.loop_start() 
print("MQTT Connected\n") 
# ========================================================= 
# AT COMMAND FUNCTION 
# ========================================================= 
def send_at(cmd, delay=1): 
    ser.reset_input_buffer() 
    ser.reset_output_buffer() 
    ser.write((cmd + "\r").encode()) 
    time.sleep(delay) 
    response = ser.read_all().decode(errors='ignore') 
    return response 
# ========================================================= 
# START GNSS 
# ========================================================= 
print(send_at("AT")) 
response = send_at("AT+QGPS?", 2) 
if "+QGPS: 1" not in response: 
    print("Starting GNSS...\n") 
    print(send_at("AT+QGPS=1", 5)) 
else: 
    print("GNSS Already Enabled\n") 
# ========================================================= 
# REVERSE GEOCODING 
# ========================================================= 
def reverse_geocode(lat, lon): 
    url = ( 
        f"https://nominatim.openstreetmap.org/reverse?" 
        f"lat={lat}&lon={lon}&format=json&accept-language=en" 
    ) 
    req = urllib.request.Request( 
        url, 
        headers={'User-Agent': 'EC200-GNSS'} 
    ) 
    try: 
        with urllib.request.urlopen(req, timeout=10) as res: 
            data = json.loads(res.read().decode()) 
            return data.get("display_name", "Unknown Location") 
    except: 
        return "Unknown Location" 
# ========================================================= 
# HAVERSINE DISTANCE 
# ========================================================= 
 
def haversine(lat1, lon1, lat2, lon2): 
    R = 6371000 
    lat1 = math.radians(lat1) 
    lon1 = math.radians(lon1) 
    lat2 = math.radians(lat2) 
    lon2 = math.radians(lon2) 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = ( 
        math.sin(dlat / 2) ** 2 
        + math.cos(lat1) 
        * math.cos(lat2) 
        * math.sin(dlon / 2) ** 2 
    ) 
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) 
    return R * c 
# ========================================================= 
# SMS FUNCTION 
# ========================================================= 
def send_sms(lat, lon, place, status, distance): 
    short_place = place[:60] 
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S") 
    message = ( 
        f"{status}\n" 
        f"Dist: {distance:.1f} m\n" 
        f"Lat: {lat}\n" 
        f"Lon: {lon}\n" 
        f"{short_place}" 
    ) 
    send_at("AT") 
    send_at("AT+CMGF=1") 
    send_at('AT+CSCS="GSM"') 
    ser.write(f'AT+CMGS="{PHONE}"\r'.encode()) 
    time.sleep(3) 
    ser.read_all() 
    ser.write(message.encode()) 
    time.sleep(1) 
    ser.write(bytes([26])) 
    time.sleep(8) 
    print("SMS SENT\n") 
# ========================================================= 
# MQTT FUNCTION 
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
    print("MQTT SENT") 
# ========================================================= 
# FIREBASE FUNCTION 
# ========================================================= 
def send_firebase(lat, lon, place, status, distance): 
    firebase_ref.push({ 
        "latitude": lat, 
        "longitude": lon, 
        "place": place, 
        "status": status, 
        "distance": distance 
    }) 
    print("FIREBASE SENT") 
# ========================================================= 
# GPS FUNCTION 
# ========================================================= 
def get_gps(): 
    while True: 
        response = send_at("AT+QGPSLOC=2", 2) 
        if "+QGPSLOC:" in response: 
            try: 
                data = response.split("+QGPSLOC:")[1].split(",") 
                latitude = float(data[1]) 
                longitude = float(data[2]) 
                return latitude, longitude 
            except: 
                pass 
        print("Waiting for GPS Fix...\n") 
        time.sleep(3) 
# ========================================================= 
# MAIN LOOP 
# ========================================================= 
while True: 
    try: 
        lat, lon = get_gps() 
        place = reverse_geocode(lat, lon) 
        distance = haversine( 
            lat, 
            lon, 
            REF_LAT, 
            REF_LON 
        ) 
        if distance <= BOUNDARY_RADIUS: 
            status = "INSIDE BOUNDARY" 
        else: 
            status = "OUTSIDE BOUNDARY" 
 
 
        print("===================================") 
        print("LATITUDE :", lat) 
        print("LONGITUDE:", lon) 
        print("DISTANCE :", round(distance, 2), "m") 
        print("STATUS   :", status) 
        print("PLACE    :", place) 
        print("===================================\n") 
        send_sms( 
            lat, 
            lon, 
            place, 
            status, 
            distance 
        ) 
        send_mqtt( 
            lat, 
            lon, 
            place, 
            status, 
            distance 
        ) 
        send_firebase( 
            lat, 
            lon, 
            place, 
            status, 
            distance 
        ) 
        time.sleep(30) 
    except Exception as e: 
        print("ERROR:", e) 
        time.sleep(5) 
