#include <Arduino_RouterBridge.h>

// PMS7003 uses UART. On this board, we use Serial1.
// Connect Sensor TX to Board RX (D0) and Sensor RX to Board TX (D1).
#define pmsSerial Serial1

struct pms7003data {
  uint16_t pm25_standard;
};

pms7003data data;

void setup() {
    // 1. Start the hardware bridge to Linux
    Bridge.begin();
    
    // 2. Start Serial for the PMS7003 (standard baud rate is 9600)
    pmsSerial.begin(9600);
    
    // 3. Register the function for the Linux side to call
    Bridge.provide("read_pm25", read_pm25);
}

void loop() {
    // Keep the bridge updated to handle incoming requests from Linux
    Bridge.update();
}

// Function to parse the PMS7003 packet
int read_pm25() {
    if (pmsSerial.available()) {
        uint8_t buffer[32];
        if (pmsSerial.read() != 0x42) return -1; // Start byte 1
        if (pmsSerial.read() != 0x4D) return -1; // Start byte 2
        
        pmsSerial.readBytes(buffer, 30);
        
        // PM2.5 standard concentration is at bytes 6 and 7 of the payload
        data.pm25_standard = (buffer[4] << 8) | buffer[5];
        return data.pm25_standard;
    }
    return -2; // No data available yet
}