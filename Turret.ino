#include <Servo.h>

Servo servoX;

// transistors 
int base1 = 33;
int base2 = 35;
int base3 = 37;

int base4 = 38;
int base5 = 40;
int base6 = 42;

// ammo counter
const uint8_t ENABLE_PIN = 2;
const uint8_t CLOCK_PIN = 3;
const uint8_t RESET_PIN = 4;

int shootTime = 0;
int percentage = 0;

// reload
int button = 25;

float currentMillis = 0;
float startMillis = 0;

void setup() {
  Serial.begin(9600);
  servoX.attach(6);  

  // transistors
  pinMode(base1, OUTPUT);
  pinMode(base2, OUTPUT);
  pinMode(base3, OUTPUT);

  pinMode(base4, OUTPUT);
  pinMode(base5, OUTPUT);
  pinMode(base6, OUTPUT);

  // seven segment display
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(RESET_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim(); 

    if (data == "No person") {
      stopShooting();
    } else {
      int x = data.toInt();
      
      // Map the x-coordinate to servo angle (0 to 180 degrees)
      int angle = map(x, 0, 640, 180, 0);  
      servoX.write(angle);
      shoot();
      currentMillis = millis() - startMillis;
      shootTime = floor(currentMillis / 1000.0);
    }
  }
  if (digitalRead(button) == HIGH) {
    startMillis = millis();
  }
  
  percentage = (shootTime / 27.0) * 100.0;
  show(100 - floor(percentage));
}

void reset() {
  digitalWrite(RESET_PIN, HIGH);
  //delay(1);
  digitalWrite(RESET_PIN, LOW);
}

void show(int num) {
  //reset();
  digitalWrite(ENABLE_PIN, LOW);
  reset();
  reset();  // <<<<<<<<<<<<<<<<<< It needs 2 resets, why?
  
  for (int i = 0; i < num; i++) {
    digitalWrite(CLOCK_PIN, LOW);
    //delay(1);
    digitalWrite(CLOCK_PIN, HIGH);
  }
  digitalWrite(ENABLE_PIN, HIGH);
}

void shoot() {
  digitalWrite(base1, HIGH);
  digitalWrite(base2, HIGH);
  digitalWrite(base3, HIGH);

  digitalWrite(base4, HIGH);
  digitalWrite(base5, HIGH);
  digitalWrite(base6, HIGH);
}

void stopShooting() {
  digitalWrite(base1, LOW);
  digitalWrite(base2, LOW);
  digitalWrite(base3, LOW);

  digitalWrite(base4, LOW);
  digitalWrite(base5, LOW);
  digitalWrite(base6, LOW);
}