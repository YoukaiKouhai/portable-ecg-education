# ECG Pipeline — Execution Guide
### How to run the full ECG acquisition and visualization pipeline end-to-end

> This guide walks through every step of the pipeline in order: flashing the Arduino,  
> recording ECG data in MATLAB, and visualizing results in Python.

---

## Table of Contents
1. [Repository File Map](#repository-file-map)
2. [Prerequisites](#prerequisites)
3. [Step 1 — Flash the Arduino](#step-1--flash-the-arduino)
4. [Step 2 — MATLAB Standard Acquisition](#step-2--matlab-standard-acquisition)
5. [Step 3 — MATLAB Live Acquisition (Optional)](#step-3--matlab-live-acquisition-optional)
6. [Step 4 — Python Visualization](#step-4--python-visualization)
7. [Output File Reference](#output-file-reference)
8. [Troubleshooting](#troubleshooting)

---

## Repository File Map

```
firmware/
└── active_code/
    ├── arduino_firmware/
    │   └── ECG_arduino_code/
    │       └── ECG_arduino_code.ino          ← Flash this to Arduino first
    │
    ├── matlab_acquisition/
    │   ├── ecg_acquisition_master_V1.m       ← Standard 20-sec recording
    │   ├── ecg_acquisition_master_live_V1.m  ← Live scrolling window
    │   └── ecg_acquisition_master_live_V2.m  ← Live + custom UI (WIP)
    │
    └── python_visualization/
        └── ecg_run_analysis.py               ← Visualize saved CSV runs
```

---

## Prerequisites

### Hardware Required
- Arduino (Uno, Mega, or compatible) with ECG front-end circuit
- ECG electrodes (minimum 3: RA, LA, LL) attached to the circuit
- USB cable connecting Arduino to computer

### Software Required

| Software | Version | Purpose |
|----------|---------|---------|
| Arduino IDE | 2.x recommended | Flash firmware to Arduino |
| MATLAB | R2021a or newer | Data acquisition and filtering |
| Python | 3.8+ | Post-run visualization |

### Python Packages Required
Install before running the Python visualization script:
```bash
pip install pandas matplotlib scipy numpy
```

---

## Step 1 — Flash the Arduino

> **Do this once.** You only need to re-flash if the firmware changes.

### 1.1 Open the Firmware
1. Launch **Arduino IDE**
2. Go to `File` → `Open`
3. Navigate to and open:
   ```
   firmware/active_code/arduino_firmware/ECG_arduino_code/ECG_arduino_code.ino
   ```

### 1.2 Select Your Board and Port
1. Go to `Tools` → `Board` → select your Arduino model (e.g., **Arduino Uno**)
2. Go to `Tools` → `Port` → select the COM port your Arduino is connected to
   - **Windows:** Will appear as `COM3`, `COM4`, `COM5`, etc.
   - **Mac/Linux:** Will appear as `/dev/ttyUSB0` or `/dev/cu.usbmodem...`
   - If you don't see a port, check your USB cable and driver installation

### 1.3 Upload the Firmware
1. Click the **Upload** button (→ arrow icon) or press `Ctrl+U` (`Cmd+U` on Mac)
2. Wait for the IDE to compile and upload
3. Confirm you see:
   ```
   Done uploading.
   ```
   in the bottom status bar — **this means the firmware is live on the Arduino**

### 1.4 Verify Serial Output (Optional but Recommended)
1. Go to `Tools` → `Serial Monitor`
2. Set baud rate to **115200** (bottom-right dropdown of Serial Monitor)
3. You should see a continuous stream of comma-separated values like:
   ```
   512,489
   513,491
   510,488
   ```
   Each line is `Lead_I_raw, Lead_II_raw` sent from the Arduino.
4. **Close the Serial Monitor before proceeding** — MATLAB cannot access the port
   while Serial Monitor is open.

---

## Step 2 — MATLAB Standard Acquisition

> This is the primary recording script. It records **20 seconds** of ECG data,  
> derives all 6 leads, calculates heart rate, applies 5 filters, and saves  
> everything to a new `RUN_###` folder.

### 2.1 Electrode Placement
Before running the script, attach electrodes to the subject:

| Electrode | Placement |
|-----------|-----------|
| **RA** (Right Arm) | Inner right wrist or right forearm |
| **LA** (Left Arm) | Inner left wrist or left forearm |
| **LL** (Left Leg) | Left ankle or left lower leg |

> Ensure good skin contact. Clean the skin with an alcohol wipe and let it dry  
> before applying electrodes. Minimize movement during recording.

### 2.2 Configure the Script
1. Open MATLAB
2. Navigate to the folder:
   ```
   firmware/active_code/matlab_acquisition/
   ```
3. Open `ecg_acquisition_master_V1.m`
4. At the top of the file, update the **USER SETTINGS** section:

```matlab
port = "COM5";        % ← Change to YOUR Arduino COM port
baud = 115200;        % ← Leave this as-is
record_time = 20;     % ← Duration in seconds (default: 20)
```

> **How to find your COM port:** In Arduino IDE, check `Tools` → `Port`.  
> On Mac/Linux, change `"COM5"` to your device path, e.g. `"/dev/ttyUSB0"`.

### 2.3 Run the Script
1. Make sure the Arduino is **plugged in** and Serial Monitor is **closed**
2. Ensure the electrodes are attached and the subject is seated and still
3. In MATLAB, press **F5** or click the **Run** button
4. Watch the MATLAB Command Window — you will see:

```
Saving data to: C:\...\firmware\active_code\matlab_acquisition\RUN_001
Recording...
```

5. The subject should remain **still and calm** for the full 20 seconds
6. When recording is complete you will see:

```
Recording complete.
Estimated Sampling Rate: 487.50 Hz
Estimated Heart Rate: 72.3 BPM
```

### 2.4 What the Script Does Automatically

Once recording finishes, the script runs without any further input:

| Task | Output File |
|------|------------|
| Saves raw 6-lead data | `raw_6lead.csv` |
| Bandpass IIR filter (0.5–40 Hz) | `bandpass_filtered.csv` |
| Butterworth bandpass (0.5–40 Hz) | `butterworth_filtered.csv` |
| Chebyshev notch (60 Hz removal) | `chebyshev_notch_filtered.csv` |
| Kalman filter | `kalman_filtered.csv` |
| LMS adaptive filter | `adaptive_filtered.csv` |
| 6-lead plot | MATLAB figure window |

### 2.5 Output Location

A new folder is created automatically in the same directory as the `.m` file:

```
firmware/active_code/matlab_acquisition/
└── RUN_001/
    ├── raw_6lead.csv
    ├── bandpass_filtered.csv
    ├── butterworth_filtered.csv
    ├── chebyshev_notch_filtered.csv
    ├── kalman_filtered.csv
    └── adaptive_filtered.csv
```

Each subsequent run creates `RUN_002`, `RUN_003`, etc. — **no data is ever overwritten.**

---

## Step 3 — MATLAB Live Acquisition (Optional)

These scripts show the ECG signal in real time while recording. Use them to verify  
electrode contact and signal quality **before** committing to a full standard run.

> Configure `port`, `baud`, and `record_time` at the top of each file the same  
> way as described in Step 2.2.

### Live V1 — Scrolling Window
**File:** `firmware/active_code/matlab_acquisition/ecg_acquisition_master_live_V1.m`

- Displays a **live 5-second scrolling window** of the ECG as it records
- Shows Lead I and Lead II in real time
- Useful for confirming signal quality before a full recording session
- Run identically to the standard script: open in MATLAB, set port, press **F5**

### Live V2 — Custom UI *(Work in Progress)*
**File:** `firmware/active_code/matlab_acquisition/ecg_acquisition_master_live_V2.m`

- Same live scrolling concept as V1 with an added **custom MATLAB UI panel**
- ⚠️ **Currently under development** — some features may be incomplete.
  Use V1 for a reliable live preview.

---

## Step 4 — Python Visualization

After a MATLAB run has completed and a `RUN_###` folder exists, use the Python  
script to load, analyze, and visualize the saved CSV files interactively.

### 4.1 Configure Plot Behaviour (Optional)

At the top of `ecg_run_analysis.py` there is a **USER CONFIGURATION** block.  
Edit these flags before running to control what the script does:

```python
show_plot        = True   # Display plots on screen
save_plots       = True   # Save plots as PNG files into RUN_###/saved_plots/
save_5sec_plots  = False  # Also save every 5-second window as individual PNGs
plot_5_sec_window = False # Show 5-second windowed plots on screen
plot_live_view   = False  # Simulate a scrolling real-time viewer at the end
```

> **Recommended defaults for a first run:** leave everything as-is above.  
> Enable `save_5sec_plots = True` only if you want a detailed per-window  
> archive — it generates many image files (one per 5-second chunk per filter).

### 4.2 Run the Script

The script **must be run from its own directory** so it can find the `RUN_###`  
folders automatically. Open a terminal and run:

```bash
cd firmware/active_code/python_visualization/
python ecg_run_analysis.py
```

> **Note:** The script scans its own directory for `RUN_###` folders.  
> The `RUN_###` folders are created by MATLAB inside `matlab_acquisition/` —  
> **not** the Python folder. You have two options:
> - Copy or move the desired `RUN_###` folder into `python_visualization/` before running, **or**
> - Edit the `BASE_DIR` line near the top of the script to point directly at the  
>   MATLAB acquisition folder:
>   ```python
>   BASE_DIR = r"C:\path\to\firmware\active_code\matlab_acquisition"
>   ```

### 4.3 Interactive Prompts

The script runs interactively. You will be asked two questions in the terminal:

---

#### Prompt 1 — Select a Run

```
Script directory: C:\...\python_visualization

Available Runs:
1. RUN_001
2. RUN_002
3. RUN_003

Select run number or type 'close':
```

Type the **number** next to the run you want to analyze and press Enter.  
Type `close` to exit.

---

#### Prompt 2 — Select a Filter

```
Filter Options:
1 - Raw
2 - Bandpass
3 - Butterworth
4 - Chebyshev Notch
5 - Kalman
6 - Adaptive
a - All Filters
close - Cancel

Choose filter:
```

| Input | What it does |
|-------|-------------|
| `1` | Plots the raw unfiltered 6-lead ECG only |
| `2` | Plots the bandpass-filtered 6-lead ECG only |
| `3` | Plots the Butterworth-filtered 6-lead ECG only |
| `4` | Plots the Chebyshev notch-filtered 6-lead ECG only |
| `5` | Plots the Kalman-filtered 6-lead ECG only |
| `6` | Plots the adaptive (LMS) filtered 6-lead ECG only |
| `a` | Runs **all** of the above, plus a Lead II filter comparison overlay |
| `close` | Exits the script |

> **Recommended:** Use `a` (All Filters) to get the complete picture including  
> the side-by-side filter comparison plot.

---

### 4.4 What the Script Generates

#### For a single filter selection (options 1–6):
- **Full 6-lead plot** — all six leads stacked vertically for the entire recording
  - Lead II shows detected R-peaks marked in red and calculated BPM in the title
  - ECG-style pink grid (major 5 mm, minor 1 mm) applied to all subplots
  - Saved as: `RUN_###/saved_plots/<filter_name>_full.png`

#### For "All Filters" (`a`):
- All six individual full 6-lead plots (one per filter), each saved as PNG
- **Filter Comparison Plot** — Lead II from all 6 filters overlaid on one chart
  for direct visual comparison of noise removal effectiveness
  - Saved as: `RUN_###/saved_plots/RUN_###_filter_comparison.png`

#### If `save_5sec_plots = True`:
- Every 5-second chunk of every filter is saved as an individual PNG into:
  ```
  RUN_###/saved_plots/5_second_windows/
  ```
  Files are named: `<filter>_window_1_0_to_5_sec.png`, `_window_2_5_to_10_sec.png`, etc.
  A 20-second recording produces **4 windows × 6 filters = 24 PNG files**.

#### If `plot_live_view = True`:
- After all plots are shown, a **simulated real-time scrolling viewer** plays back  
  Lead II from the last selected filter in a 3-second sliding window at ~50 fps.

### 4.5 Final Output Folder Structure

After running with `a` and `save_plots = True`:

```
RUN_001/
├── raw_6lead.csv
├── bandpass_filtered.csv
├── butterworth_filtered.csv
├── chebyshev_notch_filtered.csv
├── kalman_filtered.csv
├── adaptive_filtered.csv
└── saved_plots/
    ├── Raw_6-Lead_ECG_(Unfiltered)_full.png
    ├── 6-Lead_ECG_-_Bandpass_Filter_(0.5-40_Hz)_full.png
    ├── 6-Lead_ECG_-_Butterworth_Bandpass_(0.5-40_Hz)_full.png
    ├── 6-Lead_ECG_-_Chebyshev_Notch_Filter_(50_60_Hz_Removal)_full.png
    ├── 6-Lead_ECG_-_Kalman_Filter_(Adaptive_Noise_Reduction)_full.png
    ├── 6-Lead_ECG_-_Adaptive_Filter_full.png
    ├── RUN_001_filter_comparison.png
    └── 5_second_windows/        ← only if save_5sec_plots = True
        ├── ...window_1_0_to_5_sec.png
        ├── ...window_2_5_to_10_sec.png
        └── ...
```

---

## Output File Reference

All CSV files share the same column structure:

| Column | Description |
|--------|-------------|
| `t` | Time in seconds |
| `leadI` | Lead I (raw or filtered) |
| `leadII` | Lead II (raw or filtered) |
| `leadIII` | Derived: Lead II − Lead I |
| `aVR` | Derived: −(Lead I + Lead II) / 2 |
| `aVL` | Derived: Lead I − Lead II / 2 |
| `aVF` | Derived: Lead II − Lead I / 2 |

Lead derivation follows **Einthoven's Law** — only Lead I and Lead II are  
physically measured; all other leads are mathematically calculated.

---

## Troubleshooting

### MATLAB cannot connect to the serial port
- Confirm Arduino IDE Serial Monitor is **closed**
- Confirm no other program (PuTTY, etc.) has the port open
- Double-check the `port` variable matches your actual COM port
- Try unplugging and replugging the USB, then recheck `Tools → Port` in Arduino IDE
- On Windows: confirm the port in Device Manager under `Ports (COM & LPT)`

### Heart rate output is unrealistic (e.g. 200+ BPM or shows 0)
- Poor electrode contact — reapply electrodes, clean skin, ensure firm contact
- Subject was moving during recording — re-run with subject seated and still
- The Python script uses a QRS bandpass (5–15 Hz) + squared signal + adaptive  
  threshold — if the signal amplitude is very low, the threshold may not be crossed

### RUN folder was created but CSV files are missing or empty
- Verify the serial format from Arduino — open Serial Monitor and confirm lines  
  look like `512,489` (two comma-separated integers per line, no extras)
- Check the MATLAB Command Window for any error messages after "Recording..."

### Python script says "No RUN folders found"
- The script looks for `RUN_###` folders in **its own directory**  
  (`python_visualization/`), not the MATLAB folder
- Either copy the `RUN_###` folder there or update `BASE_DIR` in the script  
  to point to `firmware/active_code/matlab_acquisition/`

### Python plots open but Lead II shows "HR: N/A (No peaks detected)"
- Signal may be too noisy — try running again with the Butterworth or  
  Chebyshev filtered CSV instead of raw
- The detection uses a threshold of `mean + 1.5 × std` on the squared,  
  bandpass-filtered signal — very flat or clipped signals will not cross it

### `save_5sec_plots` is enabled but no files appear in `5_second_windows/`
- Confirm **both** `save_plots = True` AND `save_5sec_plots = True` are set —  
  both flags must be `True` for the subfolder and files to be created

---

## Quick-Start Checklist

Use this before every recording session:

- [ ] Arduino is plugged in via USB
- [ ] Arduino firmware has been uploaded (`ECG_arduino_code.ino`)
- [ ] Arduino IDE Serial Monitor is **closed**
- [ ] Electrodes attached: RA (right arm), LA (left arm), LL (left leg)
- [ ] `port` variable in MATLAB script matches current COM port
- [ ] Subject is seated, calm, ready to stay still for 20 seconds
- [ ] Run `ecg_acquisition_master_V1.m` in MATLAB
- [ ] Confirm `RUN_###` folder and CSVs were created
- [ ] Copy `RUN_###` to `python_visualization/` folder (or update `BASE_DIR`)
- [ ] Run `python ecg_run_analysis.py` and follow the prompts
- [ ] Select run → select filter (use `a` for all) → review plots

---

*Pipeline execution guide — covers Arduino firmware through Python visualization*  
*For language translation planning (Python / Java / Web), see `TRANSLATION_PLAN.md`*