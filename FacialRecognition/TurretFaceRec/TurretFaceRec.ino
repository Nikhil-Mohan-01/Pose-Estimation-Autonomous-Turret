const int motorPin1 = 3; // Pin connected to the base of the first transistor
const int motorPin2 = 5; // Pin connected to the base of the second transistor

void setup() {
  // Initialize the motor control pins as outputs
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);

  // Initialize serial communication at 9600 bits per second
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming data as a string
    String data = Serial.readStringUntil('\n');
    
    // Split the string into X and Y coordinates
    int commaIndex = data.indexOf(',');
    String xCoordStr = data.substring(0, commaIndex);
    String yCoordStr = data.substring(commaIndex + 1);

    int xCoord = xCoordStr.toInt();
    int yCoord = yCoordStr.toInt();

    // For demonstration, let's say we'll turn on the motor if the X or Y coordinate is greater than 320 (half the width of the frame)
    if (xCoord > 320 || yCoord > 240) {
      digitalWrite(motorPin1, HIGH);
      digitalWrite(motorPin2, HIGH);
    } else {
      digitalWrite(motorPin1, LOW);
      digitalWrite(motorPin2, LOW);
    }
  }
}
