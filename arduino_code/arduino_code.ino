// PUNYA FAZRIN
#include <LiquidCrystal_I2C.h>
#include <Wire.h> 

LiquidCrystal_I2C lcd(0x27,20,4);

// Serial COMM
String inString = "";
int value;
int inChar;
int steer, speed_PWM, distance, distance_sd;
int incoming[3];

//PID
float SV_steer, MV, MV_A, MV_B, PV, PVc; 
float PVf, PVf_1;
float a, fc, RC;
float Kp,Ti, Ki,Td, Kd;
float et, et_1;
float eint, eint_1, eint_update, ediff;
float interval_elapsed, interval_limit;
int inA = 9;
int inB = 6;
int enA = 3;
int ref = 2;
int inA_2 = 5;
int inB_2 = 11;
int enB = 10;
unsigned long t;
double t_1, Ts;

int dist_fusion;
int posit;

int i = 0;
void setup() {
  lcd.begin();
  lcd.begin();
  lcd.backlight();
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  pinMode(enA, OUTPUT);
  pinMode(inA, OUTPUT);
  pinMode(inB, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(inA_2, OUTPUT);
  pinMode(inB_2, OUTPUT);
  pinMode(ref, OUTPUT);
  digitalWrite(ref, 255);

  interval_elapsed = 0;
  interval_limit = 0.02;

  fc = 0.05;
  RC = 1 / (6.28 * fc);
  Ts = 0.1;
  a = RC / Ts;

  Kp = 7;      //1.6;                             //43.2;
  Ti = 380;     //1.21;   // Hasil Tuning Manual   //1.272; Hasil Perancangan
  Td = 0.5;     //0.1;                              //0.318;

    Ki =Kp/Ti;
    if (Ti==0){
      Ki=0;
    }
    else {
      Ki=Kp/Ti;
    }
  
 
  
  Kd = Kp *Td;

  et_1 = 0;
  PVf_1 = 0;
  eint_1 =0;
  t_1 = 0;

   t = millis();
   delay(100);
   
}

void loop() {
// receiving serial data
  while(Serial.available() >= 4){
    for (int i = 0; i < 4; i++){
      incoming[i] = Serial.read();
    }
    SV_steer = incoming[0]-30;
    speed_PWM = (incoming[1]*2)-100;
    posit = incoming[2]-100;
    dist_fusion = incoming[3]*4;
  }
  Serial.print("SV Steer = ");
  Serial.println(SV_steer);
  Serial.print("Speed_PWM = ");
  Serial.println(speed_PWM);

// Motor Speed
  if (speed_PWM > 0) {
    digitalWrite(inA_2, HIGH);
    digitalWrite(inB_2, LOW);
  }else if (speed_PWM <= 0){
    digitalWrite(inA_2, LOW);
    digitalWrite(inB_2, HIGH);
  }
  analogWrite(enB, abs(speed_PWM));

// PID Steer
   PV = analogRead(A0);
   
   if (PV > 765){
    PV = 765;
   }
   else if (PV < 485){
    PV = 485;
   }
   else {
    PV = PV;
   }
  PV = map(PV, 765, 485, -30, 30);
//  PVf =(PV+a*PVf_1)/(a+1);
PVf=PV;
  if (PVf > 30) {
    PVf = 30;
  }
  else if (PVf < -30) {
    PVf = -30;
  }
  else {
    PVf=PVf;
    }
    Serial.print("PVf = ");
   Serial.println(PVf);
  t = millis();
  delay(100);
  Ts =(t-t_1)/1000;
  
  et = SV_steer - PVf;

  eint_update = ((et+et_1) * Ts) / 2;
  eint = eint_update + eint_1;
  ediff = (et - et_1) / Ts;
  
  MV = (Kp * et  + Kd * ediff); // + Ki * eint
//MV = value;
  if(MV > 0){
    analogWrite (inA, 255);
    digitalWrite(inB, LOW);
  }else if (MV < 0){
   digitalWrite(inA, LOW);
   analogWrite (inB, 255);
  }
  
    MV_A = abs(MV);
  if (MV_A >= 255){
    MV_A = 255;
  }else if (MV_A <= 50){
    MV_A = 50;
  }
                   
    
  analogWrite(enA, MV_A);
  interval_elapsed = interval_elapsed + Ts;

//  if (interval_elapsed >= interval_limit)
//  {
//
  lcd.setCursor(1,0);
  lcd.print("SV Seer = ");
  lcd.print(SV_steer);
  lcd.setCursor(1,1);
  lcd.print("Speed = ");
  lcd.print(speed_PWM);
  lcd.setCursor(1,2);
  lcd.print("Position = ");
  lcd.print(posit);
  lcd.setCursor(1,3);
  lcd.print("Distance = ");
  lcd.print(dist_fusion);
  
//  
//  }
//  else {
//    interval_elapsed = interval_elapsed;
//  }

  et_1 = et;
  eint_1 =eint;

}

