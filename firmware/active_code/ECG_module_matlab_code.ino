/*
 * 6-Lead ECG RAW ACQUISITION
 * Module 1 -> Lead I  (A0)
 * Module 2 -> Lead II (A1)
 */

const unsigned long Ts = 2000;   // microseconds = 500 Hz
unsigned long lastSample = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {

  if (micros() - lastSample >= Ts) {

    lastSample += Ts;

    int leadI  = analogRead(A0);
    int leadII = analogRead(A1);

    Serial.print(leadI);
    Serial.print(",");
    Serial.println(leadII);
  }
}