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

    // Check if the data indicates a face match
    if (data == "True") {
      // Face match found, turn off the motor
      digitalWrite(motorPin1, LOW);
      digitalWrite(motorPin2, LOW);
    } else {
      // No face match, turn on the motor
      digitalWrite(motorPin1, HIGH);
      digitalWrite(motorPin2, HIGH);
    }
  }
}
