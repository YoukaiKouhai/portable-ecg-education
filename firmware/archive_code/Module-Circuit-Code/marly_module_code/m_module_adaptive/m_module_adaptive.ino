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

// Adaptive filter variables
#define FILTER_ORDER 4
#define MU 0.001  // Step size for LMS algorithm
float weights[FILTER_ORDER] = {0};
float delayed_signal[FILTER_ORDER] = {0};
float filtered_value = 0;

long instance1=0, timer;
double hrv =0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;
#define shutdown_pin 10 
#define threshold 100 // to identify R peak
#define timer_value 10000 // 10 seconds timer to calculate hr

// Sampling rate measurement variables
unsigned long last_sample_time = 0;
float sampling_rate = 0;
unsigned int sample_count = 0;
unsigned long rate_timer = 0;

void setup() {
  Serial.begin(115200);  // Increased baud rate for better sampling
  pinMode(8, INPUT); // Setup for leads off detection LO +
  pinMode(9, INPUT); // Setup for leads off detection LO -
  pinMode(shutdown_pin, OUTPUT);
  digitalWrite(shutdown_pin, HIGH);
  last_sample_time = micros();
  rate_timer = millis();
}

// Adaptive LMS filter function
float adaptive_lms_filter(int input) {
  // Shift delayed signals
  for(int i = FILTER_ORDER - 1; i > 0; i--) {
    delayed_signal[i] = delayed_signal[i-1];
  }
  delayed_signal[0] = input;
  
  // Calculate filtered output
  float output = 0;
  for(int i = 0; i < FILTER_ORDER; i++) {
    output += weights[i] * delayed_signal[i];
  }
  
  // Desired signal is the current input (adaptive noise cancellation)
  float error = input - output;
  
  // Update weights using LMS algorithm
  for(int i = 0; i < FILTER_ORDER; i++) {
    weights[i] += 2 * MU * error * delayed_signal[i];
  }
  
  return output;
}

void loop() { 
  if((digitalRead(8) == 1)||(digitalRead(9) == 1)){
    Serial.println("leads off!");
    digitalWrite(shutdown_pin, LOW); //standby mode
    instance1 = micros();
    timer = millis();
  }
  else {
    digitalWrite(shutdown_pin, HIGH); //normal mode
    value = analogRead(A0);
    
    // Apply adaptive filter
    filtered_value = adaptive_lms_filter(value);
    
    value = map(filtered_value, 250, 400, 0, 100); //to flatten the ecg values a bit
    
    // Calculate sampling rate every 5 seconds
    if (millis() - rate_timer > 5000) {
      sampling_rate = (float)sample_count / 5.0;
      sample_count = 0;
      rate_timer = millis();
    }
    sample_count++;
    
    if((value > threshold) && (!flag)) {
      count++;  
      Serial.println("in");
      flag = 1;
      interval = micros() - instance1; //RR interval
      instance1 = micros(); 
    }
    else if((value < threshold)) {
      flag = 0;
    }
    if ((millis() - timer) > 10000) {
      hr = count*6;
      timer = millis();
      count = 0; 
    }
    hrv = hr/60 - interval/1000000;
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.print(value);
    Serial.print(",");
    Serial.print(sampling_rate, 1);  // Display sampling rate with 1 decimal
    Serial.print(" Hz");
    Serial.println();
    delay(1);
  }
}

