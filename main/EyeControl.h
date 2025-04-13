#ifndef EYECONTROL_H
#define EYECONTROL_H

#include <Servo.h>

extern Servo horizontalServo;
extern Servo verticalServo;
extern int horizontalPosition;
extern int verticalPosition;

void LookLeft();
void LookLeftFast();
void LookRight();
void LookRightFast();
void CenterAfterRight();
void CenterAfterRightFast();
void CenterAfterLeft();
void CenterAfterLeftFast();
void EyeUp();
void EyeUpFast();
void CenterAfterEyeUp();
void CenterAfterEyeUpFast();
void EyeDown();
void EyeDownFast();
void CenterAfterEyeDown();
void CenterAfterEyeDownFast();

#endif
