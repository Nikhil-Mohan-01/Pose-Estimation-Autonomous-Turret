#include <Servo.h>

Servo myServo;

void setup() {
  Serial.begin(9600); // Initialize serial communication
  myServo.attach(9); // Attach servo to pin 9
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n'); // Read data until newline character
    Serial.println("Received data: " + data); // Print received data for debugging
    
    // Parse the received data
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      String xCoordStr = data.substring(0, commaIndex);
      String zCoordStr = data.substring(commaIndex + 1);
      
      float xCoord = xCoordStr.toFloat(); // Convert string to float
      float zCoord = zCoordStr.toFloat(); // Convert string to float
      
      // Control servo based on zCoord value (assuming zCoord is the depth)
      int angle = map(zCoord, 0, 100, 0, 180); // Map depth range to servo angle (adjust range as needed)
      myServo.write(angle); // Set servo angle
      
      // Print received coordinates and servo angle to serial monitor
      Serial.print("X-coordinate: ");
      Serial.print(xCoord);
      Serial.print(", Z-coordinate: ");
      Serial.print(zCoord);
      Serial.print(", Servo Angle: ");
      Serial.println(angle);
    }
  }
}
