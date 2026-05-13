# Portable ECG Educational Platform

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Project: ECG](https://img.shields.io/badge/Project-ECG-green)
![Hardware: Arduino](https://img.shields.io/badge/Hardware-Arduino-orange)
![UCSD Bioengineering](https://img.shields.io/badge/UCSD-Bioengineering-blue)

A portable, low-cost electrocardiogram (ECG) system designed for educational outreach and biomedical engineering instruction. Built as a UCSD Bioengineering (2025 - 2026) senior design project, the system allows students to safely observe, interact with, and interpret real-time cardiac electrical signals in classroom and outreach environments.

> **Special thanks** to Dr. Pedro Cabrales, Dr. Taylor Amos, and Iris Zaretzki for their guidance, mentorship, and support throughout this project.

---
Visit our project website and reference documentation for full project details and outreach resources:

- Website: [UCSD Portable ECG Project](https://sites.google.com/view/ucsd-project-7-portable-ecg)
- References: [Project resources and documentation](https://sites.google.com/view/ucsd-project-7-portable-ecg/resources-documentation/reference)

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
    - [Enclosure \& Safety Validation](#enclosure--safety-validation)
  - [Software Pipeline](#software-pipeline)
    - [1. Arduino Firmware (`firmware/active_code/arduino_firmware/ECG_arduino_code.ino`)](#1-arduino-firmware-firmwareactive_codearduino_firmwareecg_arduino_codeino)
    - [2. MATLAB Acquisition Script (`firmware/active_code/matlab_acquisition/`)](#2-matlab-acquisition-script-firmwareactive_codematlab_acquisition)
    - [3. Python Visualization (`firmware/active_code/python_visualization/` and beyond)](#3-python-visualization-firmwareactive_codepython_visualization-and-beyond)
    - [CSV Export Format](#csv-export-format)
  - [Signal Processing Methods](#signal-processing-methods)
    - [Bandpass Filter](#bandpass-filter)
    - [Butterworth Filter *(Most Reliable in Outreach)*](#butterworth-filter-most-reliable-in-outreach)
    - [Chebyshev Notch Filter (60 Hz)](#chebyshev-notch-filter-60-hz)
    - [Kalman Filter *(Best in Controlled Tests)*](#kalman-filter-best-in-controlled-tests)
    - [Adaptive LMS Filter](#adaptive-lms-filter)
  - [Filter Performance Results](#filter-performance-results)
    - [Controlled Environment (PhysioNet Database)](#controlled-environment-physionet-database)
    - [Real-World Classroom Environment](#real-world-classroom-environment)
  - [Repository Structure](#repository-structure)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Wiring](#wiring)
  - [Running the System](#running-the-system)
    - [Step 1 — Upload Arduino Firmware](#step-1--upload-arduino-firmware)
    - [Step 2 — Run MATLAB Acquisition \& Filtering](#step-2--run-matlab-acquisition--filtering)
    - [Step 3 — Visualize in Python](#step-3--visualize-in-python)
  - [Educational Outreach](#educational-outreach)
  - [Future Development](#future-development)
    - [Regulatory \& Risk Considerations](#regulatory--risk-considerations)
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

### Enclosure & Safety Validation

A **3D-printed enclosure** houses the Arduino, AD8232 modules, and battery supply, providing:
- **Electrical isolation** — Protects electrodes and participants from inadvertent contact with circuitry
- **Durability** — Weatherproof casing suitable for frequent handling during outreach events
- **Color-coded connectors** — Simplifies electrode placement for students (RA, LA, RL, LL identification)
- **Self-test mode** — Onboard reference signal for system validation without requiring participants

**Safety Verification:**
- Leakage current measured at **<10 µA** (well below IEC 60601-1 limits of 100 µA for clinical devices)
- Battery-powered operation ensures galvanic isolation from wall power
- All exposed metal surfaces are covered or insulated
- Color-coded labels guide safe electrode placement

---

## Software Pipeline

The system integrates three computational layers:

1. **Embedded Acquisition** — Arduino firmware samples ECG signals at ~500 Hz
2. **Signal Processing** — MATLAB applies digital filtering (Butterworth, Kalman, Chebyshev, LMS)
3. **Visualization** — Python renders waveforms for analysis and outreach demos

### 1. Arduino Firmware (`firmware/active_code/arduino_firmware/ECG_arduino_code.ino`)

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

### 2. MATLAB Acquisition Script (`firmware/active_code/matlab_acquisition/`)

MATLAB manages the recording session (`ecg_acquisition_master_V1.m`, `ecg_acquisition_master_live_V1.m`, `ecg_acquisition_master_live_V2.m`):

- Opens the serial connection to the Arduino
- Preallocates a fixed-size acquisition buffer (avoids latency from dynamic resizing)
- Records data for a **20-second acquisition window**
- Converts raw ADC values to millivolt-scale ECG signals
- Computes all derived leads (Lead III, aVR, aVL, aVF)
- Applies multiple filtering approaches (Butterworth, Kalman, Chebyshev, LMS adaptive)
- Exports results to structured CSV files

Effective sampling frequency is estimated post-acquisition as:

```
fs_effective = N / T
```

where `N` = total sample count and `T` = recording duration.

### 3. Python Visualization (`firmware/active_code/python_visualization/` and beyond)

Python scripts visualize the six-lead ECG using `ecg_run_analysis.py`:

```bash
pip install numpy scipy matplotlib pandas
python ecg_run_analysis.py
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

### Butterworth Filter *(Most Reliable in Outreach)*
- **Type:** 4th-order Butterworth bandpass with zero-phase (forward-backward) filtering
- **Purpose:** Maximally flat passband response — preserves waveform morphology with minimal ripple
- **Use Case:** Most reliable for real classroom and outreach demonstrations; excellent waveform fidelity in noisy environments
- **SNR Improvement (Classroom): +4.1 dB** over raw signal — consistent, stable performance
- **Note:** Chosen as the standard filter for educational outreach due to predictable behavior and ease of tuning in variable environments

### Chebyshev Notch Filter (60 Hz)
- **Type:** Chebyshev Type I stopband (59–61 Hz)
- **Purpose:** Selective suppression of powerline interference without distorting nearby ECG components
- **Note:** Sharper roll-off than Butterworth for the same filter order

### Kalman Filter *(Best in Controlled Tests)*
- **Type:** Discrete-time recursive state estimator
- **Purpose:** Adaptively estimates the true ECG signal in the presence of measurement noise
- **Strength:** Preserves low-amplitude P waves and T waves better than fixed-coefficient filters
- **SNR Improvement (PhysioNet): +12 dB** over raw signal — highest in controlled laboratory conditions
- **SNR Improvement (Classroom): +2.9 dB** over raw signal — performance degraded due to varied noise characteristics
- **Note:** Excellent for quantitative SNR metrics in stable environments; requires careful tuning of process and measurement noise covariance parameters; can be sensitive to parameter selection in classroom settings with variable noise

### Adaptive LMS Filter
- **Type:** Least Mean Squares adaptive filter using a 60 Hz reference signal
- **Purpose:** Real-time interference cancellation — adjusts filter weights iteratively
- **Limitation:** In classroom environments with variable, unpredictable noise, LMS showed sensitivity to parameter selection and was less stable than Kalman filtering under real-world conditions

---

## Filter Performance Results

### Controlled Environment (PhysioNet Database)

Performance evaluated using curated ECG recordings from the [PhysioNet](https://physionet.org/) database:

| Filter | SNR Improvement | RMS Noise | QRS Visibility |
|--------|----------------|-----------|----------------|
| Raw ECG | 0 dB | High | Poor |
| Bandpass | +8 dB | Medium | Good |
| Butterworth | +10 dB | Low | Good |
| **Kalman** | **+12 dB** | **Very Low** | **Excellent** |
| Chebyshev Notch | +9 dB | Medium | Good |
| LMS Adaptive | +7 dB | Medium | Fair |

Kalman filter achieved the highest SNR improvement in controlled, laboratory conditions.

### Real-World Classroom Environment

When tested during live outreach demonstrations with variable room noise, electrode motion, and EMG interference:

| Filter | SNR Improvement | Stability | Setup Ease | Recommended |
|--------|----------------|-----------|------------|-------------|
| **Butterworth** | **+4.1 dB** | **Excellent** | **Easy** | **✓ Yes** |
| Kalman | +2.9 dB | Variable | Difficult | No |
| Bandpass | +3.2 dB | Good | Easy | Optional |
| Chebyshev Notch | +2.5 dB | Good | Moderate | Supplementary |
| LMS Adaptive | +1.8 dB | Poor | Very Difficult | Not recommended |

**Key Finding:** While Kalman filtering achieves superior SNR in controlled testing, **Butterworth filtering proved most reliable and practical for real-world outreach demonstrations**. The consistent, predictable performance and ease of parameter selection make Butterworth the recommended choice for classroom use.

---

## Repository Structure

Active firmware, scripts, and datasets are organized as follows:

```
portable-ecg-education/
├── firmware/
│   └── active_code/
│       ├── arduino_firmware/
│       │   └── ECG_arduino_code.ino      # Arduino firmware for ADC sampling
│       ├── matlab_acquisition/
│       │   ├── ecg_acquisition_master_V1.m
│       │   ├── ecg_acquisition_master_live_V1.m
│       │   └── ecg_acquisition_master_live_V2.m
│       └── python_visualization/
│           └── ecg_run_analysis.py       # Python analysis and visualization
├── datasets/
│   ├── RUN_001/ ... RUN_010/
│   │   ├── raw_6lead.csv                 # Raw unfiltered ECG
│   │   ├── butterworth_filtered.csv      # Butterworth (4.1 dB SNR improvement)
│   │   ├── kalman_filtered.csv           # Kalman (2.9 dB SNR in classroom)
│   │   ├── chebyshev_notch_filtered.csv  # Chebyshev 60 Hz notch
│   │   └── adaptive_filtered.csv         # LMS adaptive filter output
├── hardware/
│   ├── ad8232_modules/                   # AD8232 module specifications
│   ├── pure_circuit_ecg/                 # Discrete analog design (deprecated)
│   └── 3D_enclosure/                     # STL files for protective enclosure
├── docs/
│   └── [project documentation]
├── future_directions/                    # Planned extensions (Java, Python, Web)
├── LICENSE
├── README.md
└── CITATION.cff
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
# Open firmware/active_code/arduino_firmware/ECG_arduino_code.ino in the Arduino IDE
# Select the correct board (Arduino UNO/Nano) and COM port
# Upload the sketch
```

### Step 2 — Run MATLAB Acquisition & Filtering

```matlab
% In MATLAB, navigate to firmware/active_code/matlab_acquisition/
run('ecg_acquisition_master_V2.m')
% A 20-second recording will begin automatically
% Applies Butterworth, Kalman, Chebyshev, and LMS filters
% Output CSV files are saved to datasets/RUN_XXX/
```

### Step 3 — Visualize in Python

```bash
cd firmware/active_code/python_visualization/
python ecg_run_analysis.py --input ../../datasets/RUN_001/raw_6lead.csv
```

To compare all filter outputs side by side, run the appropriate analysis script on the dataset folder or file path.

This will display raw, Butterworth, Kalman, Chebyshev, and adaptive filtered versions for educational comparison.

---

## Educational Outreach

This system was designed specifically for STEM outreach and classroom demonstrations:

- **Color-coded Electrode Guides:** Visual maps on the enclosure simplify RA, LA, RL, LL placement for students unfamiliar with ECG
- **Interactive Live Visualization:** Python GUI displays real-time six-lead ECG with live filtering demonstrations
- **Pre/Post Knowledge Surveys:** IRB-approved assessment tools measure student learning gains on cardiac physiology concepts
- **Self-Test Mode:** Built-in reference signal allows system validation without requiring human subjects
- **Outreach Events Completed:**
  - 15+ live demonstrations with 200+ students across two institutions
  - Engagement feedback: 92% of students found the experience educational and interesting
  - Notable participants: Diverse age groups (high school through undergraduate)
  - Waveform quality: Butterworth filtering consistently produced clear QRS complexes even with motion artifacts

---

## Future Development

Current limitations and planned improvements:

- **Open-Source Pipeline:** Migrate MATLAB acquisition scripts to Python (NumPy, SciPy, Pandas) to eliminate the need for a licensed MATLAB environment and improve accessibility for students
- **Browser-Based Visualization:** Implement real-time ECG streaming via the Web Serial API — no installation required, deployable on GitHub Pages
- **12-Lead Expansion:** Add additional electrode channels and physical lead measurements for a full 12-lead system
- **Custom PCB Design:** Replace breadboard prototype with a compact, manufacturable PCB for mass outreach deployment
- **Wireless Connectivity:** Bluetooth or Wi-Fi streaming to mobile devices or tablets

### Regulatory & Risk Considerations

As this platform scales beyond educational prototyping, the following regulatory and safety aspects should be addressed:

- **Regulatory Compliance:** IEC 60601-1 (General Requirements for Medical Electrical Devices) and IEC 60601-2-25 (Particular Requirements for ECG Equipment)
- **Risk Analysis:** ISO 14971 (Risk Management) assessment of electrical safety, usability hazards, and software stability
- **Clinical Validation:** Formal comparison of reconstructed leads against clinical 12-lead ECG systems (e.g., Welch Allyn CardioPerfect)
- **Longevity Testing:** Durability evaluation of AD8232 modules and battery performance across extended outreach campaigns
- **Software Quality:** Automated test suites for filter implementations to ensure robustness across varying signal conditions

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

**Group 07 — UCSD (2025-2026) Bioengineering Senior Design**

| Name | Linkedin |
|------|------|
| Joe Borovoy | https://www.linkedin.com/in/joseph-borovoy-2818a2261/ |
| John Gunay | https://www.linkedin.com/in/john-gunay-1145932b9/ |
| Marly Roufaeil | https://www.linkedin.com/in/marly-r-8ab772216/ |
| Ali Testa | https://www.linkedin.com/in/aliana-testa-643548256/ |
| Jaden Vanderpol | https://www.linkedin.com/in/jaden-vanderpol-159094283/ |
| Austin Wong | https://www.linkedin.com/in/austinwong-bme/ |

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

You are free to use, modify, and distribute this project. Any redistributed or modified versions must also be released under GPL-3.0.

See the [`LICENSE`](LICENSE) file for full license text.