# Portable ECG Educational Platform

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![ECG](https://img.shields.io/badge/Project-ECG-green)
![Arduino](https://img.shields.io/badge/Hardware-Arduino-orange)

## Overview
This project develops a portable electrocardiogram (ECG) system designed for educational outreach and biomedical engineering instruction. The system demonstrates the full ECG signal acquisition and processing pipeline, including electrode measurement, analog signal amplification, digital acquisition using Arduino, signal processing, and visualization.

The project evolved through multiple hardware iterations. An initial fully discrete analog ECG amplifier using instrumentation amplifiers and operational amplifiers was developed to explore low-level biopotential amplification. Due to stability challenges and noise susceptibility, the design transitioned to a modular architecture using AD8232 ECG front-end modules.

The current system supports acquisition of Lead I and Lead II signals and computes derived limb leads to reconstruct a six-lead ECG representation. Signal processing, filtering, and analysis are implemented in MATLAB, with visualization tools provided in Python.

## Project Goals
## System Architecture
## Hardware Designs
## Software Pipeline

The software architecture for this project is designed to demonstrate the full ECG signal acquisition and processing pipeline, from raw analog measurement to digital signal analysis and visualization. The system integrates microcontroller firmware, MATLAB-based signal processing, and Python visualization tools.

The pipeline operates as follows:

1. **Signal Acquisition (Arduino)**  
   The Arduino microcontroller collects raw ECG signals from the analog ECG front-end. In the current system configuration, two AD8232 modules are used to acquire **Lead I and Lead II** signals. The Arduino performs analog-to-digital conversion (ADC) and streams the raw data to a host computer through serial communication.

2. **Data Control and Acquisition (MATLAB)**  
   MATLAB controls the data acquisition process and manages communication with the Arduino. During each recording session, MATLAB:
   
   - Opens the serial connection to the Arduino  
   - Collects ECG data for a fixed acquisition window (typically ~20 seconds)  
   - Converts ADC values into millivolt-scale ECG signals  
   - Saves the raw data to CSV files for later analysis  

3. **Derived Lead Reconstruction**  
   From the measured Lead I and Lead II signals, MATLAB calculates the remaining limb leads using standard electrocardiographic relationships:

   - Lead III = Lead II − Lead I  
   - aVR = −(Lead I + Lead II) / 2  
   - aVL = Lead I − Lead II / 2  
   - aVF = Lead II − Lead I / 2  

   This allows reconstruction of a **six-lead ECG representation** from two measured signals.

4. **Signal Processing and Analysis**  
   MATLAB performs signal filtering, waveform processing, and heart-rate detection. Multiple filtering approaches are implemented to evaluate signal quality and reduce noise artifacts.

5. **Visualization (Python)**  
   Python scripts are used to visualize the ECG signals after acquisition and processing. The visualization tools can plot all six derived leads and compare the effects of different filtering techniques.

The MATLAB acquisition script also automatically generates structured CSV reports containing:

- Raw ECG data  
- Filtered ECG signals  
- Derived lead signals  
- Filter performance results  

This modular architecture allows the system to be easily extended with additional processing tools or visualization platforms.

## Signal Processing Methods

Electrocardiogram signals are low-amplitude biological signals that are highly susceptible to noise sources such as motion artifacts, baseline drift, and electrical interference. To improve signal quality and enable accurate analysis, several filtering techniques were implemented and evaluated.

The following signal processing methods are included in the current system:

### Bandpass Filtering
Bandpass filtering removes frequency components outside the expected ECG frequency band. Typical ECG signals contain important physiological information primarily between **0.5 Hz and 40 Hz**. Frequencies below this range often correspond to baseline drift, while higher frequencies may represent muscle noise or electrical interference.

### Butterworth Filtering
A Butterworth filter is implemented to provide a smooth and stable bandpass response with minimal ripple in the passband. This filter is commonly used in ECG processing because it preserves waveform morphology while effectively suppressing noise.

### Chebyshev Notch Filtering
A Chebyshev notch filter is used to reduce narrowband interference from power line noise, typically around **60 Hz** in North America. This filter selectively attenuates the interference frequency without significantly distorting the ECG waveform.

### Kalman Filtering
A Kalman filter is implemented as a recursive estimation technique to reduce measurement noise while preserving dynamic signal characteristics. This approach can adaptively estimate the underlying ECG signal in the presence of noisy measurements.

### Adaptive LMS Filtering
An adaptive Least Mean Squares (LMS) filter is included to demonstrate adaptive noise cancellation methods. LMS filters adjust their coefficients dynamically in response to signal variations and can help reduce motion artifacts or environmental interference.

### Heart Rate Detection
After filtering, the system performs **R-peak detection** to identify the QRS complexes within the ECG waveform. The time difference between detected R peaks is used to estimate the heart rate in beats per minute (BPM).

These signal processing techniques allow the system to evaluate and compare filtering performance and demonstrate the impact of noise reduction on ECG waveform clarity.

## Repository Structure
## Getting Started
## Running the System
## Example Results
## Future Development

While the current system uses MATLAB for signal processing and analysis, one limitation identified during the design review process is that MATLAB requires a licensed environment. For broader educational outreach, it is desirable for the entire system to operate using **fully open-source software** that can run on any student computer.

Future development efforts will focus on migrating the processing pipeline to open-source platforms and improving accessibility for educational use.

### Open-Source Software Implementations

Possible software directions include:

**Python-Based Pipeline**

Reimplement the signal acquisition and filtering pipeline in Python using open-source scientific libraries such as:

- NumPy
- SciPy
- Pandas
- Matplotlib

Students could install the required tools using standard package managers such as `pip`, making the system easier to deploy in classrooms and workshops.

**Java-Based Implementation**

Another possible direction is to implement the processing pipeline in Java. Java applications can run on many operating systems and can be easily executed in educational environments such as BlueJ or other teaching IDEs.

### Browser-Based ECG Visualization

A modern and highly accessible solution is to run the ECG visualization and analysis entirely in a web browser. Recent web technologies allow JavaScript to directly communicate with hardware devices connected via USB.

Modern browsers now support the **Web Serial API**, which allows a webpage to read serial data from devices such as an Arduino.

Example JavaScript code:

```javascript
const port = await navigator.serial.requestPort();
await port.open({ baudRate: 115200 });

const reader = port.readable.getReader();

while (true) {
  const { value } = await reader.read();
  console.log(value);
}
```
This approach enables:

- Real-time ECG streaming directly from Arduino  
- No backend server required  
- Execution entirely inside a web browser  
- Compatibility with GitHub Pages deployment  

Using this architecture, a browser-based educational ECG monitor could include:

- Real-time ECG waveform visualization  
- Heart-rate estimation  
- Filter comparison tools  
- Upload and playback of prerecorded ECG datasets  

Because the system would run entirely in the browser, it would be accessible on most modern computers without installing specialized software.

## Contributors

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

This license allows anyone to:

- Use the software for any purpose  
- Modify the source code  
- Distribute modified versions  

However, any redistributed or modified versions of the software must also be released under the same GPL-3.0 license.

See the `LICENSE` file in this repository for the full license text.