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
 * sampling_rate: calculated sampling rate
 * sample_count: counter for samples to calculate sampling rate
 * last_time: timestamp for sampling rate calculation
 */

long instance1=0, timer;
double hrv =0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;
#define shutdown_pin 10 
#define threshold 100 // to identify R peak
#define timer_value 10000 // 10 seconds timer to calculate hr

// Butterworth filter variables
float xv[3] = {0,0,0}; // input buffer
float yv[3] = {0,0,0}; // output buffer

// Sampling rate calculation variables
unsigned int sample_count = 0;
unsigned long last_time = 0;
float sampling_rate = 0;

void setup() {
  Serial.begin(115200); // Increased baud rate for more data
  pinMode(8, INPUT); // Setup for leads off detection LO +
  pinMode(9, INPUT); // Setup for leads off detection LO -
  pinMode(shutdown_pin, OUTPUT);
  digitalWrite(shutdown_pin, HIGH); //normal mode initially
  last_time = millis();
}

// 2nd order Butterworth low-pass filter, cutoff freq = 30 Hz, fs = 200Hz
int butterworthFilter(int input) {
  xv[2] = xv[1];
  xv[1] = xv[0];
  xv[0] = (float)input;
  
  yv[2] = yv[1];
  yv[1] = yv[0];
  
  // Butterworth coefficients for fs=200Hz, fc=30Hz
  yv[0] = (xv[0] + 2*xv[1] + xv[2] - yv[2] + 2*yv[1]) / 1.5675;
  
  return (int)yv[0];
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
    value = map(value, 250, 400, 0, 100); //to flatten the ecg values a bit
    
    // Apply Butterworth filter
    value = butterworthFilter(value);
    
    // Calculate sampling rate
    sample_count++;
    if (millis() - last_time >= 1000) {
      sampling_rate = (float)sample_count / ((millis() - last_time) / 1000.0);
      sample_count = 0;
      last_time = millis();
    }
    
    if((value > threshold) && (!flag)) {
      count++;  
      Serial.println("R peak detected");
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
    
    // Print data with sampling rate
    Serial.print("HR:");
    Serial.print(hr);
    Serial.print(",HRV:");
    Serial.print(hrv);
    Serial.print(",ECG:");
    Serial.print(value);
    Serial.print(",SR:");
    Serial.print(sampling_rate, 1);
    Serial.println(" Hz");
    
    delay(5); // Changed to 5ms delay for ~200Hz sampling rate
  }
}

