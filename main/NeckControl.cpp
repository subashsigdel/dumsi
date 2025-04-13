#include "NeckControl.h"
#include <Arduino.h>

void NeckMoveRight(){
    // Look right - faster
  for (NeckServoPosition = 90; NeckServoPosition <= 180; NeckServoPosition += 1) {
    NeckServo.write(NeckServoPosition);
    delay(15);
    
  }
  delay(1000);
  
}

void NeckMoveCenterAfterRight(){
    // Return to center horizontal - faster
  for (NeckServoPosition = 180; NeckServoPosition >= 90; NeckServoPosition -= 1) {
    NeckServo.write(NeckServoPosition);
    delay(15);
  }
  delay(1000);
  
}

void NeckMoveLeft(){
    // Look left - faster movement with smaller delay
  for (NeckServoPosition = 90; NeckServoPosition >= 0; NeckServoPosition -= 1) {
    NeckServo.write(NeckServoPosition);
    delay(15);
  }
  delay(1000);
  
}

void NeckMoveCenterAfterLeft(){
      // Return to center horizontal - faster
  for (NeckServoPosition = 0; NeckServoPosition <= 90; NeckServoPosition += 1) {
    NeckServo.write(NeckServoPosition);
    delay(15);
  }
  delay(1000);
  
}

void JawMoveRight(){
    // Look right - faster
  for (JawServoPosition = 90; JawServoPosition <= 160; JawServoPosition += 10) {
    JawServo.write(JawServoPosition);
    delay(5);
    
  }
  delay(1000);
  
}
void JawMoveCenterAfterRight(){
    // Return to center horizontal - faster
  for (JawServoPosition = 160; JawServoPosition >= 90; JawServoPosition -= 10) {
    JawServo.write(JawServoPosition);
    delay(5);
  }
  delay(1000);
  
}
