// ===== BENG SENIOR DESIGN: ECG KALMAN TRACKER =====

long instance1 = 0, timer;
double hrv = 0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;

#define shutdown_pin 10 
#define threshold 100 // to identify R peak
#define timer_value 10000 

// Kalman filter variables
float Q = 0.01;  
float R = 0.1;   
float P = 1.0;   
float K = 0.0;   
float X = 0.0;   
float filtered_value = 0; 

// Sampling rate measurement
unsigned long rate_timer = 0;
int sample_count = 0;
float sampling_rate = 0;

void setup() {
  Serial.begin(115200);  
  pinMode(8, INPUT); // LO +
  pinMode(9, INPUT); // LO -
  pinMode(shutdown_pin, OUTPUT);
  digitalWrite(shutdown_pin, HIGH);
  rate_timer = millis();
}

float kalman_filter(float new_value) {
  P = P + Q;
  K = P / (P + R);
  X = X + K * (new_value - X);
  P = (1 - K) * P;
  return X;
}

void loop() { 
  if((digitalRead(8) == 1) || (digitalRead(9) == 1)){
    // Output specific values for "Leads Off" so MATLAB doesn't crash
    Serial.println("0,0,0,0"); 
    digitalWrite(shutdown_pin, LOW);
    P = 1.0; X = 0.0; // Reset Kalman
    delay(100);
    return;
  }
  
  digitalWrite(shutdown_pin, HIGH);
  
  // Calculate sampling rate
  sample_count++;
  if ((millis() - rate_timer) >= 1000) {
    sampling_rate = (float)sample_count;
    sample_count = 0;
    rate_timer = millis();
  }
  
  value = analogRead(A0);
  // Re-scale the signal for easier peak detection
  value = map(value, 250, 400, 0, 150); 
  
  filtered_value = kalman_filter(value);
  
  // R-Peak detection logic
  if((filtered_value > threshold) && (!flag)) {
    count++;  
    flag = 1;
    interval = micros() - instance1; 
    instance1 = micros(); 
  }
  else if(filtered_value < (threshold - 10)) { // Add small hysteresis
    flag = 0;
  }
  
  if ((millis() - timer) > timer_value) {
    hr = count * 6;
    timer = millis();
    count = 0; 
  }
  
  hrv = hr/60.0 - interval/1000000.0;
  
  // Send 4 columns of data to MATLAB
  Serial.print(hr);            Serial.print(",");
  Serial.print(hrv);           Serial.print(",");
  Serial.print(filtered_value); Serial.print(",");
  Serial.println(sampling_rate, 0); 
  
  delay(2); // ~500Hz
}