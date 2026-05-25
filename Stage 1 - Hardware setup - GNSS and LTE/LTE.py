import serial 
import time 
PORT = "/dev/ttyUSB4" 
BAUD = 115200 
APN  = "airtelgprs.com" 
def send_at(ser, cmd, wait=2): 
    ser.write((cmd + '\r\n').encode()) 
    time.sleep(wait) 
    return ser.read_all().decode(errors='ignore').strip() 
def get_valid_ip(resp): 
    lines = resp.split("\n") 
    for line in lines: 
        if "CGPADDR" in line and "0.0.0.0" not in line: 
            return line.strip() 
    return None 
def main(): 
    print("\nLTE Setup + Activation\n") 
    try: 
        ser = serial.Serial(PORT, BAUD, timeout=3) 
        time.sleep(2) 
        # 1. Basic check 
        print("Checking module") 
        print(send_at(ser, "AT")) 
        # 2. SIM 
        resp = send_at(ser, "AT+CPIN?") 
        print("SIM:", resp) 
        # 3. Network (LTE) 
        resp = send_at(ser, "AT+CEREG?") 
        print("Network:", resp) 
        # 4. Signal 
        resp = send_at(ser, "AT+CSQ") 
        print("Signal:", resp) 
        # 5. Set APN 
        print("\nSetting APN") 
        print(send_at(ser, f'AT+CGDCONT=1,"IP","{APN}"')) 
        # 6. Activate data 
        print("\nActivating LTE data") 
        print(send_at(ser, "AT+CGACT=1,1", 3)) 
        # 7. Check IP 
        resp = send_at(ser, "AT+CGPADDR") 
        ip = get_valid_ip(resp) 
        if ip: 
            print("\nLTE DATA ACTIVE") 
            print("IP:", ip) 
        else: 
            print("\nLTE DATA FAILED (No IP)") 
        ser.close() 
    except Exception as e: 
        print("Error:", e) 
if __name__ == "__main__": 
    main() 
