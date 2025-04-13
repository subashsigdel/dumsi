#ifndef NECKCONTROL_H
#define NECKCONTROL_H

#include <Servo.h>

extern Servo NeckServo;
extern Servo JawServo;
extern int NeckServoPosition;
extern int JawServoPosition;


void NeckMoveRight();
void NeckMoveCenterAfterRight();
void NeckMoveLeft();
void NeckMoveCenterAfterLeft();
void JawMoveRight();
void JawMoveCenterAfterRight();

#endif
