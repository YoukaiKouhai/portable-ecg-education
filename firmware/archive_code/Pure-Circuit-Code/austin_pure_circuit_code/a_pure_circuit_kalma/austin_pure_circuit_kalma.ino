// ===== INTEGRATED ECG SIGNAL PROCESSOR + KALMAN FILTER =====
// For AD620 + LM741 DIY Circuit

// --- Kalman Filter Variables ---
float Q = 0.1;      // Process Noise Covariance (How much the ECG changes)
float R = 25.0;     // Measurement Noise Covariance (Increase for more smoothing)
float P = 1.0;      // Estimation Error Covariance
float K = 0.0;      // Kalman Gain
float X_hat = 512.0; // The filtered signal "estimate"

// --- Pin Definitions ---
const int ecgInputPin = A1;    
const int potGainPin  = A0;    
const int outPin      = 9;     

// --- Final Output Variables ---
float smoothValue = 512.0;
float alphaSmooth = 0.15; // Extra smoothing for the output

void setup() {
  pinMode(ecgInputPin, INPUT);
  pinMode(potGainPin, INPUT);
  pinMode(outPin, OUTPUT);
  
  // High baud rate to handle the math and data stream
  Serial.begin(115200); 
}

void loop() {
  // 1. Read Raw Sensor
  int rawValue = analogRead(ecgInputPin);

  // 2. Kalman Filter Implementation
  // Prediction Update
  P = P + Q;

  // Measurement Update (Correction)
  K = P / (P + R);                     // Calculate Kalman Gain
  X_hat = X_hat + K * (rawValue - X_hat); // Update estimate with sensor data
  P = (1.0 - K) * P;                   // Update error covariance

  // 3. Digital Gain Control via Potentiometer
  // We use X_hat (the Kalman estimate) for processing
  int potValue = analogRead(potGainPin);
  
  // Center the signal around 0 for gain application
  float centered = X_hat - 512.0; 
  
  // Map pot to a gain factor (1.0x to 15.0x)
  float gain = map(potValue, 0, 1023, 10, 150) / 10.0; 
  float scaledSignal = centered * gain;

  // 4. Final Smoothing (Simple Low Pass)
  smoothValue = (alphaSmooth * scaledSignal) + ((1.0 - alphaSmooth) * smoothValue);

  // 5. Re-center for Display
  float finalPlot = smoothValue + 512.0;

  // 6. PWM Output (Simulated Analog Out)
  int pwmOut = map((int)finalPlot, 0, 1023, 0, 255);
  pwmOut = constrain(pwmOut, 0, 255);
  analogWrite(outPin, pwmOut);

  // 7. Output to Serial Plotter
  Serial.print("Raw_Signal:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("Kalman_Filtered:");
  Serial.println(finalPlot);

  delay(2); // 500Hz Sampling
}