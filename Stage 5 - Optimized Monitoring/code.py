import serial 
import time 
import json 
import math 
import urllib.request 
import paho.mqtt.client as mqtt 
import firebase_admin 
import os 
from firebase_admin import credentials, db 
from datetime import datetime, timedelta 
 
PORT="/dev/ttyUSB4" 
BAUD=115200 
PHONE="+919786112205" 
BROKER="broker.hivemq.com" 
PORT_MQTT=1883 
TOPIC="geofence_alert" 
 
REF_LAT=13.0106565 
REF_LON=80.2349905 
BOUNDARY_RADIUS=100 
ALERT_DISTANCE=50 
 
cred=credentials.Certificate("/home/pi/Downloads/geofence-alert-system-firebase-adminsdk-fbsvc
f50526cb0e.json") 
firebase_admin.initialize_app(cred,{ 
    'databaseURL':'https://geofence-alert-system-default-rtdb.firebaseio.com/' 
}) 
firebase_ref=db.reference("gps_data") 
 
print("Opening EC200 Port...\n") 
ser=serial.Serial(PORT,BAUD,timeout=2) 
time.sleep(2) 
print("EC200 Connected\n") 
 
mqtt_client=mqtt.Client() 
mqtt_client.connect(BROKER,PORT_MQTT,60) 
mqtt_client.loop_start() 
print("MQTT Connected\n") 
 
last_geo_lat=None 
last_geo_lon=None 
last_place="Unknown Location" 
 
def send_at(cmd,delay=1): 
    ser.reset_input_buffer() 
    ser.write((cmd+"\r").encode()) 
    time.sleep(delay) 
    return ser.read_all().decode(errors='ignore') 
print(send_at("AT")) 
response=send_at("AT+QGPS?",2) 
if "+QGPS: 1" not in response: 
    print(send_at("AT+QGPS=1",3)) 
 
def haversine(lat1,lon1,lat2,lon2): 
    R=6371000 
    lat1=math.radians(lat1) 
    lon1=math.radians(lon1) 
    lat2=math.radians(lat2) 
    lon2=math.radians(lon2) 
    dlat=lat2-lat1 
    dlon=lon2-lon1 
    a=( 
        math.sin(dlat/2)**2+ 
        math.cos(lat1)* 
        math.cos(lat2)* 
        math.sin(dlon/2)**2 
    ) 
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a)) 
    return R*c 
 
def utc_to_ist(utc_time): 
    try: 
        hours=int(utc_time[0:2]) 
        minutes=int(utc_time[2:4]) 
        seconds=int(float(utc_time[4:])) 
        utc_dt=datetime.utcnow().replace( 
            hour=hours, 
            minute=minutes, 
            second=seconds, 
            microsecond=0 
        ) 
        ist_dt=utc_dt+timedelta(hours=5,minutes=30) 
        return ist_dt.strftime("%H:%M:%S") 
    except: 
        return "UNKNOWN" 
 
def reverse_geocode(lat,lon): 
    global last_geo_lat 
    global last_geo_lon 
    global last_place 
    try: 
        if last_geo_lat is None: 
            last_geo_lat=lat 
            last_geo_lon=lon 
        movement=haversine( 
            lat, 
            lon, 
            last_geo_lat, 
            last_geo_lon 
        ) 
        if movement<20: 
            return last_place 
        last_geo_lat=lat 
        last_geo_lon=lon 
        url=( 
            f"https://nominatim.openstreetmap.org/reverse?" 
            f"lat={lat}&lon={lon}" 
            f"&format=json&accept-language=en" 
        ) 
        req=urllib.request.Request( 
            url, 
            headers={'User-Agent':'EC200-GNSS'} 
        ) 
        with urllib.request.urlopen(req,timeout=3) as res: 
            data=json.loads(res.read().decode()) 
            last_place=data.get( 
                "display_name", 
                "Unknown Location" 
            ) 
            return last_place 
    except: 
        return last_place 
 
def play_audio(message): 
    cmd=( 
        f'espeak-ng "{message}" ' 
        f'-s 120 -p 40 --stdout | ' 
        f'aplay -D plughw:2' 
    ) 
    os.system(cmd) 
 
def send_sms(message): 
    send_at("AT") 
    send_at("AT+CMGF=1") 
    send_at('AT+CSCS="GSM"') 
    ser.write(f'AT+CMGS="{PHONE}"\r'.encode()) 
 
    time.sleep(2) 
    ser.read_all() 
    ser.write(message.encode()) 
    time.sleep(1) 
    ser.write(bytes([26])) 
    time.sleep(5) 
    print("SMS SENT\n") 
 
def send_mqtt(data): 
    mqtt_client.publish( 
        TOPIC, 
        json.dumps(data) 
    ) 
    print("MQTT SENT") 
 
def send_firebase(data): 
    firebase_ref.push(data) 
    print("FIREBASE SENT") 
 
def get_gps(): 
    while True: 
        response=send_at("AT+QGPSLOC=2",1) 
        if "+QGPSLOC:" in response: 
            try: 
                data=response.split("+QGPSLOC:")[1].split(",") 
                utc_time=data[0].strip() 
                latitude=float(data[1]) 
                longitude=float(data[2]) 
                ist_time=utc_to_ist(utc_time) 
                return latitude,longitude,ist_time 
            except: 
                pass 
        print("Waiting for GPS Fix...\n") 
        time.sleep(2) 
while True: 
    try: 
        lat,lon,ist_time=get_gps() 
        place=reverse_geocode(lat,lon) 
        distance=haversine( 
            lat, 
            lon, 
            REF_LAT, 
            REF_LON 
        ) 
        boundary_distance=abs( 
            distance-BOUNDARY_RADIUS 
        ) 
        if distance<=BOUNDARY_RADIUS: 
            status="INSIDE BOUNDARY" 
        else: 
 
            status="OUTSIDE BOUNDARY" 
        data={ 
            "timestamp_ist":ist_time, 
            "latitude":lat, 
            "longitude":lon, 
            "place":place, 
            "distance_from_center":round(distance,2), 
            "distance_from_boundary":round(boundary_distance,2), 
            "status":status 
        } 
        print("\n================================") 
        print("TIME      :",ist_time) 
        print("LATITUDE  :",lat) 
        print("LONGITUDE :",lon) 
        print("PLACE     :",place) 
        print("DISTANCE  :",round(distance,2),"m") 
        print("BOUNDARY  :",round(boundary_distance,2),"m") 
        print("STATUS    :",status) 
        print("================================\n") 
        if boundary_distance<=ALERT_DISTANCE: 
            if status=="INSIDE BOUNDARY": 
                alert_message=( 
                    f"Warning. Boundary is " 
                    f"{int(boundary_distance)} meters away" 
                ) 
                sms=( 
                    f"WARNING\n" 
                    f"Boundary Near\n" 
                    f"{round(boundary_distance,1)} meters away\n" 
                    f"Time: {ist_time}" 
                ) 
            else: 
                alert_message=( 
                    f"Warning. Outside boundary. " 
                    f"{int(boundary_distance)} meters from boundary" 
                ) 
                sms=( 
                    f"ALERT\n" 
                    f"Outside Boundary\n" 
                    f"{round(boundary_distance,1)} meters from boundary\n" 
                    f"Time: {ist_time}" 
                ) 
            play_audio(alert_message) 
            send_sms(sms) 
        send_mqtt(data) 
        send_firebase(data) 
        time.sleep(10) 
    except Exception as e: 
        print("ERROR:",e) 
        time.sleep(3)
