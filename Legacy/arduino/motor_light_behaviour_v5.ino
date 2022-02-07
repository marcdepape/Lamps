#include "SoftwareSerial.h"

String project_name = "motor_light_behaviour_v4";

SoftwareSerial ss(A2, A3); // RX + TX

// INCOMING
char in = 'z';
String msg = "";

// SERVO
#include <Adafruit_TiCoServo.h>
Adafruit_TiCoServo lampDial;  // create servo object to control a servo
int servoPin = 9;
int servoReadPin = A0;
int servoReadMin = 5000;
int servoReadMax = 0;
int servoSetMax = 180;
int servoSetMin = 0;
int pos = 0;
int turn_step = 1;

// NEO PIXELS
#include <FastLED.h>
#define top_pixels 16
#define bottom_pixels 24
#define top_neo_pin = 10;
#define bottom_neo_pin = 11;
CRGB top_neo_ring[top_pixels];
CRGB bottom_neo_ring[bottom_pixels];
#define UPDATES_PER_SECOND 100
int hue = 0;
int saturation = 0;
int fade_step = 3;
boolean change = true;
boolean pulse = true;

// MICROPHONE
int analogPin = A1;
boolean onOff = false;
int mic = 0;
int input = 0;
int data = 0;
const int sampleWindow = 50; // Sample window width in mS (50 mS = 20Hz)
unsigned int sample;

void setup() {
  Serial.begin(57600);
  ss.begin(57600);
  Serial.println(project_name);

  // SERVO--------------------------------------------
  pinMode(servoReadPin, INPUT);
  pinMode(servoPin, OUTPUT);

  servoCalibration();

  // NEOPIXEL--------------------------------------------
  FastLED.addLeds<NEOPIXEL, 10>(top_neo_ring, top_pixels);
  FastLED.addLeds<NEOPIXEL, 11>(bottom_neo_ring, bottom_pixels);
}


// MAIN LOOP -------------------------------------------------------

void loop() {
  incomingRequests();
  if (pulse) {
    mic = pulseMic();
    setBottom(mic);
    setTop(map(readServo(), servoSetMin, servoSetMax, 0, 255));
  } else {
    setBoth(map(readServo(), servoSetMin, servoSetMax, 0, 255));
  }
  delay(1);
}

// SERIAL BEHAVIOUR -------------------------------------------------------

void incomingRequests() {
  while (ss.available() > 0) {
    in = ss.read();
    if (in == 'r' || in == 'c' || in == 'l' || in == 'b' || in == 't' || in == 'f' || in == 'h' || in == 's') {
      msg = "";
      msg = String(in);
    } else if (in == '0' || in == '1' || in == '2' || in == '3' || in == '4' || in == '5' || in == '6' || in == '7' || in == '8' || in == '9') {
      msg = msg + String(in);
    } else {

    }
  }
  if (msg.startsWith("r") || msg.startsWith("c") || msg.startsWith("l") || msg.startsWith("b") || msg.startsWith("t") || msg.startsWith("f") || msg.startsWith("h") || msg.startsWith("s")) {
    processCommand(msg);
    in = 'z';
  } else {
    sendReply("ERROR", msg);
    in = 'z';
  }
}

void processCommand(String cmd) {
  String data = "";
  //Serial.println("PROCESS COMMAND");
  if (cmd.length() > 1) {
    for (int i = 1; i < sizeof(cmd) - 1; i++) {
      data = data + cmd[i];
    }
  }
  cmd = cmd[0];
  int val = data.toInt();

  if (cmd != "r") {
    Serial.println(cmd[0]);
  }

  if (cmd == "l") {
    setListen();
  } else if (cmd == "b") {
    setBroadcast();
  } else if (cmd == "c") {
    setChange();
  } else if (cmd == "r") {
    change = true;
    sendReply("READ", String(readServo()));
    //Serial.print("READ");
  } else if (cmd == "t") {
    turn_step = val;
    sendReply("TURN", String(val));
  } else if (cmd == "f") {
    fade_step = val;
    sendReply("FADE", String(val));
  } else if (cmd == "h") {
    hue = val;
    sendReply("HUE", String(val));
  } else if (cmd == "s") {
    saturation = val;
    sendReply("SATURATION", String(val));
    // handle errors
  } else {
    sendReply("CMD ERROR", cmd);
    //Serial.print("ERROR");
  }
}

int sendReply(String message, String reply) {
  //Serial.print(message + "   ");
  //Serial.println(reply);
  message = message + ":";
  ss.print(message);
  ss.println(reply);
}


// SERVO BEHAVIOUR -------------------------------------------------------

