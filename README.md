# Portable ECG Educational Platform

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Project: ECG](https://img.shields.io/badge/Project-ECG-green)
![Hardware: Arduino](https://img.shields.io/badge/Hardware-Arduino-orange)
![UCSD Bioengineering](https://img.shields.io/badge/UCSD-Bioengineering-blue)

A portable, low-cost electrocardiogram (ECG) system designed for educational outreach and biomedical engineering instruction. Built as a UCSD Bioengineering senior design project, the system allows students to safely observe, interact with, and interpret real-time cardiac electrical signals in classroom and outreach environments.

> **Special thanks** to Professor Pedro Cabrales and Iris Zaretzki for their guidance throughout this project.

---

## Table of Contents

- [Portable ECG Educational Platform](#portable-ecg-educational-platform)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Goals](#project-goals)
  - [System Architecture](#system-architecture)
  - [Hardware Design](#hardware-design)
    - [Components](#components)
    - [Lead Configuration](#lead-configuration)
    - [Design History](#design-history)
  - [Software Pipeline](#software-pipeline)
    - [1. Arduino Firmware (`/arduino`)](#1-arduino-firmware-arduino)
    - [2. MATLAB Acquisition Script (`/matlab`)](#2-matlab-acquisition-script-matlab)
    - [3. Python Visualization (`/python`)](#3-python-visualization-python)
    - [CSV Export Format](#csv-export-format)
  - [Signal Processing Methods](#signal-processing-methods)
    - [Bandpass Filter](#bandpass-filter)
    - [Butterworth Filter](#butterworth-filter)
    - [Chebyshev Notch Filter (60 Hz)](#chebyshev-notch-filter-60-hz)
    - [Kalman Filter *(Best Performing)*](#kalman-filter-best-performing)
    - [Adaptive LMS Filter](#adaptive-lms-filter)
  - [Filter Performance Results](#filter-performance-results)
  - [Repository Structure](#repository-structure)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Wiring](#wiring)
  - [Running the System](#running-the-system)
    - [Step 1 — Upload Arduino Firmware](#step-1--upload-arduino-firmware)
    - [Step 2 — Run MATLAB Acquisition](#step-2--run-matlab-acquisition)
    - [Step 3 — Visualize in Python](#step-3--visualize-in-python)
  - [Future Development](#future-development)
  - [Contributors](#contributors)
  - [License](#license)

---

## Overview

Clinical ECG systems typically cost between **$1,000 and $10,000**, are complex to operate, and are designed exclusively for medical environments. This project addresses the gap by developing a portable, self-contained ECG demonstration device built around the **AD8232 analog front-end** and an **Arduino microcontroller** for around **~$40 in components**.

The system captures surface bioelectric signals from two physical leads (Lead I and Lead II), applies digital signal processing and filtering, and mathematically reconstructs a full **six-lead ECG representation**. Processed signals can be visualized in real-time and exported for analysis using MATLAB and Python.

The design evolved through multiple hardware iterations. An initial fully discrete analog ECG amplifier using instrumentation amplifiers (INA/op-amp topology) was developed first, but was replaced due to noise susceptibility and stability challenges. The current system uses two **AD8232 ECG front-end modules** in a modular, reliable architecture.

---

## Project Goals

| Goal | Weight | Description |
|------|--------|-------------|
| Safety | 35% | Battery-powered, electrically isolated from wall power. Leakage current verified below 10 µA. |
| Signal Quality | 35% | Clear P, QRS, and T wave visualization with 0.5–50 Hz bandwidth and 60 Hz notch filtering. |
| Educational Usability | 30% | Color-coded electrode placement guides, self-test mode, and pre/post outreach knowledge surveys. |

**Key Constraints:**
- $400 budget limit
- IRB compliance for any participant data collection
- Week 9 of winter quarter delivery deadline
- Low-voltage (5V USB) operation for classroom safety

---

## System Architecture

The system is organized into three computational layers:

```
Electrodes → Analog Front-End (AD8232) → Arduino ADC
    → Serial Transmission (115200 baud)
    → MATLAB Acquisition & Filtering
    → CSV Export
    → Python Visualization
```

1. **Embedded Acquisition Layer** — Arduino firmware handles real-time ADC sampling
2. **Host Processing Layer** — MATLAB manages data acquisition, filtering, and CSV export
3. **Visualization Layer** — Python renders waveforms for ECG analysis and outreach demos

This layered design isolates hardware timing constraints from computationally intensive signal processing, improving maintainability and enabling parallel debugging.

---

## Hardware Design

### Components

| Component | Purpose |
|-----------|---------|
| Arduino UNO / Nano | Microcontroller for ADC sampling and serial transmission |
| AD8232 ECG Module (×2) | Analog front-end: instrumentation amplifier + built-in filtering |
| Ag/AgCl Surface Electrodes | Biopotential signal capture from skin |
| 3D-Printed Enclosure | Protects electronics during outreach demonstrations |
| USB / Battery Power | Low-voltage, electrically isolated power supply |

### Lead Configuration

Only **Lead I** and **Lead II** are physically measured. The remaining four limb leads are mathematically derived:

| Lead | Formula |
|------|---------|
| Lead III | Lead II − Lead I |
| aVR | −(Lead I + Lead II) / 2 |
| aVL | Lead I − Lead II / 2 |
| aVF | Lead II − Lead I / 2 |

This approach reduces electrode and hardware complexity while preserving a **six-lead ECG representation** suitable for waveform analysis and classroom demonstrations.

### Design History

**Iteration 1 — Discrete Analog Circuit:**  
A fully discrete ECG amplifier was designed using an AD620 instrumentation amplifier and LM741 op-amps to explore biopotential amplification from first principles. This design was ultimately replaced due to noise susceptibility and stability challenges in a non-lab environment.

**Iteration 2 — AD8232 Module Architecture (Current):**  
The AD8232 integrates a complete instrumentation amplifier, filtering, and lead-off detection into a single chip. Two modules acquire Lead I and Lead II simultaneously. This modular approach significantly improves signal stability, reduces setup time, and is more reproducible for educational use.

---

## Software Pipeline

### 1. Arduino Firmware (`/arduino`)

The Arduino firmware performs real-time analog-to-digital conversion at ~500 Hz and streams raw data over serial:

```cpp
// Each transmitted packet:
// LeadI_sample, LeadII_sample
Serial.print(analogRead(A0));
Serial.print(",");
Serial.println(analogRead(A1));
```

- Sampling rate: ~500 Hz (sufficient for 0.05–150 Hz ECG bandwidth)
- Baud rate: 115200
- No on-device filtering — all processing handled downstream to avoid sampling jitter

### 2. MATLAB Acquisition Script (`/matlab`)

MATLAB manages the recording session:

- Opens the serial connection to the Arduino
- Preallocates a fixed-size acquisition buffer (avoids latency from dynamic resizing)
- Records data for a **20-second acquisition window**
- Converts raw ADC values to millivolt-scale ECG signals
- Computes all derived leads (Lead III, aVR, aVL, aVF)
- Applies digital filters and exports results to structured CSV files

Effective sampling frequency is estimated post-acquisition as:

```
fs_effective = N / T
```

where `N` = total sample count and `T` = recording duration.

### 3. Python Visualization (`/python`)

Python scripts visualize the six-lead ECG using vertically stacked subplots:

```bash
pip install numpy scipy matplotlib pandas
python visualize_ecg.py
```

Features:
- All six leads plotted with consistent time axes
- Color-coded traces for inter-lead comparison
- Filtering comparison plots (raw vs. Butterworth vs. Kalman)
- Support for prerecorded CSV datasets (PhysioNet compatible)

### CSV Export Format

Each exported CSV contains:

```
time, lead_I, lead_II, lead_III, aVR, aVL, aVF
```

Separate files are generated for raw and each filtered version, preserving raw data for validation and enabling educational side-by-side comparisons.

---

## Signal Processing Methods

ECG signals are low-amplitude biopotentials (0.5–5 mV) that are highly susceptible to:
- **Baseline wander** (< 0.5 Hz) — from respiration or electrode movement
- **Muscle artifacts (EMG)** — broadband noise above 20 Hz
- **Powerline interference** — 60 Hz hum from electrical environment
- **Motion artifacts** — impedance changes from movement

The following filtering methods are implemented and compared:

### Bandpass Filter
- **Type:** 4th-order IIR
- **Passband:** 0.5 – 40 Hz (covers P wave, QRS complex, and T wave)
- **Purpose:** Removes baseline drift and high-frequency noise as a first-stage conditioning step
- **SNR Improvement:** +8 dB over raw signal

### Butterworth Filter
- **Type:** 4th-order Butterworth bandpass with zero-phase (forward-backward) filtering
- **Purpose:** Maximally flat passband response — preserves waveform morphology with minimal ripple
- **Use Case:** Good general-purpose ECG conditioning when waveform shape preservation matters
- **SNR Improvement:** +10 dB over raw signal

### Chebyshev Notch Filter (60 Hz)
- **Type:** Chebyshev Type I stopband (59–61 Hz)
- **Purpose:** Selective suppression of powerline interference without distorting nearby ECG components
- **Note:** Sharper roll-off than Butterworth for the same filter order

### Kalman Filter *(Best Performing)*
- **Type:** Discrete-time recursive state estimator
- **Purpose:** Adaptively estimates the true ECG signal in the presence of measurement noise
- **Strength:** Preserves low-amplitude P waves and T waves better than fixed-coefficient filters
- **SNR Improvement:** +12 dB over raw signal — highest of all methods tested
- **Note:** Requires tuning of process and measurement noise covariance parameters

### Adaptive LMS Filter
- **Type:** Least Mean Squares adaptive filter using a 60 Hz reference signal
- **Purpose:** Real-time interference cancellation — adjusts filter weights iteratively
- **Limitation:** In classroom environments with variable, unpredictable noise, LMS showed sensitivity to parameter selection and was less stable than Kalman filtering under real-world conditions

---

## Filter Performance Results

Performance was evaluated using ECG recordings from the [PhysioNet](https://physionet.org/) database with SNR as the primary metric.

| Filter | SNR Improvement | RMS Noise | QRS Visibility |
|--------|----------------|-----------|----------------|
| Raw ECG | 0 dB | High | Poor |
| Bandpass | +8 dB | Medium | Good |
| Butterworth | +10 dB | Low | Good |
| **Kalman** | **+12 dB** | **Very Low** | **Excellent** |

The Kalman filter produced the cleanest waveforms with the best preservation of all cardiac cycle components (P wave, QRS complex, and T wave), making it the most effective method for educational demonstration.

---

## Repository Structure

```
portable-ecg-education/
├── arduino/
│   └── ecg_acquisition.ino       # Arduino firmware for ADC sampling and serial output
├── matlab/
│   ├── acquire_ecg.m             # Serial acquisition and data collection script
│   ├── filter_ecg.m              # Butterworth, Chebyshev, Kalman, LMS filter implementations
│   └── export_csv.m              # CSV export for all leads and filter outputs
├── python/
│   ├── visualize_ecg.py          # Six-lead ECG visualization
│   └── compare_filters.py        # Side-by-side filter comparison plots
├── data/
│   └── sample_ecg.csv            # Example PhysioNet ECG dataset for testing
├── hardware/
│   ├── schematics/               # Circuit diagrams and wiring layouts
│   └── enclosure/                # 3D print files for the device enclosure
├── docs/
│   └── report.pdf                # Full project design report
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

**Hardware:**
- Arduino UNO or Nano
- 2× AD8232 ECG Heart Rate Monitor Module
- Ag/AgCl surface electrodes (or compatible snap electrodes)
- USB cable (for power and serial communication)

**Software:**
- [Arduino IDE](https://www.arduino.cc/en/software)
- MATLAB (R2021a or newer recommended)
- Python 3.8+ with the following packages:

```bash
pip install numpy scipy matplotlib pandas
```

### Wiring

| AD8232 Pin | Arduino Pin |
|------------|-------------|
| GND | GND |
| 3.3V | 3.3V |
| OUTPUT (Module 1 — Lead I) | A0 |
| OUTPUT (Module 2 — Lead II) | A1 |
| SDN | D10 (optional, for shutdown) |

Electrode placement follows the standard limb lead configuration:
- **RA** (Right Arm) — Right wrist or shoulder
- **LA** (Left Arm) — Left wrist or shoulder
- **RL** (Right Leg) — Right ankle or lower torso (drive electrode)
- **LL** (Left Leg) — Left ankle or lower torso

---

## Running the System

### Step 1 — Upload Arduino Firmware

```bash
# Open arduino/ecg_acquisition.ino in the Arduino IDE
# Select the correct board and COM port
# Upload the sketch
```

### Step 2 — Run MATLAB Acquisition

```matlab
% In MATLAB, navigate to the /matlab directory
run('acquire_ecg.m')
% A 20-second recording will begin automatically
% Output CSV files are saved to /data/
```

### Step 3 — Visualize in Python

```bash
cd python/
python visualize_ecg.py --input ../data/ecg_output.csv
```

To compare filter outputs side by side:

```bash
python compare_filters.py --input ../data/ecg_output.csv
```

---

## Future Development

Current limitations and planned improvements:

- **Open-Source Pipeline:** Migrate MATLAB acquisition scripts to Python (NumPy, SciPy, Pandas) to eliminate the need for a licensed MATLAB environment and improve accessibility for students
- **Browser-Based Visualization:** Implement real-time ECG streaming via the Web Serial API — no installation required, deployable on GitHub Pages
- **12-Lead Expansion:** Add additional electrode channels and physical lead measurements for a full 12-lead system
- **Custom PCB Design:** Replace breadboard prototype with a compact, manufacturable PCB for mass outreach deployment
- **Wireless Connectivity:** Bluetooth or Wi-Fi streaming to mobile devices or tablets

**Example Web Serial API Integration:**

```javascript
const port = await navigator.serial.requestPort();
await port.open({ baudRate: 115200 });

const reader = port.readable.getReader();

while (true) {
  const { value } = await reader.read();
  // Parse and render ECG samples in real time
}
```

---

## Contributors

**Group 07 — UCSD Bioengineering Senior Design**

| Name |
|------|
| Joe Borovoy |
| John Gunay |
| Marly Roufaeil |
| Ali Testa |
| Jaden Vanderpol |
| Austin Wong |

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

You are free to use, modify, and distribute this project. Any redistributed or modified versions must also be released under GPL-3.0.

See the [`LICENSE`](LICENSE) file for full license text.