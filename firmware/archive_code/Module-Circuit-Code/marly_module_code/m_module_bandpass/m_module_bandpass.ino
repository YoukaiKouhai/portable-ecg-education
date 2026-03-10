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
 * sampling_rate: calculated actual sampling rate
 * last_sample_time: timestamp of last sample for rate calculation
 * sample_count: counter for sampling rate calculation
 */
long instance1=0, timer, last_sample_time = 0;
double hrv =0, hr = 72, interval = 0;
int value = 0, count = 0;
float sampling_rate = 0;
int sample_count = 0;
bool flag = 0;
#define shutdown_pin 10 
#define threshold 100 // to identify R peak
#define timer_value 10000 // 10 seconds timer to calculate hr

// Bandpass filter variables (0.5Hz - 40Hz)
float xv[3] = {0,0,0}, yv[3] = {0,0,0};

void setup() {
  Serial.begin(115200);  // Increased baud rate for better sampling
  pinMode(8, INPUT); // Setup for leads off detection LO +
  pinMode(9, INPUT); // Setup for leads off detection LO -
  pinMode(shutdown_pin, OUTPUT);
  digitalWrite(shutdown_pin, HIGH);
  last_sample_time = micros();
}

void loop() { 
  if((digitalRead(8) == 1)||(digitalRead(9) == 1)){
    Serial.println("leads off!");
    digitalWrite(shutdown_pin, LOW); //standby mode
    instance1 = micros();
    timer = millis();
    delay(100);
  }
  else {
    digitalWrite(shutdown_pin, HIGH); //normal mode
    
    // Calculate sampling rate
    sample_count++;
    if (micros() - last_sample_time >= 1000000) { // Every second
      sampling_rate = sample_count;
      sample_count = 0;
      last_sample_time = micros();
    }
    
    value = analogRead(A0);
    
    // Bandpass filter implementation
    xv[0] = xv[1];
    xv[1] = xv[2];
    xv[2] = value / 1023.0;  // Normalize to 0-1
    
    yv[0] = yv[1];
    yv[1] = yv[2];
    yv[2] = (xv[2] - xv[0]) * 0.1124 + (yv[0] - yv[1]) * 1.6754 + yv[1] * -0.7532;
    
    // Scale filtered signal back to ADC range and apply mapping
    value = (int)(yv[2] * 100) + 325;  // Center the signal
    value = constrain(value, 0, 1023);
    value = map(value, 250, 400, 0, 100); //to flatten the ecg values a bit
    
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
    Serial.println(sampling_rate);
    delay(1);
  }
}

