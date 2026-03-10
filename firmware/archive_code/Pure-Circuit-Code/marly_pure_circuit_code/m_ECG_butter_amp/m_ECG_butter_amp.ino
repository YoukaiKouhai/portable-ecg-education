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

// ===== BUTTERWORTH FILTER VARIABLES =====
// 2nd order Butterworth low-pass filter, cutoff ~40Hz, sampling ~500Hz
float b0 = 0.2066;
float b1 = 0.4131;
float b2 = 0.2066;
float a1 = -0.3695;
float a2 = 0.1958;
float x1 = 0, x2 = 0;  // input history
float y1 = 0, y2 = 0;  // output history
float filteredValue = 0;

// Sampling rate measurement
unsigned long lastSampleTime = 0;
unsigned long sampleInterval = 0;
float samplingRate = 0.0;

void setup() {
  // initializes pin modes
  pinMode(potOutputPin, INPUT);  // ECG after pot
  pinMode(ecgInputPin, INPUT);   // ECG before pot (optional monitor)

  Serial.begin(115200); // initiates serial communication for debugging
  lastSampleTime = micros();
}

void loop() {
  // Calculate sampling rate
  unsigned long currentTime = micros();
  sampleInterval = currentTime - lastSampleTime;
  samplingRate = 1000000.0 / sampleInterval;  // Hz
  lastSampleTime = currentTime;

  // Read ECG from potentiometer output
  rawValue = analogRead(potOutputPin);

  // Remove DC offset
  dcEstimate = alphaDC * dcEstimate + (1 - alphaDC) * rawValue;
  float ecg = rawValue - dcEstimate;

  // Smooth the signal
  smooth = alphaSmooth * ecg + (1 - alphaSmooth) * smooth;

  // ===== BUTTERWORTH FILTER =====
  // Apply 2nd order Butterworth low-pass filter
  filteredValue = b0 * smooth + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
  
  // Update filter history
  x2 = x1;
  x1 = smooth;
  y2 = y1;
  y1 = filteredValue;

  // Send to Serial Plotter (use filtered signal instead of raw smooth)
  Serial.print("ECG:");
  Serial.print(filteredValue);
  Serial.print(",SR:");
  Serial.println(samplingRate);

  delay(2); // ~500 Hz sampling
}

