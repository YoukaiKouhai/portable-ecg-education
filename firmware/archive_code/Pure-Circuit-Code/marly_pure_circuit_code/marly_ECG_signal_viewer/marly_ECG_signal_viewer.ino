// ===== ECG SIGNAL VIEWER =====

// Pin definitions
int potOutputPin = A0;   // Potentiometer output (final ECG signal)
int ecgInputPin  = A1;   // LM741 output (monitor only)

// Variables
int rawValue = 0;
float dcEstimate = 512.0;
float alphaDC = 0.995;
float smooth = 0;
float alphaSmooth = 0.25;

void setup() {
  // initializes pin modes
  pinMode(potOutputPin, INPUT);  // ECG after pot
  pinMode(ecgInputPin, INPUT);   // ECG before pot (optional monitor)

  Serial.begin(115200); // initiates serial communication for debugging
}

void loop() {

  // Read ECG from potentiometer output
  rawValue = analogRead(potOutputPin);

  // Remove DC offset
  dcEstimate = alphaDC * dcEstimate + (1 - alphaDC) * rawValue;
  float ecg = rawValue - dcEstimate;

  // Smooth the signal
  smooth = alphaSmooth * ecg + (1 - alphaSmooth) * smooth;

  // Send to Serial Plotter
  Serial.println(smooth);

  delay(2); // ~500 Hz sampling
}
