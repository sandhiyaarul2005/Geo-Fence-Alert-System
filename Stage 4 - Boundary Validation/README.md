# Geofence Alert and Monitoring System

## Circular Boundary Algorithm

### Principle
A fixed center coordinate and radius define the geofence.
### Steps
1. Acquire current GPS coordinates.
2. Compute distance from the reference location using the Haversine formula.
3. Compare calculated distance with the predefined boundary radius.
4. Generate status:
   * **Inside Boundary**
   * **Outside Boundary**
5. Trigger alert mechanisms when required.

### Mathematical Model
* Reference Point: `(Latitude₀, Longitude₀)`
* Radius: `R`
* Distance Calculation: Haversine Formula
* Condition:
  * Distance ≤ R → Inside Boundary
  * Distance > R → Outside Boundary
---
## Polygonal Boundary Algorithm
### Principle
A custom polygon is created using multiple GPS coordinates to represent the geofence.
### Steps
1. Define polygon vertices.
2. Obtain current GPS coordinates.
3. Create a GPS point object.
4. Perform Point-in-Polygon analysis using the Shapely library.
5. Determine:
   * **Inside Boundary**
   * **Outside Boundary**
6. Calculate nearest distance from the polygon boundary.
7. Trigger alerts if the object exits the geofence.
### Mathematical Model
* Boundary represented by ordered vertices:
  `(P₁, P₂, P₃ ... Pₙ)`
* Point-in-Polygon containment test
* Minimum distance computed from point to nearest polygon edge
---

## Alert Mechanisms
### SMS Alert
* Sent through Quectel EC200 LTE module.
* Includes: When the system in near boundary region and exceeds the boundary
  * Boundary status
  * Distance from boundary
  * GPS coordinates
  * Location information
### Speaker/Buzzer Alert
* Activated immediately when the tracked object moves outside the permitted boundary.  When the system in near boundary region and exceeds the boundary.
### MQTT Monitoring
* Publishes live geofence data to an MQTT broker.
* Enables real-time dashboard visualization and remote monitoring
### Firebase Realtime Database
Stores:
* Latitude
* Longitude
* Boundary status
* Distance from boundary
* Location details
* Timestamp information
---
