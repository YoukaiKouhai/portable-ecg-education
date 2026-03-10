// ===== INTEGRATED ECG SIGNAL PROCESSOR (AD620 + LM741) =====

// Pin Definitions
const int ecgInputPin = A1;    // Output from your LM741 circuit
const int potGainPin  = A0;    // Potentiometer for on-the-fly gain control
const int outPin      = 9;     // PWM Output (to simulate an analog out)

// Processing Variables
float dcEstimate   = 512.0;    // Tracks the "baseline" of the signal
float alphaDC      = 0.995;    // Filter constant for DC tracking (0.99 - 0.999)
float smoothValue  = 512.0;    // The final clean signal
float alphaSmooth  = 0.25;     // Smoothing factor (lower = smoother but more lag)

void setup() {
  // Initialize Pins
  pinMode(ecgInputPin, INPUT);
  pinMode(potGainPin, INPUT);
  pinMode(outPin, OUTPUT);

  // High baud rate for smooth Serial Plotter visuals
  Serial.begin(115200); 
}

void loop() {
  // 1. Read the raw signal from the op-amp circuit
  int rawValue = analogRead(ecgInputPin);

  // 2. Adaptive DC Offset Removal
  // This calculates a moving average to find the signal's "center"
  dcEstimate = (alphaDC * dcEstimate) + ((1.0 - alphaDC) * rawValue);
  float centered = rawValue - dcEstimate;

  // 3. Digital Gain Control via Potentiometer
  // Read pot and map to a gain factor (e.g., 1x to 20x)
  int potValue = analogRead(potGainPin);
  float gain = map(potValue, 0, 1023, 10, 200) / 10.0; // 1.0 to 20.0 gain
  float scaledSignal = centered * gain;

  // 4. Low-Pass Smoothing
  // Removes high-frequency "fuzz" not caught by your analog RC filter
  smoothValue = (alphaSmooth * scaledSignal) + ((1.0 - alphaSmooth) * smoothValue);

  // 5. Shift back to mid-range for display (Adding 512)
  float finalPlot = smoothValue + 512;

  // 6. PWM Output (Simulated Analog Output)
  // Map the 0-1023 range to 0-255 for the PWM pin
  int pwmOut = map((int)finalPlot, 0, 1023, 0, 255);
  pwmOut = constrain(pwmOut, 0, 255); // Safety limit
  analogWrite(outPin, pwmOut);

  // 7. Multi-Variable Plotting
  // Format compatible with Arduino Serial Plotter
  Serial.print("Raw:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("Filtered:");
  Serial.println(finalPlot);

  delay(2); // ~500 Hz Sampling Rate
}