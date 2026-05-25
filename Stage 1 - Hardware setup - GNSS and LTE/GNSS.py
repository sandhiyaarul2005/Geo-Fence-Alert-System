import serial 
import time 
PORT = "/dev/ttyUSB4" #Can be changed according to the requirement
BAUD = 115200 
def send_at(ser, command, wait=2): 
    ser.write((command + '\r\n').encode()) 
    time.sleep(wait) 
    response = ser.read_all().decode(errors='ignore') 
    return response.strip() 
 
def format_lat_lon(lat, lon): 
    lat = float(lat) 
    lon = float(lon) 
    lat_dir = "N" if lat >= 0 else "S" 
    lon_dir = "E" if lon >= 0 else "W" 
    lat_str = f"{abs(lat):.5f} {lat_dir}" 
    lon_str = f"{abs(lon):.5f} {lon_dir}" 
    return lat_str, lon_str 
 
try: 
    print("Opening GNSS port\n") 
    ser = serial.Serial(PORT, BAUD, timeout=5) 
    time.sleep(2) 
    print("GNSS module connected\n") 
    # AT Test 
    response = send_at(ser, "AT") 
    print("AT Response:") 
    print(response) 
    print() 
    # Check GNSS status 
    response = send_at(ser, "AT+QGPS?", 2) 
    print("GNSS Status:") 
    print(response) 
    print() 
    # Enable only if GNSS is OFF 
    if "+QGPS: 1" not in response: 
        print("Starting GNSS...\n") 
        response = send_at(ser, "AT+QGPS=1", 2) 
        print("GNSS Enable Response:") 
        print(response) 
        print() 
    else: 
        print("GNSS is already enabled\n") 
    print("Waiting for GPS fix...\n") 
    while True: 
        response = send_at(ser, "AT+QGPSLOC=2", 2) 
        print("Raw Response:") 
        print(response) 
        print() 
        if "+QGPSLOC:" in response: 
            gps_data = response.split(":")[1].split(",") 
            utc_time = gps_data[0] 
            latitude = gps_data[1] 
            longitude = gps_data[2] 
            hdop = gps_data[3] 
            altitude = gps_data[4] 
            date = gps_data[9] 
            lat_std, lon_std = format_lat_lon(latitude, longitude) 
            print("===================================") 
            print("        GPS FIX ACQUIRED") 
            print("===================================\n") 
            print("Latitude  :", lat_std) 
            print("Longitude :", lon_std) 
            print("\nUTC Time  :", utc_time) 
            print("Date      :", date) 
            print("\nAltitude  :", altitude, "m") 
            print("HDOP      :", hdop) 
            print("\n===================================") 
            break 
        else: 
            print("Searching for satellites\n") 
        time.sleep(5) 
    ser.close() 
except Exception as e: 
    print("Error:", e) 
