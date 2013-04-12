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

// DAC pins
#define DAC_N 2
byte DAC_pins[DAC_N] = {DAC0, DAC1};

// digital input pins
#define DIN_N 2
byte DIN_pins[DIN_N] = {8, 9};
// digital output pins
#define DOUT_N 4
byte DOUT_pins[DOUT_N] = {2, 3, 4, 5};

#define CMDADDR 0x07 // bits 1-3
#define CMDTYPE 0x38 // bits 4-6
#define CMDMSBB 0xC0 // bits 7-8

#define TYPE_UTILITY 0x00
#define TYPE_DAC 0x01
#define TYPE_DIGITAL 0x02

int inData = 0;
byte outData = 0;
byte data = 0x00;

int tmp = 0x00;
byte inBytes[4];

/* 
 Analog write on Arduino Due's DAC0 and DAC1
 */
void setDAC(byte pin_idx, int outputValue) {
  // check if device index in range
  if (pin_idx >= DAC_N) {
    return;
  }
  byte pin = DAC_pins[pin_idx];
  analogWrite(pin, outputValue);
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
      Serial.println(DAC_N, DEC);
      break;
    case 0x02:
      Serial.println(DOUT_N, DEC);
      break;
    case 0x03:
      Serial.println(DIN_N, DEC);
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
  case TYPE_DAC:
    setDAC(addr, inData);
    break;
  case TYPE_DIGITAL:
    setDigital(addr, inData);
    break;
  }
}


void setup(){
  analogWriteResolution(12);
  // ready SPI to talk to DAC
  for (byte i = 0; i < DAC_N; i++) {
    pinMode(DAC_pins[i], OUTPUT);
    setDAC(i, 0);
  }

  // DAC test pulses
  for (byte i = 0; i < DAC_N; i++) {
    setDAC(i, DACMAX);
    delay(DAC_TEST_DELAY);
    setDAC(i, 0);
  }

  // initialize serial connection
  Serial.begin(57600);

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
void serialRcvEvent() {
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
  if (Serial.available()) {
    serialRcvEvent();
  }
  //delay(1);
}

