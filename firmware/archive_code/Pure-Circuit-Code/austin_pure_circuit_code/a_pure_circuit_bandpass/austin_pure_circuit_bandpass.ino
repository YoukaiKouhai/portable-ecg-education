// ===== INTEGRATED ECG SIGNAL PROCESSOR + BANDPASS FILTER =====
// For AD620 + LM741 DIY Circuit

// --- Filter Coefficients (Butterworth 0.5Hz - 40Hz @ 500Hz Sampling) ---
float xb[5] = {0, 0, 0, 0, 0}; // Input buffer
float yb[5] = {0, 0, 0, 0, 0}; // Output buffer

// Derived coefficients for the difference equation
float b_coeff[] = {0.0461, 0, -0.0922, 0, 0.0461};
float a_coeff[] = {1.0000, -3.5185, 4.6853, -2.7845, 0.6178};

// --- Pin Definitions ---
const int ecgInputPin = A1;    
const int potGainPin  = A0;    
const int outPin      = 9;     

// --- Processing Variables ---
float smoothValue = 512.0;
float alphaSmooth = 0.25; 

void setup() {
  pinMode(ecgInputPin, INPUT);
  pinMode(potGainPin, INPUT);
  pinMode(outPin, OUTPUT);
  Serial.begin(115200); 
}

void loop() {
  // 1. Read Raw Sensor
  int rawValue = analogRead(ecgInputPin);

  // 2. Apply Digital Bandpass Filter (Difference Equation)
  xb[0] = (float)rawValue;
  
  // The mathematical implementation of the Butterworth filter
  yb[0] = b_coeff[0]*xb[0] + b_coeff[1]*xb[1] + b_coeff[2]*xb[2] + b_coeff[3]*xb[3] + b_coeff[4]*xb[4]
          - a_coeff[1]*yb[1] - a_coeff[2]*yb[2] - a_coeff[3]*yb[3] - a_coeff[4]*yb[4];

  // Shift buffers for next sample
  for(int i=4; i>0; i--) {
    xb[i] = xb[i-1];
    yb[i] = yb[i-1];
  }

  // 3. Digital Gain Control via Potentiometer
  int potValue = analogRead(potGainPin);
  float gain = map(potValue, 0, 1023, 10, 300) / 10.0; // 1.0x to 30.0x gain
  float scaledSignal = yb[0] * gain;

  // 4. Smoothing Filter (Final clean-up)
  smoothValue = (alphaSmooth * scaledSignal) + ((1.0 - alphaSmooth) * smoothValue);

  // 5. Re-center for Serial Plotter Display
  // Because the filter removes DC, we add 512 back to see it in the middle of the graph
  float finalPlot = smoothValue + 512;

  // 6. PWM Output (Simulated Analog Out)
  int pwmOut = map((int)finalPlot, 0, 1023, 0, 255);
  pwmOut = constrain(pwmOut, 0, 255);
  analogWrite(outPin, pwmOut);

  // 7. Output to Serial Plotter
  Serial.print("Raw:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("Filtered_Bandpass:");
  Serial.println(finalPlot);

  // Maintain exactly 500Hz sampling (critical for filter math)
  delay(2); 
}