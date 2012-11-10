/*
  Created on Fri Nov 09 21:06:21 2012
  @author: <Ronny Eichler> ronny.eichler@gmail.com
  
  Video2phys translator for Spotter.Funker
  
  Hacked together  based on information from:
    Serial Event example by Tom Igoe
      http://www.arduino.cc/en/Tutorial/SerialEvent
   
    SPI tutorial, for MCP4921 by John Boxall, Chapter 36.2 at
      http://tronixstuff.com/tutorials
 
  Translates Strings received via Serial port to digital or
  analog output corresponding to the detection or position of
  a tracked object, or crossing/occupancy of region of interest.
  
  
  TODO: Make pins arrays for simplicity
        pin_SS better different pin, to allow more than one SPI device!
            --> device array!
 */

#include "SPI.h" // handles SPI communication to MCP4921 DAC

#define pin_SCK 52
#define pin_SS 53
#define pin_MOSI 51
#define pin_MISO 50

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


// Serial Communication
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
char charBuffer[16];

// DAC translation
word outputValue = 0; // 16 bit, 12 bit DAC
byte data = 0;
int value = 0;

void setup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve bytes for the inputString:
  inputString.reserve(16);
  
  // ready SPI to talk to DAC
  pinMode(pin_SS, OUTPUT);
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
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
//    value = value + 1024;
//    if (value-1 > 4095) {
//      value = 0;
//    }
    value = inputString.toInt();
    setDAC(0, value); 
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
 
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    if (inChar == '\n') {
      stringComplete = true;
      //Serial.println(inputString.toInt());
    } else {
      inputString += inChar;
    }
  }
}

void setDAC(int device, int outputValue) {
    // should set device!
    digitalWrite(pin_SS, LOW);
    data = highByte(outputValue);
    data = 0b00001111 & data;
    data = 0b00110000 | data;
    SPI.transfer(data);
    data = lowByte(outputValue);
    SPI.transfer(data);
    digitalWrite(pin_SS, HIGH);
}


