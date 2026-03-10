/*
 * BENG Senior Design: ECG with Kalman Filter
 * This version uses a recursive Kalman estimator to strip away random Gaussian noise.
 */

// Kalman Variables
float Q = 0.1;      // Process noise covariance (How much we trust our model)
float R = 20;       // Measurement noise covariance (How much we trust the sensor - increase for more smoothing)
float P = 1.0;      // Estimation error covariance
float K = 0.0;      // Kalman Gain
float X_hat = 0.0;  // The filtered "estimated" signal

long instance1 = 0, timer;
double hrv = 0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;

#define shutdown_pin 10 
#define threshold 350     // Adjusted for typical AD8232 output ranges
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

    // 2. Kalman Filter Implementation
    // Step 2a: Prediction Update (Predict the future state)
    P = P + Q;

    // Step 2b: Measurement Update (Correct the prediction)
    K = P / (P + R);                     // Calculate Kalman Gain
    X_hat = X_hat + K * (raw - X_hat);   // Update the estimate with sensor data
    P = (1 - K) * P;                     // Update error covariance

    // 3. Assign filtered estimate to 'value' for peak detection
    value = (int)X_hat;

    // 4. R-Peak Detection Logic
    if((value > threshold) && (!flag)) {
      count++;  
      flag = 1;
      interval = micros() - instance1; 
      instance1 = micros(); 
    }
    else if(value < threshold) {
      flag = 0;
    }

    // 5. Calculate Heart Rate every 10 seconds
    if ((millis() - timer) > timer_value) {
      hr = count * 6;
      timer = millis();
      count = 0; 
    }

    // 6. Calculate HRV
    hrv = (hr / 60.0) - (interval / 1000000.0);

    // 7. Output: HR, HRV, and the smooth Kalman Signal
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.println(value);

    delay(2); // 500Hz sampling is great for Kalman stability
  }
}