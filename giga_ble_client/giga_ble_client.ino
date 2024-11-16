#include <ArduinoBLE.h>
#include "Arduino_H7_Video.h"
#include "ArduinoGraphics.h"
#include <async.h>

#define MAX_CONNECTIONS 2  // Adjust this based on how many servers you want to connect to
#define SERVICE_UUID "181A"
#define CHARACTERISTIC_UUID "2A6E"

Async asyncEngine = Async();       // Allocate on Stack
Arduino_H7_Video Display(800, 480, GigaDisplayShield);
BLEDevice connectedDevices[MAX_CONNECTIONS];  // Array to store connected devices
int connectionCount = 0;  // Track number of active connections
byte controllerOneData[50], controllerTwoData[50];


void setup() {
  Serial.println("INITAIATING BLE CENTRAL");
  Serial.begin(9600);
  while(!Serial);

  Display.begin();
  Display.clear();
 
  if (!BLE.begin()) {
    Serial.println("STARTING BLE FAILED!");
    while (1);
  }

  Serial.println("SCANNING FOR SERVICE UUID");
  BLE.scanForUuid("181A");
}


void loop() {
  asyncEngine.run();
  short id = asyncEngine.setInterval(readPeripherals, 10); // asynchronously read data

  if (connectionCount < MAX_CONNECTIONS){
    BLEDevice peripheral = BLE.available();               // check if a peripheral has been discovered
  
    if (peripheral) {
      printPeripheralInfo(peripheral);                    // print peripheral info
      if (peripheral.connect()){                          // connect to peripheral
        Serial.println("Connected!");
        connectedDevices[connectionCount] = peripheral;   // and store peripheral in global array
        connectionCount++;
      }
    }
  }
}


void printPeripheralInfo(BLEDevice peripheral){
  Serial.println("Discovered a peripheral");
  Serial.println("-----------------------");
  Serial.print("Address: ");
  Serial.println(peripheral.address());
  if (peripheral.hasLocalName()) {
    Serial.print("Local Name: ");
    Serial.println(peripheral.localName());
  }
  if (peripheral.hasAdvertisedServiceUuid()) {
    Serial.print("Service UUIDs: ");
    for (int i = 0; i < peripheral.advertisedServiceUuidCount(); i++) {
      Serial.print(peripheral.advertisedServiceUuid(i));
      Serial.print(" ");
    }
    Serial.println();
  }
  Serial.print("RSSI: ");
  Serial.println(peripheral.rssi());
  Serial.println();
}


void readPeripherals() {
  // use millis to execute nonblocking code
  static unsigned long start = millis();

  if((millis() - start) >= 10 && (millis() - start) < 1000) {
    for (int i = 0; i < connectionCount; i++) {
      if (connectedDevices[i]) {
        connectedDevices[i].discoverAttributes();
        Serial.print(connectedDevices[i].localName());
        Serial.print(" ");
        BLEService service = connectedDevices[i].service("181A");
        Serial.print("Service ");
        Serial.print(service.uuid());
        BLECharacteristic characteristic = service.characteristic("2A6E");
        Serial.print("; Characteristic ");
        Serial.print(characteristic.uuid());
        if (characteristic.canRead()) {
          if (connectedDevices[i].localName() == "TEAM 1 CONTROLLER 1") {
            // characteristic.readValue(&controllerOneData, 2);
            int len = characteristic.readValue(controllerOneData, sizeof(controllerOneData));
            if (len > 0) {
              // Convert byte array to null-terminated string
              controllerOneData[len] = '\0';  
              String utf8String = String((char*)controllerOneData);

              // Print received string
              Serial.print("Received String: ");
              Serial.println(utf8String);

              // Parse and convert numerical portions from the string
              parseAndConvertToFloat(utf8String);
            }
            // Serial.print("; value = ");
            // Serial.println((float) controllerOneData);
            // displayText("test1", i*50+50, i*50+50);
          } else {
            int len = characteristic.readValue(&controllerTwoData, 2);
            if (len > 0) {
              // Convert byte array to null-terminated string
              controllerTwoData[len] = '\0';  
              String utf8String = String((char*)controllerTwoData);

              // Print received string
              Serial.print("Received String: ");
              Serial.println(utf8String);

              // Parse and convert numerical portions from the string
              parseAndConvertToFloat(utf8String);
            }
            // Serial.print("; value = ");
            // Serial.println((float) controllerTwoData);
            // displayText("test2", i*50+50, i*50+50);
          }
        }
      }
    }
  }
  else if ((millis() - start) >= 1000) {  // reset millis
    start = millis();
  }
}


// Function to parse received string by whitespace and convert numerical portions to float
void parseAndConvertToFloat(String input) {
  char buffer[100];
  
  // Copy String object to char array for strtok usage
  input.toCharArray(buffer, sizeof(buffer));

  char* token = strtok(buffer, " ");  // Split by spaces

  while (token != NULL) {
    Serial.print("Token: ");
    Serial.println(token);

    // Check if token is a number and convert it to float using atof()
    float num = atof(token);  
    if (num != 0 || strcmp(token, "0") == 0) {   // atof returns 0 for non-numeric tokens, so check for "0"
      Serial.print("Converted Float: ");
      Serial.println(num);
    }

    token = strtok(NULL, " ");   // Get next token
  }
}


void displayText(char* text, int x, int y){
  Display.beginDraw();
  Display.textFont(Font_5x7);
  Display.stroke(255, 255, 255);
  Display.text(text, x, y);
  Display.endDraw();
}