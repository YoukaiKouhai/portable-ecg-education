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

// ===== KALMAN FILTER VARIABLES =====
float kalmanValue = 0;        // Filtered output
float kalmanP = 1;            // Estimation error covariance
float kalmanQ = 0.125;        // Process noise covariance (adjust for responsiveness)
float kalmanR = 32;           // Measurement noise covariance (adjust for smoothing)
float kalmanK = 0;            // Kalman gain
// ===================================

// Sampling rate measurement
unsigned long lastTime = 0;
unsigned long currentTime = 0;
float samplingRate = 0;
int sampleCount = 0;
unsigned long lastPrintTime = 0;

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

  // ===== KALMAN FILTER =====
  // Prediction update
  kalmanP = kalmanP + kalmanQ;
  
  // Measurement update
  kalmanK = kalmanP / (kalmanP + kalmanR);
  kalmanValue = kalmanValue + kalmanK * (smooth - kalmanValue);
  kalmanP = (1 - kalmanK) * kalmanP;
  // ==========================

  // Send filtered signal to Serial Plotter
  Serial.println(kalmanValue);

  // Calculate and display sampling rate every second
  sampleCount++;
  currentTime = micros();
  if (currentTime - lastPrintTime >= 1000000) { // 1 second
    samplingRate = sampleCount;
    Serial.print("Sampling Rate: ");
    Serial.print(samplingRate);
    Serial.println(" Hz");
    sampleCount = 0;
    lastPrintTime = currentTime;
  }
  lastTime = currentTime;

  delay(2); // ~500 Hz sampling
}

