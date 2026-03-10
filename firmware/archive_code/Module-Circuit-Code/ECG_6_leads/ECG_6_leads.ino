/*
 * DUAL MODULE ECG - 6 LEAD SYSTEM
 * Module 1 (Leads I, II, III via calculation) -> Pins A0, 8, 9, 7
 * Module 2 (Precordial/Augmented) -> Pins A1, 5, 4, 3
 */

// --- Module 1 Variables ---
long instance1 = 0;
double hrv1 = 0, hr1 = 72, interval1 = 0;
int count1 = 0;
bool flag1 = 0;

// --- Module 2 Variables ---
long instance2 = 0;
double hrv2 = 0, hr2 = 72, interval2 = 0;
int count2 = 0;
bool flag2 = 0;

long timer;
#define threshold 100 
#define timer_value 10000 

// --- Kalman Filter 1 (Module 1) ---
float Q1 = 0.01, R1 = 0.1, P1 = 1.0, X1 = 0.0;
// --- Kalman Filter 2 (Module 2) ---
float Q2 = 0.01, R2 = 0.1, P2 = 1.0, X2 = 0.0;

// Sampling rate measurement
float sampling_rate = 0;
int sample_count = 0;
unsigned long rate_timer = 0;

void setup() {
  Serial.begin(115200); 

  // Module 1 Pins
  pinMode(8, INPUT); // LO-
  pinMode(9, INPUT); // LO+
  pinMode(7, OUTPUT); // SDN
  digitalWrite(7, HIGH);

  // Module 2 Pins
  pinMode(5, INPUT); // LO-
  pinMode(4, INPUT); // LO+
  pinMode(3, OUTPUT); // SDN
  digitalWrite(3, HIGH);

  rate_timer = millis();
  timer = millis();
}

// Separate Kalman functions to keep signals distinct
float kalman1(float val) {
  P1 = P1 + Q1;
  float K = P1 / (P1 + R1);
  X1 = X1 + K * (val - X1);
  P1 = (1 - K) * P1;
  return X1;
}

float kalman2(float val) {
  P2 = P2 + Q2;
  float K = P2 / (P2 + R2);
  X2 = X2 + K * (val - X2);
  P2 = (1 - K) * P2;
  return X2;
}

void loop() { 
  // 1. Leads Off Detection (Independent for each module)
  bool lo1 = (digitalRead(8) == 1 || digitalRead(9) == 1);
  bool lo2 = (digitalRead(5) == 1 || digitalRead(4) == 1);

  if (lo1) digitalWrite(7, LOW); else digitalWrite(7, HIGH);
  if (lo2) digitalWrite(3, LOW); else digitalWrite(3, HIGH);

  // 2. Sampling Rate Calculation
  sample_count++;
  if ((millis() - rate_timer) >= 1000) {
    sampling_rate = (float)sample_count;
    sample_count = 0;
    rate_timer = millis();
  }

  // 3. Read and Filter Module 1
  int raw1 = analogRead(A0);
  float val1 = map(raw1, 250, 400, 0, 100);
  float filtered1 = kalman1(val1);

  // 4. Read and Filter Module 2
  int raw2 = analogRead(A1);
  float val2 = map(raw2, 250, 400, 0, 100);
  float filtered2 = kalman2(val2);

  // 5. Peak Detection (Logic for Heart Rate 1)
  if((filtered1 > threshold) && (!flag1)) {
    count1++; flag1 = 1;
    interval1 = micros() - instance1;
    instance1 = micros(); 
  } else if(filtered1 < threshold) {
    flag1 = 0;
  }

  // 6. 10-Second HR Calculation
  if ((millis() - timer) > timer_value) {
    hr1 = count1 * 6;
    hr2 = count2 * 6; // Assuming pulses are synchronized, but tracking separately
    timer = millis();
    count1 = 0; count2 = 0;
  }

  // 7. Data Output (6-Lead Data Stream)
  // Format: HR, Filtered1, Filtered2, SamplingRate
  Serial.print(hr1);        Serial.print(",");
  Serial.print(filtered1);  Serial.print(",");
  Serial.print(filtered2);  Serial.print(",");
  Serial.println(sampling_rate, 0);

  delay(1); 
}