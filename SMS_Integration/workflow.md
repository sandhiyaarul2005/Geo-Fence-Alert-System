# IoT GNSS Tracking System with SMS, MQTT, and Firebase Integration

## Introduction

This project presents the design and implementation of a real-time GNSS-based tracking system using a Raspberry Pi and an EC200 LTE-GNSS module. The system acquires geographic coordinates, resolves them into human-readable locations, and transmits the data through multiple communication channels including SMS, MQTT, and Firebase Realtime Database.

The solution demonstrates a hybrid communication architecture combining cellular and cloud-based IoT technologies for reliable tracking and monitoring.

## System Description

### GNSS Data Acquisition

The EC200 module provides GNSS functionality. The Raspberry Pi communicates with the GNSS engine via serial interface (`/dev/ttyUSB0`) using AT commands to obtain latitude and longitude.

### Reverse Geocoding

The acquired coordinates are converted into a human-readable address using the OpenStreetMap Nominatim API.

### SMS Transmission

The LTE functionality of the EC200 module is used to send SMS alerts via AT commands over a separate serial interface (`/dev/ttyUSB4`).

### MQTT Communication

Location data is published to a public MQTT broker (`broker.hivemq.com`) under a predefined topic for real-time cloud streaming.

### Firebase Integration

All tracking data is logged into Firebase Realtime Database for persistent storage and later analysis.

---

## Features

* Real-time GNSS-based position tracking
* Reverse geocoding for location identification
* SMS alert generation via LTE module
* MQTT-based cloud communication
* Firebase-based data logging
* Continuous autonomous operation

---

## Hardware Requirements

* Raspberry Pi (with USB support)
* EC200 LTE + GNSS Module
* Active SIM card (SMS capability required)
* USB interface connections
* Stable power supply

---

## Software Requirements

* Python 3.x
* Required Python libraries:

```bash
pip install pyserial paho-mqtt firebase-admin
```

---

## Configuration

### Serial Ports

```python
GNSS_PORT = "/dev/ttyUSB0"
LTE_PORT  = "/dev/ttyUSB4"
```

### SMS Configuration

```python
PHONE = "+91XXXXXXXXXX"
```

### Firebase Setup

* Download Firebase Admin SDK credentials
* Place JSON file securely in the system
* Update path in code:

```python
cred = credentials.Certificate("/path/to/firebase.json")
```

* Set database URL:

```python
'databaseURL': 'https://<project-id>.firebaseio.com/'
```

---

## Data Flow

1. GNSS module provides latitude and longitude
2. Raspberry Pi processes and parses the data
3. Reverse geocoding resolves location name
4. Data is transmitted through:

   * SMS (LTE network)
   * MQTT (cloud broker)
   * Firebase (database storage)

---
