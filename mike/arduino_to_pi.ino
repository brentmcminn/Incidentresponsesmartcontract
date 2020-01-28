int senseTemp = A0;
int sensorTempInput;
int senseSmoke = A1;
int sensorSmokeInput;
double temp;
double smoke;
boolean actionCounter = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  sensorTempInput = analogRead(A0);
  temp = (double)sensorTempInput / 1024;
  temp = temp *5;
  temp = temp - 0.5;
  temp = temp * 100;  
  
  sensorSmokeInput = analogRead(A1);
  smoke = (double)sensorSmokeInput;

  delay(1000);
  Serial.print(round(temp));
  //delay(1000);
  Serial.print(',');
  //delay(1000);
  Serial.print(round(smoke));
  //delay(1000);
  Serial.print(';');
  //delay(3000);
  
  //if (smoke > 1000 && actionCounter == false){
    //tone(9,88,2000);
    //actionCounter = true;
    
    //}
}