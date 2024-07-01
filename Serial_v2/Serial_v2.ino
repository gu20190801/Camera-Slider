#include <AccelStepper.h>
#include <AFMotor.h>

// Define the motor driver
AF_Stepper motor1(200, 2); // Assuming you're using Adafruit Motor Shield
AF_Stepper motor2(200, 1);

void forwardstep1() {  
  motor1.onestep(FORWARD, SINGLE);
}
void backwardstep1() {  
  motor1.onestep(BACKWARD, SINGLE);
}

void forwardstep2() {  
  motor2.onestep(FORWARD, SINGLE);
}
void backwardstep2() {  
  motor2.onestep(BACKWARD, SINGLE);
}

AccelStepper stepper1(forwardstep1, backwardstep1);
AccelStepper stepper2(forwardstep2, backwardstep2);

int dist = 3000;
int mode = 0;

void setup() {
  Serial.begin(115200);
  stepper1.setMaxSpeed(400); // Set the maximum speed of the stepper motor
  stepper1.setAcceleration(100); // Set the acceleration of the stepper motor

  stepper2.setMaxSpeed(300); // Set the maximum speed of the stepper motor
  stepper2.setAcceleration(100); // Set the acceleration of the stepper motor
}

void loop() {
  if (mode == 1){
    stepper2.moveTo(1000);
      stepper1.run();
      mode = 0;
  }
  if (mode == -1){
    stepper2.moveTo(-1000);
      stepper1.run();
      mode = 0;
    }
  char ch;
  if (Serial.available()>0){
    ch = Serial.read();
    if (ch == '1'){
      stepper1.setSpeed(400);
      stepper1.runSpeed();
      //stepper1.moveTo(200);
      //stepper1.run();
    }
    else if (ch == '2'){
      stepper1.setSpeed(-400);
      stepper1.runSpeed();
      //stepper1.moveTo(-200);
      //stepper1.run();
    }
    else if (ch == '9'){
      stepper2.stop();
      mode = 0;
    }
    else if (ch == '8'){
      mode = -1;
    }
    else if (ch == '7'){
      mode = 1;
    }
    Serial.read();
  }
}
