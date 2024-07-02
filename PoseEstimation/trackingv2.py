import serial
import time

try:
    # Open the serial port
    ser = serial.Serial('COM9', 9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish

    print("Connected to Arduino on COM9")

    # Send data to Arduino
    ser.write(b'Hello Arduino\n')
    time.sleep(1)  # Wait for the Arduino to process the data

    # Read data from Arduino
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print("Received from Arduino:", line)

    # Close the serial port
    ser.close()
    print("Serial port closed")

except serial.SerialException as e:
    print(f"Error: {e}")
except PermissionError as e:
    print(f"Permission Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
