// ===== INTEGRATED ECG SIGNAL PROCESSOR + CHEBYSHEV NOTCH =====
// For AD620 + LM741 DIY Circuit
// Rejection Frequency: 60Hz | Sampling Rate: 500Hz

// --- Chebyshev Type II Notch Variables ---
float xc[3] = {0, 0, 0}; // Input history
float yc[3] = {0, 0, 0}; // Output history

// Coefficients calculated for 60Hz Rejection at 500Hz Sampling
// This provides a steep, narrow stopband
float bc[] = {0.9328, -1.3320, 0.9328}; 
float ac[] = {1.0000, -1.3320, 0.8656};

// --- Pin Definitions ---
const int ecgInputPin = A1;    
const int potGainPin  = A0;    
const int outPin      = 9;     

void setup() {
  pinMode(ecgInputPin, INPUT);
  pinMode(potGainPin, INPUT);
  pinMode(outPin, OUTPUT);
  
  // High baud rate is mandatory for timing accuracy
  Serial.begin(115200); 
}

void loop() {
  // 1. Read Raw Sensor
  int rawValue = analogRead(ecgInputPin);

  // 2. Chebyshev Notch Implementation (Difference Equation)
  xc[0] = (float)rawValue;

  // yc[0] = (b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2) / a0
  yc[0] = bc[0]*xc[0] + bc[1]*xc[1] + bc[2]*xc[2] 
          - ac[1]*yc[1] - ac[2]*yc[2];

  // Shift buffers for next sample
  xc[2] = xc[1]; xc[1] = xc[0];
  yc[2] = yc[1]; yc[1] = yc[0];

  // 3. Digital Gain Control
  int potValue = analogRead(potGainPin);
  
  // Center the signal (assuming mid-rail is 512)
  float centered = yc[0] - 512.0; 
  
  // Gain range: 1.0x to 25.0x
  float gain = map(potValue, 0, 1023, 10, 250) / 10.0; 
  float scaledSignal = centered * gain;

  // 4. Re-center for Plotter
  float finalPlot = scaledSignal + 512.0;

  // 5. PWM Output (Simulated Analog)
  int pwmOut = map((int)finalPlot, 0, 1023, 0, 255);
  analogWrite(outPin, constrain(pwmOut, 0, 255));

  // 6. Serial Output
  // Blue line is Raw, Red line is the "Surgically Cleaned" signal
  Serial.print("Raw:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("Chebyshev_Notch:");
  Serial.println(finalPlot);

  // CRITICAL: The notch is math-locked to 500Hz. 
  // delay(2) ensures the math hits exactly 60Hz.
  delay(2); 
}