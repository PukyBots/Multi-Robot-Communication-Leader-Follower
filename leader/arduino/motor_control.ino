#define M1_PWM 10
#define M1_DIR 6
#define M2_PWM 9
#define M2_DIR 5
#define ENC_RIGHT_A 3
#define ENC_RIGHT_B 2
#define ENC_LEFT_A A4
#define ENC_LEFT_B A5

volatile long rightCount = 0;
volatile long leftCount = 0;

void rightEncoderA() {
  if (digitalRead(ENC_RIGHT_A) == digitalRead(ENC_RIGHT_B))
    rightCount++;
  else
    rightCount--;
}

void rightEncoderB() {
  if (digitalRead(ENC_RIGHT_A) == digitalRead(ENC_RIGHT_B))
    rightCount--;
  else
    rightCount++;
}

void leftEncoderA() {
  if (digitalRead(ENC_LEFT_A) == digitalRead(ENC_LEFT_B))
    leftCount++;
  else
    leftCount--;
}

void setup() {
  Serial.begin(9600);
  pinMode(M1_PWM, OUTPUT);
  pinMode(M1_DIR, OUTPUT);
  pinMode(M2_PWM, OUTPUT);
  pinMode(M2_DIR, OUTPUT);
  pinMode(ENC_RIGHT_A, INPUT_PULLUP);
  pinMode(ENC_RIGHT_B, INPUT_PULLUP);
  pinMode(ENC_LEFT_A, INPUT_PULLUP);
  pinMode(ENC_LEFT_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_RIGHT_A), rightEncoderA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_RIGHT_B), rightEncoderB, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_LEFT_A), leftEncoderA, CHANGE);
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "FORWARD") {
      digitalWrite(M1_DIR, LOW);
      analogWrite(M1_PWM, 150);
      digitalWrite(M2_DIR, LOW);
      analogWrite(M2_PWM, 150);
    }
    else if (cmd == "BACKWARD") {
      digitalWrite(M1_DIR, HIGH);
      analogWrite(M1_PWM, 150);
      digitalWrite(M2_DIR, HIGH);
      analogWrite(M2_PWM, 150);
    }
    else if (cmd == "SMOOTH_LEFT") {
      digitalWrite(M1_DIR, LOW);
      analogWrite(M1_PWM, 60);
      digitalWrite(M2_DIR, LOW);
      analogWrite(M2_PWM, 150);
    }
    else if (cmd == "SMOOTH_RIGHT") {
      digitalWrite(M1_DIR, LOW);
      analogWrite(M1_PWM, 150);
      digitalWrite(M2_DIR, LOW);
      analogWrite(M2_PWM, 60);
    }
    else if (cmd == "STOP") {
      analogWrite(M1_PWM, 0);
      analogWrite(M2_PWM, 0);
    }
  }
  static unsigned long lastTime = 0;
  if (millis() - lastTime >= 100) {
    Serial.print("ENC:");
    Serial.print(rightCount);
    Serial.print(",");
    Serial.println(leftCount);
    lastTime = millis();
  }
}