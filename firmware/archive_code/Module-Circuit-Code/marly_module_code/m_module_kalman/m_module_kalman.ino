/*
 * VARIABLES
 * count: variable to hold count of rr peaks detected in 10 seconds
 * flag: variable that prevents multiple rr peak detections in a single heatbeat
 * hr: HeartRate (initialised to 72)
 * hrv: Heart Rate variability (takes 10-15 seconds to stabilise)
 * instance1: instance when heart beat first time
 * interval: interval between second beat and first beat
 * timer: variable to hold the time after which hr is calculated
 * value: raw sensor value of output pin
 */
long instance1=0, timer;
double hrv =0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;
#define shutdown_pin 10 
#define threshold 100 // to identify R peak
#define timer_value 10000 // 10 seconds timer to calculate hr

// Kalman filter variables
float Q = 0.01;  // Process noise covariance (adjust for smoothness vs response)
float R = 0.1;   // Measurement noise covariance (adjust based on sensor noise)
float P = 1.0;   // Estimation error covariance
float K = 0.0;   // Kalman gain
float X = 0.0;   // Filtered value
float filtered_value = 0;  // Kalman filtered output

// Sampling rate measurement
unsigned long last_sample_time = 0;
unsigned long sample_interval = 0;
float sampling_rate = 0;
int sample_count = 0;
unsigned long rate_timer = 0;

void setup() {
  Serial.begin(115200);  // Increased baud rate for better data transmission
  pinMode(8, INPUT); // Setup for leads off detection LO +
  pinMode(9, INPUT); // Setup for leads off detection LO -
  pinMode(shutdown_pin, OUTPUT);
  digitalWrite(shutdown_pin, HIGH);
  last_sample_time = micros();
  rate_timer = millis();
}

float kalman_filter(float new_value) {
  // Prediction update
  P = P + Q;
  
  // Measurement update
  K = P / (P + R);
  X = X + K * (new_value - X);
  P = (1 - K) * P;
  
  return X;
}

void loop() { 
  if((digitalRead(8) == 1)||(digitalRead(9) == 1)){
    Serial.println("leads off!");
    digitalWrite(shutdown_pin, LOW); //standby mode
    instance1 = micros();
    timer = millis();
    // Reset Kalman filter when leads off
    P = 1.0;
    X = 0.0;
  }
  else {
    digitalWrite(shutdown_pin, HIGH); //normal mode
    
    // Calculate sampling rate
    sample_count++;
    if ((millis() - rate_timer) >= 1000) {
      sampling_rate = (float)sample_count;
      sample_count = 0;
      rate_timer = millis();
    }
    
    value = analogRead(A0);
    value = map(value, 250, 400, 0, 100); //to flatten the ecg values a bit
    
    // Apply Kalman filter
    filtered_value = kalman_filter(value);
    
    if((filtered_value > threshold) && (!flag)) {
      count++;  
      Serial.println("in");
      flag = 1;
      interval = micros() - instance1; //RR interval
      instance1 = micros(); 
    }
    else if((filtered_value < threshold)) {
      flag = 0;
    }
    
    if ((millis() - timer) > 10000) {
      hr = count*6;
      timer = millis();
      count = 0; 
    }
    
    hrv = hr/60 - interval/1000000;
    
    // Output filtered value instead of raw value
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.print(filtered_value);
    Serial.print(",");
    Serial.println(sampling_rate, 0);  // Add sampling rate to output
    
    delay(1);
  }
}

