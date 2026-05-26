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

### MQTT Python Library

This project uses **Paho MQTT Client**

#### Installation

```bash
pip install paho-mqtt
