## 5. System Architecture

The system architecture is organized into distinct functional layers to ensure modularity, scalability, and efficient data flow.

### 5.1 Functional Layers

**1. Data Acquisition Layer**
- The GNSS receiver integrated within the LTE module acquires signals from navigation satellites.
- It generates positioning information in the form of NMEA sentences (e.g., GPGGA, GPRMC).
- This data is transmitted to the Raspberry Pi through a serial communication interface (USB/UART).

**2. Processing Layer**
- The Raspberry Pi serves as the central processing unit of the system.
- It reads the incoming GNSS data stream continuously.
- Relevant parameters such as latitude and longitude are extracted and formatted for further analysis.

**3. Geofence Evaluation Layer**
- A virtual boundary is defined using:
  - Center coordinates (latitude and longitude)
  - Radius (in meters)
- The system computes the distance between the current position and the defined center point.
- A logical decision is made to determine whether the device is within or outside the geofence.

**4. Communication Layer**
- The LTE module provides internet connectivity.
- When a geofence breach is detected, alert data is transmitted to a remote server using communication protocols such as HTTP.

---

### 5.2 Data Flow

The overall data flow in the system is as follows:

GNSS Satellites  
→ LTE Module (GNSS Receiver)  
→ Raspberry Pi (Serial Communication)  
→ Data Parsing and Processing  
→ Geofence Evaluation  
→ LTE Communication  
→ Remote Server / Monitoring System  

---

## 6. Working Principle

The operation of the geo-fence alert system is based on continuous location monitoring and boundary evaluation.

1. The GNSS module receives signals from satellites and determines the device’s geographic position.  

2. The Raspberry Pi establishes serial communication with the LTE module and reads NMEA data continuously.  

3. The received data is parsed to extract latitude and longitude coordinates.  

4. A geofence is predefined by specifying a center coordinate and a radius.  

5. The system calculates the distance between the current location and the geofence center using a geographic distance formula.  

6. The calculated distance is compared with the predefined radius:
   - If the distance is within the radius, the device is considered inside the geofence.
   - If the distance exceeds the radius, a geofence breach is detected.  

7. Upon detecting a breach, the system sends an alert to a remote server via the LTE network.  
