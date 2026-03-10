/*
  Arduino ECG Input (AD620/LM741) and Potentiometer Output
  - Input: Raw ECG signal from circuit -> Pin A0
  - Output: Simulated ECG output -> Pin 9 (PWM)
*/

const int ecgPin = A0;    // AD620+LM741 Output Input
const int outPin = 9;     // Potentiometer/Output simulation Pin
int ecgValue = 0;         // Variable to store input
int mappedValue = 0;      // Variable to store output

void setup() {
  Serial.begin(9600);     // Initialize serial communication
  pinMode(outPin, OUTPUT);
}

void loop() {
  // Read the analog value from the ECG circuit (0-1023)
  ecgValue = analogRead(ecgPin);

  // Map the input signal to a PWM output (0-255)
  // This simulates the potentiometer-like output
  mappedValue = map(ecgValue, 0, 1023, 0, 255);

  // Output the mapped value to pin 9
  analogWrite(outPin, mappedValue);

  // Print values to Serial Plotter (Tools > Serial Plotter)
  Serial.print("RawECG:");
  Serial.print(ecgValue);
  Serial.print(",");
  Serial.print("OutputSignal:");
  Serial.println(mappedValue);

  delay(1); // Small delay for stability
}
