// ===== INTEGRATED ECG SIGNAL PROCESSOR + ADAPTIVE LMS FILTER =====
// For AD620 + LM741 DIY Circuit

// --- Adaptive Filter Variables ---
float mu = 0.015;    // Learning rate (Convergence speed: 0.001 to 0.05)
float w = 0.5;       // Initial Filter weight
float x_delay = 512; // Previous input sample (Reference)

// --- Pin Definitions ---
const int ecgInputPin = A1;    
const int potGainPin  = A0;    
const int outPin      = 9;     

// --- Final Output Variables ---
float smoothValue = 512.0;
float alphaSmooth = 0.2; // Final stage low-pass smoothing

void setup() {
  pinMode(ecgInputPin, INPUT);
  pinMode(potGainPin, INPUT);
  pinMode(outPin, OUTPUT);
  
  // High baud rate is essential for real-time math
  Serial.begin(115200); 
}

void loop() {
  // 1. Read Raw Sensor
  int rawValue = analogRead(ecgInputPin);

  // 2. Adaptive Filtering (LMS Algorithm)
  // Step A: Predict the current sample based on the previous sample
  float prediction = w * x_delay;
  
  // Step B: Calculate the Estimation Error (Noise component)
  float error = (float)rawValue - prediction;
  
  // Step C: Update the weight (w) to minimize future error
  // This is the "Learning" step
  w = w + mu * error * x_delay; 
  
  // Step D: Update the delay for the next loop
  x_delay = (float)rawValue;

  // 3. Digital Gain Control via Potentiometer
  // We use the 'prediction' as our filtered signal
  int potValue = analogRead(potGainPin);
  
  // Center the signal around 0
  float centered = prediction - 512.0; 
  
  // Map pot to a gain factor (1.0x to 20.0x)
  float gain = map(potValue, 0, 1023, 10, 200) / 10.0; 
  float scaledSignal = centered * gain;

  // 4. Final Post-Filter Smoothing
  smoothValue = (alphaSmooth * scaledSignal) + ((1.0 - alphaSmooth) * smoothValue);

  // 5. Re-center for Display
  float finalPlot = smoothValue + 512.0;

  // 6. PWM Output (Simulated Analog Out)
  int pwmOut = map((int)finalPlot, 0, 1023, 0, 255);
  pwmOut = constrain(pwmOut, 0, 255);
  analogWrite(outPin, pwmOut);

  // 7. Output to Serial Plotter
  Serial.print("Raw:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("Adaptive_LMS:");
  Serial.println(finalPlot);

  delay(2); // 500Hz Sampling
}