//Simple motor serial communication with python
//By: Logan Norman

int data; int c1; int c2; int i; int k;
void setup() {
 Serial.begin(115200); 
  pinMode(2, OUTPUT); pinMode(3, OUTPUT);   //BottomRotation
  pinMode(5, OUTPUT); pinMode(6, OUTPUT);   //TopRotation
  pinMode(8, OUTPUT); pinMode(9, OUTPUT);   //BottomLinear
  pinMode(11, OUTPUT);pinMode(12, OUTPUT);  //TopLinear
  pinMode(4, OUTPUT); digitalWrite(7, LOW); //Drive Activation
  pinMode(7, OUTPUT); digitalWrite(7, LOW); //Drive Activation
  pinMode(10, OUTPUT); digitalWrite(7, LOW); //Drive Activation
  pinMode(13, OUTPUT); digitalWrite(7, LOW); //Drive Activation

}

void loop() {
while (Serial.available()){
  data = Serial.read();

if (data == 'a'){ //Clockwiseb
  digitalWrite(2, LOW);
  Runmotor(3);
}

if (data == 'b'){ //Counterclockwiseb
  digitalWrite(2, HIGH);
  Runmotor(3);
}

if (data == 'c'){ //Clockwiset
  digitalWrite(5, LOW);
  Runmotor(6);
}

if (data == 'd'){ //CounterClockwiset
  digitalWrite(5, HIGH);
  Runmotor(6);
}

if (data == 'e'){ //Backwardb
  digitalWrite(8, LOW);
  Runmotor(9);
}

if (data == 'f'){ //Forwardb
  digitalWrite(8, HIGH);
  Runmotor(9);
}

if (data == 'g'){ //Backwardt
  digitalWrite(11, LOW);
  Runmotor(12);
}

if (data == 'h'){ //Forwardt
  digitalWrite(11, HIGH);
  Runmotor(12);
}

if (data == 'j'){

  digitalWrite(2, HIGH);
  while (analogRead(A2) == 1){
    digitalWrite (3, HIGH);
    delayMicroseconds(10000);
    digitalWrite (3, LOW);
    delayMicroseconds(10000); 
  }
  digitalWrite(8, LOW);
  while (analogRead(A3) == 1){
    digitalWrite (9, HIGH);
    delayMicroseconds(10000);
    digitalWrite (9, LOW);
    delayMicroseconds(10000);
  }
}
}
}

void Runmotor(int x)
{
delay(30);
c1=Serial.read();
for(i=0; i<c1; i++) {
    digitalWrite (x, HIGH);
    delayMicroseconds(10000);
    digitalWrite (x, LOW);
    delayMicroseconds(10000);
  }
  Serial.flush();

}
