// ===== INTEGRATED ECG SIGNAL PROCESSOR + 4TH ORDER BUTTERWORTH =====
// For AD620 + LM741 DIY Circuit
// Cutoff Frequency: 40Hz | Sampling Rate: 500Hz

// --- 4th Order Filter Variables ---
// We split the 4th order into two 2nd-order stages (Cascaded Biquads) for stability
float x1[3] = {0,0,0}, y1[3] = {0,0,0}; // Stage 1 buffers
float x2[3] = {0,0,0}, y2[3] = {0,0,0}; // Stage 2 buffers

// Coefficients for 40Hz Low-pass @ 500Hz Sampling
// Stage 1 coefficients
float b1[] = {0.0305, 0.0609, 0.0305};
float a1[] = {1.0000, -1.4800, 0.6019};
// Stage 2 coefficients
float b2[] = {0.0305, 0.0609, 0.0305};
float a2[] = {1.0000, -1.7249, 0.8468};

// --- Pin Definitions ---
const int ecgInputPin = A1;    
const int potGainPin  = A0;    
const int outPin      = 9;     

void setup() {
  pinMode(ecgInputPin, INPUT);
  pinMode(potGainPin, INPUT);
  pinMode(outPin, OUTPUT);
  Serial.begin(115200); 
}

void loop() {
  // 1. Read Raw Sensor
  int rawValue = analogRead(ecgInputPin);

  // 2. 4th Order Butterworth Implementation (Cascaded Biquad)
  
  // --- Stage 1 ---
  x1[0] = (float)rawValue;
  y1[0] = b1[0]*x1[0] + b1[1]*x1[1] + b1[2]*x1[2] - a1[1]*y1[1] - a1[2]*y1[2];
  
  // --- Stage 2 (Input is the output of Stage 1) ---
  x2[0] = y1[0];
  y2[0] = b2[0]*x2[0] + b2[1]*x2[1] + b2[2]*x2[2] - a2[1]*y2[1] - a2[2]*y2[2];

  // Shift Buffers
  x1[2] = x1[1]; x1[1] = x1[0];
  y1[2] = y1[1]; y1[1] = y1[0];
  x2[2] = x2[1]; x2[1] = x2[0];
  y2[2] = y2[1]; y2[1] = y2[0];

  // 3. Digital Gain Control
  int potValue = analogRead(potGainPin);
  float centered = y2[0] - 512.0; 
  float gain = map(potValue, 0, 1023, 10, 250) / 10.0; 
  float scaledSignal = centered * gain;

  // 4. Re-center for Plotter
  float finalPlot = scaledSignal + 512.0;

  // 5. PWM Output
  int pwmOut = map((int)finalPlot, 0, 1023, 0, 255);
  analogWrite(outPin, constrain(pwmOut, 0, 255));

  // 6. Serial Output
  Serial.print("Raw:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("Butterworth_4th:");
  Serial.println(finalPlot);

  delay(2); // Critical 500Hz sampling
}