#define IN1 5
#define IN2 6
#define IN3 9
#define IN4 10
#define ENA 3
#define ENB 11

// CALIBRATION: Adjust these if the robot curves to one side
// If it curves LEFT, increase RIGHT_SPEED or decrease LEFT_SPEED
// If it curves RIGHT, increase LEFT_SPEED or decrease RIGHT_SPEED
#define LEFT_SPEED 80
#define RIGHT_SPEED 80

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  
  stopMotors();
  // No println here to keep the serial buffer clean for the Pi
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "FORWARD") {
      forward();
    }
    else if (cmd == "BACKWARD") {
      backward();
    }
    else if (cmd == "SMOOTH_LEFT") {
      smoothLeft();
    }
    else if (cmd == "SMOOTH_RIGHT") {
      smoothRight();
    }
    else if (cmd == "STOP") {
      stopMotors();
    }
  }
}

void forward() {
  // Assuming these directions based on your "same direction" fix
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, LEFT_SPEED);
  analogWrite(ENB, RIGHT_SPEED);
}

void backward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, LEFT_SPEED);
  analogWrite(ENB, RIGHT_SPEED);
}

void smoothLeft() {
  // Slow down the left motor to turn left
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, LEFT_SPEED * 0.3); // 30% speed
  analogWrite(ENB, RIGHT_SPEED);
}

void smoothRight() {
  // Slow down the right motor to turn right
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, LEFT_SPEED);
  analogWrite(ENB, RIGHT_SPEED * 0.3); // 30% speed
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}