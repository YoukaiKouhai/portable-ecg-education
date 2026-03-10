# Java ECG Processing Pipeline (Future Direction)

This folder contains a **Java-based implementation of the ECG processing pipeline** originally developed in MATLAB for the Portable ECG Educational Platform.

The MATLAB program currently serves as the primary data acquisition and signal processing environment for this project. However, MATLAB requires a licensed installation, which can limit accessibility for educational outreach and classroom use.

The goal of this Java implementation is to create a **fully open-source and portable alternative** that can run on any computer with a Java Runtime Environment (JRE).

---

## Purpose

The Java version aims to replicate the core functionality of the MATLAB pipeline while maintaining compatibility with open-source tools and standard Java libraries.

Key motivations include:

- Removing dependence on proprietary software
- Improving accessibility for schools and workshops
- Enabling cross-platform execution
- Supporting future web-based or GUI interfaces

---

## Pipeline Overview

The original MATLAB program (~900 lines) implements the full ECG processing workflow, including several subsystems:

- File and run-folder management
- Serial data acquisition from Arduino
- CSV file loading
- ADC to millivolt signal conversion
- Derived ECG lead calculation
- Real-time ECG plotting
- Multiple filtering methods
- Heart-rate detection
- CSV result export
- Filter performance evaluation

MATLAB provides many built-in signal processing tools (`designfilt`, `findpeaks`, etc.), so the Java version recreates this pipeline using open-source libraries.

---

## Java Libraries Used

The following libraries are used to implement the ECG processing pipeline:

| Task | Java Library |
|-----|-----|
| Arduino Serial Communication | jSerialComm |
| CSV Data Handling | OpenCSV |
| Plotting / Visualization | XChart |
| Digital Signal Processing | Apache Commons Math |
| Fast Fourier Transform (FFT) | JTransforms |

These libraries provide functionality similar to MATLAB's signal processing and visualization features.

---

## Intended Features

The Java pipeline aims to support the following capabilities:

- Serial communication with Arduino ECG hardware
- Loading and saving ECG CSV datasets
- Conversion of ADC values to millivolt ECG signals
- Reconstruction of derived limb leads
- ECG signal filtering
- Real-time waveform visualization
- R-peak detection and heart-rate estimation
- Filter performance comparison

---

## Educational Goals

This implementation is intended to support educational demonstrations in biomedical engineering courses and outreach events. The Java environment allows students to explore ECG signal processing concepts without requiring specialized software.

---

## Future Improvements

Possible extensions of the Java pipeline include:

- Graphical user interface (GUI) for ECG monitoring
- Real-time data streaming from Arduino
- Interactive filter comparison tools
- Support for additional ECG leads
- Integration with browser-based visualization tools

---

## Relationship to MATLAB Implementation

The MATLAB codebase remains the **primary working implementation** for the project.

This Java version should currently be considered:

- Experimental
- Incomplete
- A foundation for future open-source development

Future contributors may expand this implementation to fully replace the MATLAB pipeline.

---

## Running the Java Version

Example workflow:

1. Compile the source files
2. Connect the Arduino ECG device
3. Run the main application

Example command:
javac src/ecg/*.java
java ecg.Main


Library dependencies must be included in the Java classpath.

---

## Repository Context

This Java implementation is part of the larger **Portable ECG Educational Platform**, which includes:

- Arduino firmware for ECG data acquisition
- MATLAB signal processing pipeline
- Python visualization tools
- Hardware documentation

See the main repository README for the full system architecture.