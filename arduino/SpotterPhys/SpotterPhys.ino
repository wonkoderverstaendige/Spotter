/* 
  Arduino/Python interface for Spotter.

  After reset the Arduino will wait for a handshake command.
  Once received, it will continually check the sensors and
  report their values via Serial port. At the same time incoming
  commands and data will be written to digital ports or via
  SPI to the DACs for analog out of e.g. coordinates, speed...

  Created 18 January 2013
  by Ronny Eichler

*/
#include "SPI.h" // handles SPI communication to MCP4921 DAC

#define pin_SCK 52
#define pin_MOSI 51
#define pin_MISO 50

// SPI clients
#define pin_dev0 48
#define pin_dev1 49

// digital input pins
#define pin_din0 30
#define pin_din1 31
#define pin_din2 32
#define pin_din3 33

// digital output pins
#define pin_dout0 40
#define pin_dout1 41
#define pin_dout2 42
#define pin_dout3 43

boolean msgComplete = false; // command data complete
byte inCommand = 0;
int inData = 0;

byte outData = 0;
byte device = 0;

byte inByte[4] = {0, 0, 0, 0};
byte data = 0;

byte n = 0;

void setup(){
  // initialize serial connection
 Serial.begin(57600);
 
  // ready SPI to talk to DAC
  pinMode(pin_dev0, OUTPUT);
  pinMode(pin_dev1, OUTPUT);
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
 
   // ready digital input pins
  pinMode(pin_din0, INPUT);
  pinMode(pin_din1, INPUT);
  pinMode(pin_din2, INPUT);
  pinMode(pin_din3, INPUT);
  
  // ready ditital output pins
  pinMode(pin_dout0, OUTPUT);
  pinMode(pin_dout1, OUTPUT);
  pinMode(pin_dout2, OUTPUT);
  pinMode(pin_dout3, OUTPUT);
  
  setDAC(0, 0);
  setDAC(1, 0);
  delay(200);
  setDAC(0, 4095);
  setDAC(1, 4095);
  delay(200);
  setDAC(0, 0);
  setDAC(1, 0);
}

void loop() {
  if (msgComplete) {
    interpret();
    msgComplete = false;
  }
}
  

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  inData = 0;
  inCommand = 0;
  n = 0;
//  while (Serial.available()) {
//    while (n < 4) {
//      // get the new byte:
//      inByte[n] = Serial.read();
//      if (inByte[n] > -1) {
//        n++;
//      }
//    }
//  }
}

void interpret() {
  Serial.println(inByte[0]);
  Serial.println(inByte[1]);
  Serial.println(inByte[2]);
  if (inByte[3] == '\n') {
    inCommand = inByte[0];
    inData = inByte[1] + (inByte[2]<<8);
    
    Serial.println(inCommand);
    Serial.println(inData);
    
    if (inCommand == 48) {
      setDAC(0, inData);
    } else if (inCommand == 49) {
      setDAC(1, inData);
    } else if (inCommand == 42) {
      Serial.println('Hello Spotter!');
    }
  } 
//  else {
//    msgComplete = false;
//  }
}


void setDAC(int device, int outputValue) {
    // should set device!
    if (device == 0 ) {
      digitalWrite(pin_dev0, LOW);
    } else if (device == 1) {
      digitalWrite(pin_dev1, LOW);
    }
    
    data = highByte(outputValue);
    data = 0b00001111 & data;
    data = 0b00110000 | data;
    SPI.transfer(data);
    data = lowByte(outputValue);
    SPI.transfer(data);
    
    if (device == 0 ) {
      digitalWrite(pin_dev0, HIGH);
    } else if (device == 1) {
      digitalWrite(pin_dev1, HIGH);
    }
}
