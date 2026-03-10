// ===================== PINS =====================
const int potPin = A0;   // POT = output control knob
const int ecgPin = A1;   // ECG = signal input
const int leadOff1 = 10;
const int leadOff2 = 11;

// ===================== VARIABLES =====================
int rawECG = 0;
int centered = 0;
int scaled = 0;
int smooth = 0;
int prev = 0;

void setup() {
  Serial.begin(115200);
  pinMode(leadOff1, INPUT);
  pinMode(leadOff2, INPUT);
}

// ===================== LOOP =====================
void loop() {

  // Lead-off protection
  if (digitalRead(leadOff1) == HIGH || digitalRead(leadOff2) == HIGH) {
    Serial.println(512);
    delay(2);
    return;
  }

  // Read ECG from A1
  rawECG = analogRead(ecgPin);

  // Remove DC bias
  centered = rawECG - 512;

  // Potentiometer = OUTPUT CONTROL
  int pot = analogRead(potPin);
  float gain = map(pot, 0, 1023, 1, 15);

  // Apply pot scaling
  scaled = centered * gain;

  // Add DC back
  scaled = scaled + 512;

  // Smooth
  smooth = (scaled + prev) / 2;
  prev = smooth;

  // Send to plotter
  Serial.println(smooth);

  delay(2); // ~500 Hz
}