int readServo() {
  int reading = analogRead(servoReadPin);
  reading = constrain(map(reading, servoReadMin, servoReadMax, -5, 185), 0, 180);
  return reading;
}

void setListen() {
  int reading = readServo();

  if (change) {
    pulse = false;

    for (int i = mic; i < reading; i = i + fade_step) {
      setBottom(constrain(i, 0, 255));
    }

    lampDial.attach(servoPin);
    while (reading <= servoSetMax) {
      lampDial.write(reading);
      setBoth(map(reading, servoSetMin, servoSetMax, 0, 255));
      reading = reading + turn_step;
      delay(1);
    }
    setBoth(0);
    lampDial.detach();
    change = false;
  }
  sendReply("LISTEN", String(reading));
}

void setBroadcast() {
  int reading = readServo();

  if (change) {
    pulse = true;
    lampDial.attach(servoPin);
    while (reading >= servoSetMin) {
      lampDial.write(reading);
      setBoth(map(reading, servoSetMin, servoSetMax, 0, 255));
      reading = reading - turn_step;
      delay(1);
    }
    setBoth(0);
    lampDial.detach();
    change = false;
  }
  sendReply("BROADCAST", String(reading));
}

void setChange() {
  int reading = readServo();
  pulse = false;

  if (change) {
    for (int i = reading; i > 0; i = i - fade_step) {
      setTop(constrain(i, 0, 255));
    }
    for (int i = 0; i < 255; i = i + fade_step) {
      setTop(constrain(i, 0, 255));
    }
    change = false;
  }
  sendReply("CHANGE", String(reading));
}

// NEO PIXEL BEHAVIOUR ---------------------------------------------------------------

void setTop(int val) {
  for (int i = 0; i < top_pixels; i++) {
    top_neo_ring[i] = CHSV(hue, saturation, val);
    FastLED.show();
    //delay(1);
  }
}

void setBottom(int val) {
  for (int i = 0; i < bottom_pixels; i++) {
    bottom_neo_ring[i] = CHSV(hue, saturation, val);
    FastLED.show();
    //delay(1);
  }
}

void setBoth(int val) {
  for (int i = 0; i < top_pixels; i++) {
    top_neo_ring[i] = CHSV(hue, saturation, val);
    FastLED.show();
    //delay(1);
  }
  for (int i = 0; i < bottom_pixels; i++) {
    bottom_neo_ring[i] = CHSV(hue, saturation, 255 - val);
    FastLED.show();
    //delay(1);
  }
}

int pulseMic() {
  unsigned long startMillis = millis(); // Start of sample window
  unsigned int peakToPeak = 0;   // peak-to-peak level

  unsigned int signalMax = 0;
  unsigned int signalMin = 1024;

  // collect data for 50 mS
  while (millis() - startMillis < sampleWindow)
  {
    sample = analogRead(A1);
    if (sample < 1024)  // toss out spurious readings
    {
      if (sample > signalMax)
      {
        signalMax = sample;  // save just the max levels
      }
      else if (sample < signalMin)
      {
        signalMin = sample;  // save just the min levels
      }
    }
  }
  peakToPeak = signalMax - signalMin;  // max - min = peak-peak amplitude
  //Serial.print(peakToPeak);
  //Serial.print(" : ");
  peakToPeak = constrain(map(peakToPeak, 1, 30, 0, 255), 0, 255);
  return peakToPeak;
}

// SERVO CALIBRATION ---------------------------------

void servoCalibration() {
  lampDial.attach(servoPin);
  lampDial.write(90);
  delay(200);
  
  int reading = readServo();
  while (reading >= servoSetMin) {
    lampDial.write(reading);
    reading--;
    delay(50);
  }
  lampDial.write(0);
  delay(200);
  
  for (int i = 0; i < 100; i++) {
    int input = analogRead(servoReadPin);
    if (input < servoReadMin) {
      servoReadMin = input;
      delay(10);
    }
  }

  // Servo Max
  reading = readServo();
  while (reading <= servoSetMax) {
    lampDial.write(reading);
    reading++;
    delay(50);
  }
  lampDial.write(180);
  delay(200);
  
  for (int i = 0; i < 100; i++) {
    int input = analogRead(servoReadPin);
    if (input > servoReadMax) {
      servoReadMax = input;
      delay(10);
    }
  }

  reading = readServo();
  while (reading >= 90) {
    lampDial.write(90);
    reading--;
    delay(50);
  }
  delay(200);
  lampDial.detach();
  Serial.print("Max: ");
  Serial.print(servoReadMax);
  Serial.print("   Min: ");
  Serial.println(servoReadMin);
}

