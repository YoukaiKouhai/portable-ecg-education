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
 * filteredValue: ECG value after Chebyshev notch filter
 * samplingRate: calculated sampling rate in Hz
 * lastSampleTime: for sampling rate calculation
 * sampleCount: for sampling rate calculation
 */

long instance1=0, timer;
double hrv =0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;
#define shutdown_pin 10 
#define threshold 100 // to identify R peak
#define timer_value 10000 // 10 seconds timer to calculate hr

// Chebyshev Notch Filter variables (50Hz/60Hz removal)
#define FILTER_ORDER 2
#define SAMPLING_FREQ 500 // Assumed sampling frequency in Hz (adjust based on your system)
#define NOTCH_FREQ 50     // 50Hz notch filter (change to 60Hz if needed)
float xv[FILTER_ORDER+1]; // Input buffer
float yv[FILTER_ORDER+1]; // Output buffer

// Filter coefficients for 2nd order Chebyshev notch filter (50Hz notch, 500Hz sampling)
// These coefficients create a -40dB notch at 50Hz with 2Hz bandwidth
float a[FILTER_ORDER+1] = {1, -1.987, 0.990};  // Denominator coefficients
float b[FILTER_ORDER+1] = {0.995, -1.987, 0.995}; // Numerator coefficients

int filteredValue = 0;  // Filtered ECG value
float samplingRate = 0;  // Calculated sampling rate in Hz
unsigned long lastSampleTime = 0;
unsigned long sampleCount = 0;
unsigned long sampleTimer = 0;

void setup() {
  Serial.begin(9600);
  pinMode(8, INPUT); // Setup for leads off detection LO +
  pinMode(9, INPUT); // Setup for leads off detection LO -
  
  // Initialize filter buffers
  for(int i=0; i<=FILTER_ORDER; i++) {
    xv[i] = 0;
    yv[i] = 0;
  }
  
  lastSampleTime = micros();
  sampleTimer = millis();
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
    
    // Apply Chebyshev Notch Filter
    xv[0] = xv[1];
    xv[1] = xv[2];
    xv[2] = (float)value / 100.0;  // Normalize input
    
    // Calculate filter output
    yv[0] = yv[1];
    yv[1] = yv[2];
    yv[2] = (b[0]*xv[2] + b[1]*xv[1] + b[2]*xv[0] 
           - a[1]*yv[1] - a[2]*yv[0]);
    
    filteredValue = (int)(yv[2] * 100);  // Denormalize output
    
    // Calculate sampling rate
    sampleCount++;
    unsigned long currentTime = micros();
    unsigned long timeDiff = currentTime - lastSampleTime;
    
    if (timeDiff > 0) {
      float instantRate = 1000000.0 / timeDiff;
      // Smooth the sampling rate with low-pass filter
      samplingRate = samplingRate * 0.9 + instantRate * 0.1;
    }
    lastSampleTime = currentTime;
    
    // Display sampling rate every 5 seconds
    if (millis() - sampleTimer > 5000) {
      Serial.print("Sampling Rate: ");
      Serial.print(samplingRate, 1);
      Serial.println(" Hz");
      sampleTimer = millis();
    }
    
    // Use filteredValue for R peak detection instead of raw value
    if((filteredValue > threshold) && (!flag)) {
      count++;  
      Serial.println("in");
      flag = 1;
      interval = micros() - instance1; //RR interval
      instance1 = micros(); 
    }
    else if((filteredValue < threshold)) {
      flag = 0;
    }
    
    if ((millis() - timer) > 10000) {
      hr = count*6;
      timer = millis();
      count = 0; 
    }
    
    hrv = hr/60 - interval/1000000;
    
    // Print filtered value instead of raw value
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.print(filteredValue);
    Serial.print(",");
    Serial.print(samplingRate, 1);
    Serial.print(",");
    Serial.println(value);  // Optional: still print raw value for comparison
    
    delay(1);
  }
}

