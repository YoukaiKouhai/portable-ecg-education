/*
 * BENG Senior Design: ECG with Adaptive LMS Filter
 * The filter "learns" the signal trend and adapts its weights (w) 
 * to minimize noise in real-time.
 */

// Adaptive Filter Variables
float mu = 0.01;    // Learning rate (Convergence speed)
float w = 0.5;      // Initial Filter weight
float x_delay = 0;  // Previous input sample (Reference)

long instance1 = 0, timer;
double hrv = 0, hr = 72, interval = 0;
int value = 0, count = 0;  
bool flag = 0;

#define shutdown_pin 10 
#define threshold 400     // Adjust based on your circuit's R-peak height
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

    // 2. Adaptive Filtering (LMS Algorithm)
    // Predict the current value based on the previous sample and current weight
    float prediction = w * x_delay;
    
    // Calculate the estimation error
    float error = (float)raw - prediction;
    
    // Update the weight (w) using the LMS update rule
    // w(n+1) = w(n) + mu * error(n) * x(n-1)
    w = w + mu * error * x_delay; 
    
    // Store the current raw value as the 'delay' for the next loop
    x_delay = (float)raw;

    // 3. Assign the 'prediction' or 'error' as the output
    // In this mode, the 'prediction' acts as a smoothed version of the signal
    value = (int)prediction;

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

    // 7. Output: HR, HRV, and Filtered Signal
    Serial.print(hr);
    Serial.print(",");
    Serial.print(hrv);
    Serial.print(",");
    Serial.println(value);

    delay(2); // 500Hz sampling
  }
}