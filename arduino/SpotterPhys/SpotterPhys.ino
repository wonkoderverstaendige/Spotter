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
#ifdef DEBUG_FLAG
#define DEBUGLN(x)  Serial.println(x)
#define DEBUG(x)  Serial.print(x)
#else
#define DEBUGLN(x)
#define DEBUG(x)
#endif

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

int tmp = 0;
byte inBytes[4] = {
  0, 0, 0, 0};
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
  digitalWrite(pin_dev0, HIGH);
  digitalWrite(pin_dev1, HIGH);

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

  setDAC(0, 4095);
  setDAC(1, 0);
  delay(200);
  setDAC(0, 0);
  setDAC(1, 4095);
  delay(200);
  setDAC(0, 0);
  setDAC(1, 0);
}

void loop() {
  delay(1);
  readSensors();
}


/*
Called when serial data available after each loop()
 Requires use of non-blocking timings for opening outputs,
 otherwise delayed and buffers might fill up
 */
void serialEvent() {
  while (Serial.available()) {
    n = 0;
    while (n < 4) {
      // get the new byte:
      tmp = Serial.read();
      if (tmp > -1) {
        inBytes[n] = tmp;
        n++;
      }
    }
    interpretCommand();
  }
}

/*
Interpret the received byte array by splitting it into a command, followed
 by payload data used in its execution
 */
void interpretCommand() {
  if (inBytes[3] == '\n') {
    inCommand = inBytes[0];
    inData = inBytes[1] + (inBytes[2]<<8);

    Serial.println(readSensors());
//    Serial.println(inCommand);
//    Serial.println(inData);

    if (inCommand == 48) {
      setDAC(0, inData);
    } 
    else if (inCommand == 49) {
      setDAC(1, inData);
    } 
    else if (inCommand == 40) {
      setDigital(40, inData);
    } 
    else if (inCommand == 41) {
      setDigital(41, inData);
    } 
    else if (inCommand == 42) {
      setDigital(42, inData);
    } 
    else if (inCommand == 43) {
      setDigital(43, inData);
    }

    //    else if (inCommand == 39) {
    //      Serial.println('Hello Spotter!');
    //    }
  } 
}


void setDAC(byte device, int outputValue) {
  // should set select chip
  if (device == 0 ) {
    digitalWrite(pin_dev0, LOW);
  } 
  else if (device == 1) {
    digitalWrite(pin_dev1, LOW);
  }

  data = highByte(outputValue);
  data = 0b00001111 & data;
  data = 0b00110000 | data;
  SPI.transfer(data);
  data = lowByte(outputValue);
  SPI.transfer(data);

  digitalWrite(pin_dev0, HIGH);
  digitalWrite(pin_dev1, HIGH);
}

/* 
 Read digital pins, e.g. sensors
 Loop through digital pins, return
 byte whose LSB bits represent the state of 
 a specific pin.
 */
byte readSensors() {
  return 0x00;
}


/*
 Set digital pins to the value of their specific bit
 in the received state byte
 */
void setDigital(byte pin, short data) {
  if (data > 0) {
    digitalWrite(pin, HIGH);
  } 
  else {
    digitalWrite(pin, LOW);  
  }
}


