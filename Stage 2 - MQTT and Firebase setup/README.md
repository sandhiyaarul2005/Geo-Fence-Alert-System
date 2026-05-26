# MQTT and Firebase Cloud Integration
## System Architecture

The data flow in this system is as follows:
GNSS Module → Raspberry Pi → Data Processing → Reverse Geocoding API (Location Name)  → MQTT Broker (Real-time streaming)  → Firebase Realtime Database (Cloud storage)

---

## MQTT (Message Queuing Telemetry Transport)
MQTT is a lightweight publish-subscribe network protocol used for IoT communication. It is designed for low bandwidth, high latency, or unreliable networks.
### MQTT Architecture
MQTT follows a **publish-subscribe model**:
- Publisher → Sends data
- Broker → Distributes data
- Subscriber → Receives data
GNSS Device → Raspberry Pi (Publisher) → MQTT Broker → Subscribers (Live dashboard)
### MQTT Broker Details
- Broker: broker.hivemq.com  
- Port: 1883  
- Topic Used: gnss/data  
### MQTT Python Library installation
This project uses **Paho MQTT Client**
```bash
pip install paho-mqtt
```
### Initialising MQTT in the program
```bash
import paho.mqtt.client as mqtt
mqtt_client = mqtt.Client()
mqtt_client.connect("broker.hivemq.com", 1883, 60)
mqtt_client.publish("gnss/data", payload)
```
---

## Firebase Cloud Integration
Cloud integration allows IoT devices to store and manage data remotely in cloud databases for monitoring and analysis.
Cloud storage used here: Firebase
### Firebase Setup 
- Create a Firebase Account
- Create a New Project
- Enable Realtime Database
- Generate Service Account Key - .json file is generated and this file has to be used in the program
- Get Database URL - This URL is used in the program
### Libraries to be installed
```bash
pip install firebase-admin
```
### Initializing the Firebase in the program
```
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com/'
})
```
---
## Outputs Observed
Reverse geo-coding is performed to convert the geographic-coordinates into human readable address
OpenStreetMap Nominatim API is used: https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json

The program send the latitude, longitude and name of the place to cloud and MQTT broker
---
