// Install the library Adafruit_MCP4725

void setup() {
    Serial.begin(115200);
}

int value = -1;

void loop() {
    int r = Serial.read();

    // Same value is recieved 2 times
    // in a row (to ensure no corruption)
    if(value == r) {
        // Send value to rio
        
    }
    value = r;
}
