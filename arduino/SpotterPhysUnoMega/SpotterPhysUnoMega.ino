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

//#define DEBUG
#define DAC_TEST_DELAY 20
#define DACMAX 4095

#ifdef DEBUG
  #define DEBUGLN(x)  Serial.println(x)
  #define DEBUG(x)  Serial.print(x)
#else
  #define DEBUGLN(x)
  #define DEBUG(x)
#endif

#include "SPI.h" // handles SPI communication to MCP4921 DAC

#if defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
  // SPI pins
  #define pin_SCK 52
  #define pin_MOSI 51
  #define pin_MISO 50
  // SPI clients
  #define SPI_N_DEVS 2 // number of SPI clients
  byte SPI_pins[SPI_N_DEVS] = {48, 49};
  // digital input pins
  #define DIN_N 4
  byte DIN_pins[DIN_N] = {30, 31, 32, 33};
  // digital output pins
  #define DOUT_N 4
  byte DOUT_pins[DOUT_N] = {40, 41, 42, 43};
#elif defined(__AVR_ATmega168__) || defined(__AVR_ATmega328P__)
  // SPI pins
  #define pin_SCK 13
  #define pin_MOSI 11
  #define pin_MISO 12
  // SPI clients
  #define SPI_N_DEVS 2 // number of SPI clients
  byte SPI_pins[SPI_N_DEVS] = {6, 7};
  // digital input pins
  #define DIN_N 2
  byte DIN_pins[DIN_N] = {8, 9};
  // digital output pins
  #define DOUT_N 4
  byte DOUT_pins[DOUT_N] = {2, 3, 4, 5};
#endif

#define CMDADDR 0x07 // bits 1-3
#define CMDTYPE 0x38 // bits 4-6
#define CMDMSBB 0xC0 // bits 7-8

#define TYPE_UTILITY 0x00
#define TYPE_SPI_DAC 0x01
#define TYPE_DIGITAL 0x02

int inData = 0;
byte outData = 0;

int tmp = 0x00;
byte inBytes[4];

byte data = 0x00;
//byte n = 0;


/* 
 Transfer 4 command bits and 12 data bits
 via SPI to the DACs
 */
void setDAC(byte pin_idx, int outputValue) {
  // check if device index in range
  if (pin_idx >= SPI_N_DEVS) {
    return;
  }
  byte pin = SPI_pins[pin_idx];
  // select SPI device
  digitalWrite(pin, LOW);
  // command bits and 4 MSB data bits
  data = highByte(outputValue);
  data = 0b00001111 & data;
  data = 0b00110000 | data;
  SPI.transfer(data);
  // last 8 LSB data bits
  data = lowByte(outputValue);
  SPI.transfer(data);
  // deselect SPI device
  digitalWrite(pin, HIGH);
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
void setDigital(byte pin_idx, short outputValue) {
  // check if device index in range
  if (pin_idx >= DOUT_N) {
    return;
  }
  byte pin = DOUT_pins[pin_idx];
  if (outputValue > 0) {
    digitalWrite(pin, HIGH);
  } 
  else {
    digitalWrite(pin, LOW);  
  }
}


/*
Report arduino capabilities to Spotter. I.e. give number
 of analog out, digital out pins.
 */
void report(byte request, short inputValue) {
  switch (request) {
    case 0x00:
      Serial.println(inputValue, DEC);
      break;
    case 0x01:
      Serial.println(SPI_N_DEVS, DEC);
      break;
    case 0x02:
      Serial.println(DOUT_N, DEC);
      break;
  }
}


/*
Interpret the received byte array by splitting it into a command, followed
 by payload data used in its execution
 */
void interpretCommand() {
  if (inBytes[3] != '\n') {
    return;
  }
  inData = (inBytes[2]<<8) + inBytes[1];
  if (inData > DACMAX) {
    inData = DACMAX;
  }
  byte addr = (CMDADDR & inBytes[0]);
  byte type = (CMDTYPE & inBytes[0]) >> 3;
  DEBUGLN(type);
  DEBUGLN(addr);
  DEBUGLN(inData);

  switch (type) {
  case TYPE_UTILITY: 
    report(addr, inData);
    break;
  case TYPE_SPI_DAC:
  //////////////// TO GO BACK TO THE DAC SIGNAL, COMMENT THE LINES WITH //////s
  for (byte i=0; i<3; i++) { ////////////////
      setDAC(addr, inData);
      delay(1);////////////////
      setDAC(addr, 0);////////////////
      delay(1);////////////////
    }////////////////
    break;
  case TYPE_DIGITAL:
    setDigital(addr, inData);
    break;
  }
//  Serial.println(readSensors());
}


void setup(){
  // initialize serial connection
  Serial.begin(57600);

  // ready SPI to talk to DAC
  for (byte i = 0; i < SPI_N_DEVS; i++) {
    pinMode(SPI_pins[i], OUTPUT);
    digitalWrite(SPI_pins[i], HIGH);
  }
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);

  // DAC test pulses
  for (byte i = 0; i < SPI_N_DEVS; i++) {
    setDAC(i, DACMAX);
    delay(DAC_TEST_DELAY);
    setDAC(i, 0);
  }

  // ready ditital output pins
  for (byte i = 0; i < DOUT_N; i++) {
    pinMode(DOUT_pins[i], OUTPUT);
    digitalWrite(DOUT_pins[i], LOW);
  }

  // ready digital input pins
  for (byte i = 0; i < DIN_N; i++) {
    pinMode(DIN_pins[i], INPUT);
  }
}

/*
Called when serial data available after each loop()
 Requires use of non-blocking timings for opening outputs,
 otherwise delayed and buffers might fill up
 
 Current protocol is defined as one command byte, followed
 by two data bytes and closed with a newline.
 */
void serialEvent() {
  while (Serial.available()) {
    byte n = 0;
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


void loop() {
  delay(1);
}

