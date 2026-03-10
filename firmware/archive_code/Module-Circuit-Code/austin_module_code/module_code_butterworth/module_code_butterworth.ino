/*
 * BENG Senior Design: ECG with Butterworth Bandpass (0.5Hz - 40Hz)
 * This code filters raw data before detecting R-peaks to improve HR accuracy.
 */

// Filter Variables
float x_b[5] = {0,0,0,0,0}; // Input history
float y_b[5] = {0,0,0,0,0}; // Output history

// 2nd Order Butterworth Coefficients (Fs=200Hz, Fc1=0.5Hz, Fc2=40Hz)
// Note: We use 200Hz (delay 5ms) for better stability on Arduino Uno math
float b_band[] = {0.1311, 0, -0.2622, 0, 0.1311};
float a_band[] = {1.0000, -3.1411, 3.8211, -2.1025, 0.4354};

long instance1 = 0, timer;
double hrv = 0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;

#define shutdown_pin 10 
#define threshold 60      // Adjusted for filtered signal range
#define timer_value 10000 

void setup() {
  Serial.begin(115200); // Use 115200 for faster data streaming
  pinMode(8, INPUT);    // LO +
  pinMode(9, INPUT);    // LO -
  pinMode(shutdown_pin, OUTPUT);
  timer = millis();
}

void loop() { 
  if((digitalRead(8) == 1) || (digitalRead(9) == 1)){
    Serial.println("leads off!");
    digitalWrite(shutdown_pin, LOW); 
    instance1 = micros();
    timer = millis();
  }
  else {
    digitalWrite(shutdown_pin, HIGH); 
    
    // 1. Read Raw Sensor
    int raw = analogRead(A0);

    // 2. Apply Butterworth Bandpass Filter Math (Difference Equation)
    x_b[0] = (float)raw;
    y_b[0] = b_band[0]*x_b[0] + b_band[1]*x_b[1] + b_band[2]*x_b[2] + b_band[3]*x_b[3] + b_band[4]*x_b[4]
             - a_band[1]*y_b[1] - a_band[2]*y_b[2] - a_band[3]*y_b[3] - a_band[4]*y_b[4];

    // 3. Shift Buffers for next iteration
    for(int i=4; i>0; i--) {
      x_b[i] = x_b[i-1];
      y_b[i] = y_b[i-1];
    }

    // 4. Use filtered value for peak detection
    // We add an offset (50) to keep the signal visible in positive range
    value = (int)y_b[0] + 50; 

    // 5. R-Peak Detection Logic
    if((value > threshold) && (!flag)) {
      count++;  
      // Serial.println("in"); // Commented out to keep CSV clean
      flag = 1;
      interval = micros() - instance1; 
      instance1 = micros(); 
    }
    else if(value < threshold) {
      flag = 0;
    }

    // 6. Calculate Heart Rate every 10 seconds
    if ((millis() - timer) > timer_value) {
      hr = count * 6;
      timer = millis();
      count = 0; 
    }

    // 7. Calculate HRV (Simplified difference)
    hrv = (hr/60.0) - (interval/1000000.0);

    // 8. Output to Serial Plotter (HR, HRV, Filtered_Signal)
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.println(value);

    delay(5); // 5ms delay = 200Hz sampling. Better for Butterworth math stability.
  }
}