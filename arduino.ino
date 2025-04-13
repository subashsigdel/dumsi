#include <Servo.h>

// Define servo pins
#define EYE_VERTICAL_PIN 9
#define EYE_HORIZONTAL_PIN 10
#define JAW_PIN 11
#define NECK_PIN 12

// Define servo angle limits
#define EYE_VERTICAL_MIN 50
#define EYE_VERTICAL_MAX 90
#define EYE_HORIZONTAL_MIN 0
#define EYE_HORIZONTAL_MAX 180
#define JAW_MIN 90
#define JAW_MAX 160
#define NECK_MIN 0
#define NECK_MAX 180

// Create servo objects
Servo eyeVertical;
Servo eyeHorizontal;
Servo jaw;
Servo neck;

// Variables to store current angles
int eyeVerticalPos = 90;  // Center position
int eyeHorizontalPos = 90;  // Center position
int jawPos = 90;  // Closed position
int neckPos = 90;  // Center position

// Variables for talking animation
bool isTalking = false;
unsigned long lastJawMove = 0;
int jawDirection = 1;  // 1 for opening, -1 for closing
int jawStep = 5;  // Degrees to move jaw each step while talking
int jawSpeed = 50;  // Milliseconds between jaw movements

void setup() {
  // Initialize Serial at 9600 baud
  Serial.begin(9600);
  
  // Attach servos to their pins
  eyeVertical.attach(EYE_VERTICAL_PIN);
  eyeHorizontal.attach(EYE_HORIZONTAL_PIN);
  jaw.attach(JAW_PIN);
  neck.attach(NECK_PIN);
  
  // Move servos to initial positions
  eyeVertical.write(eyeVerticalPos);
  eyeHorizontal.write(eyeHorizontalPos);
  jaw.write(jawPos);
  neck.write(neckPos);
  
  Serial.println("Robot initialized. Ready for commands.");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
  
  // Handle jaw movement if talking
  if (isTalking) {
    animateJaw();
  }
}

void processCommand(String command) {
  // Split the command string by the delimiter (space)
  int firstSpace = command.indexOf(' ');
  
  if (firstSpace != -1) {
    String action = command.substring(0, firstSpace);
    String valueStr = command.substring(firstSpace + 1);
    int value = valueStr.toInt();
    
    if (action == "EYE_V") {
      moveEyeVertical(value);
    } 
    else if (action == "EYE_H") {
      moveEyeHorizontal(value);
    } 
    else if (action == "JAW") {
      moveJaw(value);
    } 
    else if (action == "NECK") {
      moveNeck(value);
    }
    else if (action == "TALK") {
      setTalking(value > 0);
    }
    else {
      Serial.println("Unknown command: " + action);
    }
  } 
  else {
    Serial.println("Invalid command format. Use: ACTION VALUE");
  }
}

void moveEyeVertical(int angle) {
  // Constrain the angle to valid range
  angle = constrain(angle, EYE_VERTICAL_MIN, EYE_VERTICAL_MAX);
  eyeVerticalPos = angle;
  eyeVertical.write(angle);
  Serial.println("Eye vertical: " + String(angle));
}

void moveEyeHorizontal(int angle) {
  // Constrain the angle to valid range
  angle = constrain(angle, EYE_HORIZONTAL_MIN, EYE_HORIZONTAL_MAX);
  eyeHorizontalPos = angle;
  eyeHorizontal.write(angle);
  Serial.println("Eye horizontal: " + String(angle));
}

void moveJaw(int angle) {
  // Constrain the angle to valid range
  angle = constrain(angle, JAW_MIN, JAW_MAX);
  jawPos = angle;
  jaw.write(angle);
  Serial.println("Jaw: " + String(angle));
}

void moveNeck(int angle) {
  // Constrain the angle to valid range
  angle = constrain(angle, NECK_MIN, NECK_MAX);
  neckPos = angle;
  neck.write(angle);
  Serial.println("Neck: " + String(angle));
}

void setTalking(bool talking) {
  isTalking = talking;
  if (talking) {
    Serial.println("Started talking");
  } else {
    Serial.println("Stopped talking");
    // Return jaw to closed position
    moveJaw(JAW_MIN);
  }
}

void animateJaw() {
  unsigned long currentTime = millis();
  
  // Check if it's time to move the jaw
  if (currentTime - lastJawMove > jawSpeed) {
    lastJawMove = currentTime;
    
    // Move jaw in current direction
    jawPos += jawStep * jawDirection;
    
    // Check if jaw reached limits
    if (jawPos >= JAW_MAX) {
      jawPos = JAW_MAX;
      jawDirection = -1;  // Change direction
    } else if (jawPos <= JAW_MIN) {
      jawPos = JAW_MIN;
      jawDirection = 1;  // Change direction
    }
    
    // Apply movement
    jaw.write(jawPos);
  }
}