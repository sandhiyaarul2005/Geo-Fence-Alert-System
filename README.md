# Geo-Fence Alert System

An IoT-based real-time geofence monitoring and alert system developed using Raspberry Pi and EC200 GNSS/LTE module. The system continuously tracks user location, evaluates geofence boundaries, and generates alerts through audio, SMS, MQTT, and cloud services.

## Features

- Real-time GPS location tracking
- Circular and polygonal geofence support
- Near-boundary warning alerts
- Boundary violation detection
- Audio alerts using speaker
- SMS notifications via LTE
- MQTT-based real-time monitoring
- Node-RED dashboard visualization
- Firebase cloud data storage
- Reverse geocoding support

---

## Hardware Components

- Raspberry Pi
- EC200 GNSS/LTE Module
- GNSS Antenna
- MAX98357A Audio Amplifier
- Speaker
- SIM Card

---

## Technologies Used

- Python
- MQTT Protocol
- HiveMQ Broker
- Node-RED
- Firebase Realtime Database
- OpenStreetMap Nominatim API
- espeak-ng
- Shapely Library
- AT Commands

---

## Project Flow

```text
GPS Satellites
      ↓
EC200 GNSS/LTE Module
      ↓
Raspberry Pi Processing
      ↓
Geofence Evaluation
      ↓
 ┌───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓               ↓
Audio Alert    SMS Alert     MQTT Publish    Firebase
                                      ↓
                             Node-RED Dashboard
```

---

## Working Principle

1. GNSS module acquires real-time GPS coordinates.
2. Raspberry Pi retrieves latitude and longitude using AT commands.
3. Geofence boundaries are initialized.
4. Haversine formula calculates distance from boundary.
5. Near-boundary and outside-boundary conditions are detected.
6. Audio and SMS alerts are generated.
7. Data is published using MQTT.
8. Node-RED dashboard displays live monitoring data.
9. Firebase stores event logs and GPS information.

---

## AT Commands Used

```bash
AT
AT+QGPS?
AT+QGPS=1
AT+QGPSEND
AT+QGPSLOC=2
AT+QGPSGNMEA="GGA"
AT+CPIN?
AT+CEREG?
AT+CMGF=1
AT+CMGS="number"
```

---

## Applications

- Fisherman boundary monitoring
- Vehicle tracking
- Personal safety systems
- Asset monitoring
- Restricted area surveillance
- Industrial safety monitoring

---

## Future Enhancements

- Satellite communication support
- Mobile application integration
- AI-based tracking analytics
- Energy optimization
- Emergency response integration

---

## Authors

- Sandhiya A
- Mirunalini S
- Navina P

Department of Electronics and Communication  
College of Engineering Guindy, Anna University

---

## Sponsor

Centre for Sponsored Research and Consultancy (CSRC)  
Anna University, Chennai
