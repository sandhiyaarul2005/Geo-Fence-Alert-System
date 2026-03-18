# Hardware Specification and Configuration Guide

## 1. Introduction

This document outlines the hardware components and configuration procedures for the Geo-Fence Alert System. The system integrates a GNSS-enabled LTE module with a Raspberry Pi to enable real-time positioning and cellular data communication.

---

## 2. Hardware Specifications

### 2.1 Core Components

* **Processing Unit:** Raspberry Pi (Linux-based embedded platform)
* **GNSS Module:** Integrated GNSS receiver for real-time positioning : EC200G-CN LTE Cat 1 4G GNSS Industrial Modem
* **LTE Module:** Cellular communication module supporting packet data services : EC200G-CN LTE Cat 1 4G GNSS Industrial Modem
* **SIM Card:** Required for LTE network connectivity
* **Interface:** USB-based serial communication

### 2.2 Functional Capabilities

* Continuous acquisition of geospatial coordinates
* Support for NMEA sentence output (e.g., `$GNRMC`, `$GNGSV`)
* Cellular network registration and data session establishment
* IP-based communication for cloud integration

---

## 3. GNSS Configuration

### 3.1 Initialization and Control

The GNSS subsystem is controlled using standard AT commands over a serial interface.

| Function              | Command              |
| --------------------- | -------------------- |
| Communication check   | `AT`                 |
| Enable GNSS engine    | `AT+QGPS=1`          |
| Satellite information | `AT+QGPSGNMEA="GSV"` |
| Location retrieval    | `AT+QGPSLOC=2`       |

---

### 3.2 Data Acquisition and Processing

The GNSS module outputs standard NMEA sentences. The `$GNRMC` sentence is used to extract valid positioning data.

Processing steps:

1. Read serial data from GNSS interface
2. Identify valid fix (`Status = A`)
3. Extract latitude and longitude fields
4. Convert coordinates from NMEA format to decimal degrees
5. Validate and update location periodically

---

### 3.3 Software Interface

A Python-based interface is used for:

* Serial communication with the GNSS module
* Real-time parsing of NMEA data
* Coordinate conversion to decimal format
* Reverse geocoding using external APIs
* Periodic update and display of location data

---

## 4. LTE Configuration

### 4.1 Network and SIM Verification

| Function             | Command                 |
| -------------------- | ----------------------- |
| SIM status check     | `AT+CPIN?`              |
| Network registration | `AT+CREG?`, `AT+CGREG?` |
| Signal strength      | `AT+CSQ`                |
| Network information  | `AT+QNWINFO`            |

---

### 4.2 Packet Data Configuration

| Function             | Command                              |
| -------------------- | ------------------------------------ |
| Set APN              | `AT+CGDCONT=1,"IP","airtelgprs.com"` |
| Attach to network    | `AT+CGATT=1`                         |
| Activate PDP context | `AT+QIACT=1`                         |
| Verify IP address    | `AT+QIACT?`                          |

---

## 5. System Integration

The overall system operation follows a sequential workflow:

1. GNSS module acquires real-time positional data
2. Raspberry Pi reads and processes GNSS output via serial interface
3. Coordinates are converted and validated
4. LTE module establishes network connectivity
5. Processed data is transmitted to remote servers using MQTT or HTTP protocols

---

## 6. Conclusion

The described hardware configuration provides a robust platform for real-time geolocation and communication. The integration of GNSS and LTE technologies enables reliable deployment of geo-fencing and location-based alert systems in practical environments.

