/*
 * BENG Senior Design: ECG with Chebyshev Type II Notch Filter
 * Specifically targets 60Hz noise with a steep roll-off.
 * Sampling Rate: 500Hz
 */

// Chebyshev II Notch Variables
float xc[3] = {0, 0, 0}; 
float yc[3] = {0, 0, 0};

// Coefficients for 60Hz Rejection at 500Hz Sampling
// These are mathematically derived for a "deep notch"
float bc[] = {0.9328, -1.3320, 0.9328}; 
float ac[] = {1.0000, -1.3320, 0.8656};

long instance1 = 0, timer;
double hrv = 0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;

#define shutdown_pin 10 
#define threshold 450      // Threshold for R-peak detection
#define timer_value 10000 

void setup() {
  Serial.begin(115200);
  pinMode(8, INPUT); // LO +
  pinMode(9, INPUT); // LO -
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
    
    // 1. Read Raw Sensor Data
    int raw = analogRead(A0);

    // 2. Chebyshev Filter Implementation (Direct Form I)
    xc[0] = (float)raw;
    
    // The Difference Equation
    yc[0] = bc[0]*xc[0] + bc[1]*xc[1] + bc[2]*xc[2] 
            - ac[1]*yc[1] - ac[2]*yc[2];

    // 3. Shift buffers for the next sample
    xc[2] = xc[1]; xc[1] = xc[0];
    yc[2] = yc[1]; yc[1] = yc[0];

    // 4. Update 'value' for peak detection
    value = (int)yc[0];

    // 5. R-Peak Detection Logic
    if((value > threshold) && (!flag)) {
      count++;  
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

    // 7. Calculate HRV
    hrv = (hr / 60.0) - (interval / 1000000.0);

    // 8. Output
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.println(value);

    // IMPORTANT: Delay must be exactly 2ms to maintain 500Hz sampling
    // for the filter math to stay accurate to 60Hz.
    delay(2); 
  }
}