# GNSS Tracking System using MQTT and Firebase Cloud Integration

## System Architecture

The data flow in this system is as follows:

GNSS Module → Raspberry Pi → Data Processing →  
→ Reverse Geocoding API (Location Name)  
→ MQTT Broker (Real-time streaming)  
→ Firebase Realtime Database (Cloud storage)

---

## Working Principle

1. Raspberry Pi communicates with the GNSS module via serial interface.
2. AT commands are used to enable GPS and fetch location data.
3. Raw GNSS output is parsed to extract latitude and longitude.
4. Coordinates are converted from NMEA format to decimal degrees.
5. Reverse geocoding API converts coordinates into a readable address.
6. Data is published to MQTT broker for real-time updates.
7. Data is pushed to Firebase Realtime Database for cloud storage.

---

## Key Features

- Real-time GNSS location tracking
- Conversion from NMEA format to decimal degrees
- Reverse geocoding using OpenStreetMap API
- MQTT-based live data publishing
- Firebase cloud database integration
- Timestamped location logging
- Embedded serial communication with GNSS module

---

## Technologies Used

- Python 3
- Raspberry Pi
- GNSS/GPS Module
- MQTT Protocol
- Firebase Realtime Database
- OpenStreetMap Nominatim API
- Serial Communication (pyserial)

---

## MQTT (Message Queuing Telemetry Transport)

### Definition

MQTT is a lightweight publish-subscribe network protocol used for IoT communication. It is designed for low bandwidth, high latency, or unreliable networks.

---

### MQTT Architecture

MQTT follows a **publish-subscribe model**:

- Publisher → Sends data
- Broker → Distributes data
- Subscriber → Receives data

---

### MQTT Flow in This Project

GNSS Device → Raspberry Pi (Publisher) → MQTT Broker → Subscribers

---

### MQTT Broker Details

- Broker: broker.hivemq.com  
- Port: 1883  
- Topic Used: gnss/data  

---

### MQTT Python Library

This project uses **Paho MQTT Client**

#### Installation

```bash
pip install paho-mqtt
