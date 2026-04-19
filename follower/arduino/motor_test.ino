#define IN1 5
#define IN2 6
#define IN3 9
#define IN4 10
#define ENA 3
#define ENB 11

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  stopMotors();
  Serial.println("Arduino Ready!");
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "FORWARD") {
      // Balanced: Left is slower (150), Right is max (255) to fix the slant
      analogWrite(ENA, 200); analogWrite(ENB, 60); 
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
      Serial.println("Moving Forward!");
    } else if (cmd == "BACKWARD") {
      analogWrite(ENA, 180); analogWrite(ENB, 80);
      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
      Serial.println("Moving Backward!");
    } else if (cmd == "SMOOTH_LEFT") {
      analogWrite(ENA, 150); analogWrite(ENB, 200);
      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
      Serial.println("Turning Left!");
    } else if (cmd == "SMOOTH_RIGHT") {
      analogWrite(ENA, 200); analogWrite(ENB, 150);
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
      Serial.println("Turning Right!");
    } else if (cmd == "STOP") {
      stopMotors();
      Serial.println("Stopped!");
    }
  }
}