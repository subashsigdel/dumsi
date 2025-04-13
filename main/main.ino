#include <Servo.h>
#include "EyeControl.h"
#include "NeckControl.h"
// Create servo objects
Servo horizontalServo;  // For left/right movement
Servo verticalServo;    // For up/down movement
Servo NeckServo;
Servo JawServo;

// Define the pins for the servos
const int horizontalServoPin = 9;
const int verticalServoPin = 10;
const int NeckServoPin = 11;
const int JawServoPin = 12;

// Variables for eye positions
int horizontalPosition = 90; // Center position horizontally
int verticalPosition = 90;   // Center position vertically
int NeckServoPosition = 90;
int JawServoPosition = 90;

void setup() {
  // Attach servos to pins
  horizontalServo.attach(horizontalServoPin);
  verticalServo.attach(verticalServoPin);
  NeckServo.attach(NeckServoPin);
  JawServo.attach(JawServoPin);
 
  // Initialize eyes to center position
  horizontalServo.write(horizontalPosition);
  verticalServo.write(verticalPosition);
  NeckServo.write(NeckServoPosition);
  JawServo.write(JawServoPosition);
 
  Serial.begin(9600);
}

<<<<<<< Updated upstream


void loop(){
 if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    if (command == "headleft") {
      // Turn left action
      NeckMoveLeft();
      NeckMoveCenterAfterLeft();
    }
    else if (command == "headright") {
      // Turn right action
      NeckMoveRight();
      NeckMoveCenterAfterRight();
    }else if (command == "openmouth") {
      // Turn right action
      JawMoveRight();
    }else if (command == "closemouth") {
      // Turn right action
      JawMoveCenterAfterRight();
    }else if (command == "lookright") {
      // Turn right action
      LookRight();
      CenterAfterRight();
    }else if (command == "lookleft") {
      // Turn right action
      LookLeft();
      CenterAfterLeft();
    }
    
    
    
    
    
    }
    
  
=======
void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "LEFT") LookLeft();
    else if (command == "LEFT_FAST") LookLeftFast();
    else if (command == "RIGHT") LookRight();
    else if (command == "RIGHT_FAST") LookRightFast();
    else if (command == "CENTER_FROM_LEFT") CenterAfterLeft();
    else if (command == "CENTER_FROM_LEFT_FAST") CenterAfterLeftFast();
    else if (command == "CENTER_FROM_RIGHT") CenterAfterRight();
    else if (command == "CENTER_FROM_RIGHT_FAST") CenterAfterRightFast();
    else if (command == "EYE_UP") EyeUp();
    else if (command == "EYE_UP_FAST") EyeUpFast();
    else if (command == "EYE_DOWN") EyeDown();
    else if (command == "EYE_DOWN_FAST") EyeDownFast();
    else if (command == "NECK_LEFT") NeckMoveLeft();
    else if (command == "NECK_RIGHT") NeckMoveRight();
    else if (command == "NECK_CENTER_FROM_LEFT") NeckMoveCenterAfterLeft();
    else if (command == "NECK_CENTER_FROM_RIGHT") NeckMoveCenterAfterRight();
    else if (command == "JAW_OPEN") JawMoveRight();
    else if (command == "JAW_CLOSE") JawMoveCenterAfterRight();
    
    // Send back an acknowledgment
    Serial.println("OK");
  }
>>>>>>> Stashed changes
}
