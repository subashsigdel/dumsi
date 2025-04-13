#include "EyeControl.h"
#include <Arduino.h>
//// for right and left movement of eyes
void LookLeft(){
    // Look left - faster movement with smaller delay
  for (horizontalPosition = 90; horizontalPosition >= 45; horizontalPosition -= 2) {
    horizontalServo.write(horizontalPosition);
    delay(15);
  }
  delay(500);
}
void LookLeftFast(){
    // Look left - faster movement with smaller delay
  for (horizontalPosition = 90; horizontalPosition >= 45; horizontalPosition -= 4) {
    horizontalServo.write(horizontalPosition);
    delay(15);
  }
  delay(500);
}
void LookRight(){
    // Look right - faster
  for (horizontalPosition = 90; horizontalPosition <= 135; horizontalPosition += 2) {
    horizontalServo.write(horizontalPosition);
    delay(15);
    
  }
  delay(500);
  }
  void LookRightFast(){
    // Look right - faster
  for (horizontalPosition = 90; horizontalPosition <= 135; horizontalPosition += 4) {
    horizontalServo.write(horizontalPosition);
    delay(15);
    
  }
  delay(500);
  }
  
void CenterAfterRight(){
    // Return to center horizontal - faster
  for (horizontalPosition = 135; horizontalPosition >= 90; horizontalPosition -= 2) {
    horizontalServo.write(horizontalPosition);
    delay(15);
  }
  delay(500);
}
  
void CenterAfterRightFast(){
    // Return to center horizontal - faster
  for (horizontalPosition = 135; horizontalPosition >= 90; horizontalPosition -= 4) {
    horizontalServo.write(horizontalPosition);
    delay(15);
  }
  delay(500);
}
void CenterAfterLeft(){
    // Return to center horizontal - faster
  for (horizontalPosition = 45; horizontalPosition <= 90; horizontalPosition += 2) {
    horizontalServo.write(horizontalPosition);
    delay(15);
  }
  delay(500);
}
void CenterAfterLeftFast(){
    // Return to center horizontal - faster
  for (horizontalPosition = 45; horizontalPosition <= 90; horizontalPosition += 4) {
    horizontalServo.write(horizontalPosition);
    delay(15);
  }
  delay(500);
}
////for vertical means up and down of eyes


void EyeUp(){
    // Look up (55 degrees up from center) - faster
  for (verticalPosition = 90; verticalPosition >= 45; verticalPosition -= 2) {
    verticalServo.write(verticalPosition);
    delay(5);
  }
  delay(500);
}
void EyeUpFast(){
    // Look up (55 degrees up from center) - faster
  for (verticalPosition = 90; verticalPosition >= 45; verticalPosition -= 2) {
    verticalServo.write(verticalPosition);
    delay(5);
  }
  delay(500);
}

void CenterAfterEyeUp(){
    // Return to center vertical - faster
  for (verticalPosition = 35; verticalPosition <= 90; verticalPosition += 2) {
    verticalServo.write(verticalPosition);
    delay(15);
  }
  delay(500);
}
void CenterAfterEyeUpFast(){
    // Return to center vertical - faster
  for (verticalPosition = 35; verticalPosition <= 90; verticalPosition += 4) {
    verticalServo.write(verticalPosition);
    delay(15);
  }
  delay(500);
}
void EyeDown(){
    // Look down (55 degrees down from center) - faster
  for (verticalPosition = 90; verticalPosition <= 145; verticalPosition += 2) {
    verticalServo.write(verticalPosition);
     delay(15);
  }
  delay(500);
}
void EyeDownFast(){
    // Look down (55 degrees down from center) - faster
  for (verticalPosition = 90; verticalPosition <= 145; verticalPosition += 4) {
    verticalServo.write(verticalPosition);
     delay(15);
  }
  delay(500);
}



void CenterAfterEyeDown(){
    // Return to center vertical - faster
  for (verticalPosition = 145; verticalPosition >= 90; verticalPosition -= 2) {
    verticalServo.write(verticalPosition);
    delay(15);
  }
  delay(500);
}
void CenterAfterEyeDownFast(){
    // Return to center vertical - faster
  for (verticalPosition = 145; verticalPosition >= 90; verticalPosition -= 4) {
    verticalServo.write(verticalPosition);
    delay(15);
  }
  delay(500);
}
