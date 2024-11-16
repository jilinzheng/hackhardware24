#include <ArduinoBLE.h>
#include "Arduino_H7_Video.h"
#include "ArduinoGraphics.h"
#include <async.h>

Async asyncEngine = Async();       // Allocate on Stack

Arduino_H7_Video Display(800, 480, GigaDisplayShield);

#define MAX_CONNECTIONS 2  // Adjust this based on how many servers you want to connect to
#define SERVICE_UUID "181A"
#define CHARACTERISTIC_UUID "2A6E"

BLEDevice connectedDevices[MAX_CONNECTIONS];  // Array to store connected devices
int connectionCount = 0;  // Track number of active connections

void setup() {
  Serial.println("INITAIATING BLE CENTRAL");
  Serial.begin(9600);
  while(!Serial);

  Display.begin();
  Display.clear();
 
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  Serial.println("SCANNING FOR SERVICE UUID")
  BLE.scanForUuid("181A"); 
}

void loop() {
  asyncEngine.run();
  short id = asyncEngine.setInterval(readPeripherals, 3); // asynchrnously read data

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


void readPeripherals() {
  // use millis to execute nonblocking code
  static unsigned long start = millis();

  if((millis() - start) >= 10 && (millis() - start) < 100) {
    for (int i = 0; i < connectionCount; i++) {
      if (connectedDevices[i]) {
        connectedDevices[i].discoverAttributes();
        BLEService service = connectedDevices[i].service("181A");
        Serial.print("Service ");
        Serial.print(service.uuid());
        BLECharacteristic characteristic = service.characteristic("2A6E");
        readCharacteristicValue(characteristic);
      }
    }
  }

  if((millis() - start) >= 100) {  // reset millis
    start = millis();
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

void readCharacteristicValue(BLECharacteristic characteristic) {
  Serial.print("\tCharacteristic ");
  Serial.print(characteristic.uuid());
  if (characteristic.canRead()) {
    int16_t value = 0;
    characteristic.readValue(&value, 2);
    Serial.print(", value = ");
    Serial.println((float) value);
  }
}

void displayText(char* text){
  Display.beginDraw();
  Display.textFont(Font_5x7);
  Display.stroke(255, 255, 255);
  Display.text("Hello world!", 50, 50);
  Display.endDraw();
}