
# ECG Acquisition System — Language Translation Plan
### Source: `ecg_acquisition_master_V1.m`
> This document outlines how the MATLAB ECG acquisition and processing pipeline would be 
> re-implemented in **Python**, **Java**, and as a **Web Application**. Each section covers 
> architecture decisions, library choices, pseudocode, and execution strategy.

---

## Table of Contents
1. [System Overview](#system-overview)
2. [MATLAB Pipeline Breakdown](#matlab-pipeline-breakdown)
3. [Translation to Python](#translation-to-python)
4. [Translation to Java](#translation-to-java)
5. [Translation to Web Application](#translation-to-web-application)
6. [Cross-Language Comparison](#cross-language-comparison)
7. [Recommended Path Forward](#recommended-path-forward)

---

## System Overview

The MATLAB script performs the following high-level tasks:

| Step | Description |
|------|-------------|
| 1 | Connect to Arduino via Serial port |
| 2 | Record raw ECG data (Lead I + Lead II) for N seconds |
| 3 | Derive additional leads (III, aVR, aVL, aVF) |
| 4 | Estimate sampling rate and detect heart rate (BPM) |
| 5 | Apply 5 different signal filters |
| 6 | Save all data to organized run folders as CSVs |
| 7 | Plot a 6-lead ECG figure |

The system reads **two raw leads** from an Arduino over serial (115200 baud) and 
mathematically derives the remaining four standard limb leads.

---

## MATLAB Pipeline Breakdown

### Data Acquisition
```matlab
s = serialport(port, baud);
line = readline(s);
values = str2double(split(line, ","));  % expects "val1,val2\n"
```
The Arduino sends comma-separated pairs. The script collects them into a Nx2 matrix.

### Lead Derivation (Einthoven's Law)
```
Lead III = Lead II - Lead I
aVR      = -(Lead I + Lead II) / 2
aVL      =   Lead I - Lead II / 2
aVF      =   Lead II - Lead I / 2
```

### Heart Rate Detection
- Uses `findpeaks()` on Lead II
- MinPeakDistance = 0.4 × Fs (prevents double-counting)
- MinPeakHeight = mean + 1 std deviation
- HR = 60 / mean(RR intervals)

### Filters Applied
| Filter | Type | Purpose |
|--------|------|---------|
| Bandpass IIR | 0.5–40 Hz | Remove DC drift and high-freq noise |
| Butterworth | 0.5–40 Hz | Smoother roll-off bandpass |
| Chebyshev Notch | 59–61 Hz | Remove 60 Hz powerline interference |
| Simple Kalman | Custom | Recursive state estimation smoothing |
| LMS Adaptive | Custom | Adaptive powerline noise cancellation |

---

## Translation to Python

### Recommended Libraries

| MATLAB Function | Python Equivalent |
|----------------|-------------------|
| `serialport()` | `pyserial` (`serial.Serial`) |
| `filtfilt()` | `scipy.signal.filtfilt` |
| `designfilt()` | `scipy.signal.iirfilter` / `butter` |
| `findpeaks()` | `scipy.signal.find_peaks` |
| `writetable()` | `pandas.DataFrame.to_csv()` |
| `subplot/plot` | `matplotlib.pyplot` |
| `cheby1()` | `scipy.signal.cheby1` |

### Project Structure
```
ecg_python/
├── main.py                  # Entry point, orchestrates everything
├── acquisition.py           # Serial port reading
├── leads.py                 # Lead derivation math
├── heart_rate.py            # Peak detection and BPM calculation
├── filters/
│   ├── bandpass.py
│   ├── butterworth.py
│   ├── chebyshev_notch.py
│   ├── kalman.py
│   └── adaptive_lms.py
├── storage.py               # Folder creation and CSV writing
├── plotting.py              # Matplotlib 6-lead figure
└── requirements.txt
```

### Pseudocode

#### `main.py`
```
IMPORT all modules

SET port = "COM5", baud = 115200, record_time = 20

run_folder = storage.create_run_folder(base_dir=current_directory)

raw_data = acquisition.record(port, baud, record_time)
    → returns Nx2 numpy array

[lead_I, lead_II] = raw_data columns 0 and 1
Fs = len(lead_I) / record_time
t  = numpy.linspace(0, record_time, len(lead_I))

[lead_III, aVR, aVL, aVF] = leads.derive(lead_I, lead_II)

HR = heart_rate.calculate(lead_II, Fs)
PRINT "Heart Rate: {HR} BPM"

storage.save_raw_csv(run_folder, t, lead_I, lead_II, lead_III, aVR, aVL, aVF)

FOR each filter in [bandpass, butterworth, chebyshev, kalman, lms]:
    filtered_I, filtered_II = filter.apply(lead_I, lead_II, Fs)
    storage.save_filtered_csv(run_folder, filter.name, t, filtered_I, filtered_II)

plotting.plot_6lead(t, lead_I, lead_II, lead_III, aVR, aVL, aVF)
```

#### `acquisition.py`
```
FUNCTION record(port, baud, duration):
    OPEN serial connection on port at baud rate
    FLUSH buffer
    
    data = empty list
    start = current time
    
    WHILE elapsed time < duration:
        line = READ one line from serial
        values = SPLIT line by "," and CONVERT to float
        
        IF len(values) == 2 AND neither value is NaN:
            APPEND values to data
    
    CLOSE serial connection
    RETURN numpy array of data
```

#### `leads.py`
```
FUNCTION derive(lead_I, lead_II):
    lead_III = lead_II - lead_I
    aVR      = -(lead_I + lead_II) / 2
    aVL      = lead_I - (lead_II / 2)
    aVF      = lead_II - (lead_I / 2)
    RETURN lead_III, aVR, aVL, aVF
```

#### `heart_rate.py`
```
FUNCTION calculate(lead_II, Fs):
    min_distance = 0.4 * Fs          # samples between peaks
    min_height   = mean(lead_II) + std(lead_II)
    
    peaks, properties = scipy.signal.find_peaks(
        lead_II,
        distance=min_distance,
        height=min_height
    )
    
    RR_intervals = diff(peaks) / Fs  # in seconds
    HR = 60 / mean(RR_intervals)
    RETURN HR
```

#### `filters/kalman.py`
```
FUNCTION simple_kalman(signal):
    Q = 0.01   # process noise
    R = 0.1    # measurement noise
    P = 1.0    # estimate error
    X = 0.0    # initial state
    output = array of zeros same size as signal
    
    FOR each sample k in signal:
        P = P + Q                    # predict
        K = P / (P + R)              # Kalman gain
        X = X + K * (signal[k] - X) # update state
        P = (1 - K) * P             # update error
        output[k] = X
    
    RETURN output
```

#### `filters/adaptive_lms.py`
```
FUNCTION lms_filter(signal, reference):
    mu = 0.01    # step size / learning rate
    w  = 0.0     # adaptive weight
    output = array of zeros same size as signal
    
    FOR each sample n:
        output[n] = signal[n] - w * reference[n]
        w = w + mu * output[n] * reference[n]
    
    RETURN output
```

### Python-Specific Notes
- Use `numpy` arrays throughout — avoid Python lists in the signal loops for performance
- Use `scipy.signal.filtfilt` for zero-phase filtering (matches MATLAB's `filtfilt`)
- The Chebyshev notch uses `cheby1(4, 1, [59, 61], btype='bandstop', fs=Fs)`
- Generate the noise reference with: `noise_ref = numpy.sin(2 * pi * 60 * t)`
- Use `pathlib.Path` for all folder/file operations instead of `os.path`

---

## Translation to Java

### Recommended Libraries

| Need | Java Library |
|------|-------------|
| Serial Communication | `jSerialComm` or `RXTX` |
| Signal Processing | `Apache Commons Math` (for FFT, stats) |
| CSV Writing | `OpenCSV` or plain `BufferedWriter` |
| Plotting | `JFreeChart` |
| Matrix math | `EJML` (Efficient Java Matrix Library) |

### Project Structure
```
ecg-java/
├── src/main/java/ecg/
│   ├── Main.java
│   ├── acquisition/
│   │   └── SerialReader.java
│   ├── signal/
│   │   ├── LeadDerivation.java
│   │   ├── HeartRateDetector.java
│   │   └── filters/
│   │       ├── BandpassFilter.java
│   │       ├── ButterworthFilter.java
│   │       ├── ChebyshevNotchFilter.java
│   │       ├── KalmanFilter.java
│   │       └── LMSAdaptiveFilter.java
│   ├── storage/
│   │   ├── RunFolderManager.java
│   │   └── CSVWriter.java
│   └── plotting/
│       └── ECGPlotter.java
├── pom.xml  (Maven) or build.gradle (Gradle)
```

### Pseudocode

#### `Main.java`
```
CLASS Main:
    MAIN METHOD:
        config = load settings (port, baud, recordTime)
        
        runFolder = RunFolderManager.createNext(baseDirectory)
        
        SerialReader reader = new SerialReader(port, baud)
        double[][] rawData   = reader.record(recordTime)
        
        double[] leadI  = rawData column 0
        double[] leadII = rawData column 1
        double   Fs     = rawData.length / recordTime
        double[] t      = linspace(0, recordTime, rawData.length)
        
        LeadDerivation derived = LeadDerivation.compute(leadI, leadII)
        
        double HR = HeartRateDetector.calculate(leadII, Fs)
        System.out.println("Heart Rate: " + HR + " BPM")
        
        CSVWriter.writeRaw(runFolder, t, leadI, leadII, derived)
        
        FOR each FilterStrategy filter : getAllFilters():
            double[] fI  = filter.apply(leadI, Fs)
            double[] fII = filter.apply(leadII, Fs)
            CSVWriter.writeFiltered(runFolder, filter.getName(), t, fI, fII, Fs)
        
        ECGPlotter.plot6Lead(t, leadI, leadII, derived)
```

#### `SerialReader.java`
```
CLASS SerialReader:
    CONSTRUCTOR(port, baud):
        OPEN serial port via jSerialComm
        SET baud rate
        SET read timeout
    
    METHOD record(duration) → double[][]:
        data = new ArrayList
        startTime = System.currentTimeMillis()
        
        WHILE elapsed < duration * 1000:
            line = readLine from serial input stream
            parts = line.split(",")
            
            IF parts.length == 2:
                val1 = parseDouble(parts[0])
                val2 = parseDouble(parts[1])
                IF both are valid numbers:
                    data.add([val1, val2])
        
        CLOSE port
        RETURN data as 2D double array
```

#### `LeadDerivation.java`
```
CLASS LeadDerivation:
    double[] III, aVR, aVL, aVF
    
    STATIC METHOD compute(leadI, leadII) → LeadDerivation:
        result = new LeadDerivation()
        FOR each index i:
            result.III[i] = leadII[i] - leadI[i]
            result.aVR[i] = -(leadI[i] + leadII[i]) / 2.0
            result.aVL[i] = leadI[i] - (leadII[i] / 2.0)
            result.aVF[i] = leadII[i] - (leadI[i] / 2.0)
        RETURN result
```

#### `KalmanFilter.java`
```
CLASS KalmanFilter IMPLEMENTS FilterStrategy:
    METHOD apply(signal, Fs) → double[]:
        Q = 0.01, R = 0.1, P = 1.0, X = 0.0
        output = new double[signal.length]
        
        FOR i = 0 TO signal.length - 1:
            P = P + Q
            K = P / (P + R)
            X = X + K * (signal[i] - X)
            P = (1 - K) * P
            output[i] = X
        
        RETURN output
    
    METHOD getName() → String:
        RETURN "kalman_filtered"
```

#### `HeartRateDetector.java`
```
CLASS HeartRateDetector:
    STATIC METHOD calculate(leadII, Fs) → double:
        mean   = computeMean(leadII)
        stdDev = computeStdDev(leadII)
        
        minPeakHeight    = mean + stdDev
        minPeakSamples   = (int)(0.4 * Fs)
        
        peaks = findPeaks(leadII, minPeakHeight, minPeakSamples)
            // Iterate through array, track local maxima
            // Enforce minimum distance between accepted peaks
        
        IF peaks.size() < 2: RETURN -1  // not enough data
        
        totalRR = 0
        FOR i = 1 TO peaks.size() - 1:
            totalRR += (peaks[i] - peaks[i-1]) / Fs
        
        avgRR = totalRR / (peaks.size() - 1)
        RETURN 60.0 / avgRR
```

### Java-Specific Notes
- Implement a `FilterStrategy` interface with `apply(double[] signal, double Fs)` 
  and `getName()` methods — makes adding new filters trivial
- Butterworth and Chebyshev IIR filter design requires implementing the bilinear 
  transform; use `Apache Commons Math` for polynomial root finding, or pre-compute 
  coefficients in Python and hard-code them as constants for a fixed Fs
- `filtfilt` (zero-phase) must be implemented manually: forward pass, reverse the 
  output, forward pass again, reverse again
- Consider using `ExecutorService` for concurrent filtering of all 5 filters
- Use `JFreeChart` with `XYLineAndShapeRenderer` for the 6-lead subplot layout

---

## Translation to Web Application

### Architecture Decision

A web app requires splitting the system into two parts:

```
[Browser / Frontend]  ←HTTP/WebSocket→  [Backend Server]  ←Serial→  [Arduino]
```

The browser **cannot** access serial ports directly in most cases.  
**Exception:** Chrome's Web Serial API allows direct browser-to-serial communication 
(no backend needed), but has limited browser support.

### Recommended Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript |
| Charting | Chart.js or Plotly.js |
| Signal Processing (client) | DSP.js or math.js |
| Backend | Python (FastAPI) or Node.js (Express) |
| Serial Bridge | Python `pyserial` or Node `serialport` |
| Real-time comms | WebSocket (`socket.io` or native WS) |
| File export | Browser `Blob` API / backend file write |

### Option A — Python FastAPI Backend (Recommended)

#### Project Structure
```
ecg-webapp/
├── backend/
│   ├── main.py              # FastAPI app + WebSocket server
│   ├── acquisition.py       # pyserial reader
│   ├── leads.py             # Lead derivation
│   ├── filters.py           # All 5 filters (scipy)
│   ├── heart_rate.py        # Peak detection
│   └── storage.py           # Run folder + CSV writing
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ECGChart.tsx       # Live scrolling chart
│   │   │   ├── LeadSelector.tsx   # Toggle which leads to view
│   │   │   ├── FilterSelector.tsx # Choose active filter
│   │   │   ├── HRDisplay.tsx      # BPM readout
│   │   │   └── ExportPanel.tsx    # Download CSVs
│   │   └── hooks/
│   │       └── useWebSocket.ts    # WebSocket data stream hook
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

#### Backend Pseudocode (`main.py`)
```
IMPORT FastAPI, WebSocket, pyserial, filters, leads, heart_rate

APP = FastAPI()
ACTIVE_CONNECTIONS = []

ENDPOINT GET /runs:
    RETURN list of all RUN_XXX folders and their CSV files

ENDPOINT GET /runs/{run_id}/download/{filename}:
    RETURN file as download response

ENDPOINT POST /start:
    BODY: { port, baud, duration }
    
    START background task:
        open serial connection
        FOR each line read:
            parse "val1,val2"
            derive all 6 leads
            estimate HR
            apply selected filter
            BROADCAST to all WebSocket clients:
                {
                  timestamp, 
                  leadI, leadII, leadIII, aVR, aVL, aVF,
                  hr,
                  filtered_I, filtered_II
                }
        
        AFTER recording ends:
            save all CSVs to run folder
            BROADCAST { event: "recording_complete", run_id }

ENDPOINT WebSocket /ws:
    ACCEPT connection
    ADD to ACTIVE_CONNECTIONS
    KEEP alive until disconnect
    REMOVE from ACTIVE_CONNECTIONS on close
```

#### Frontend Pseudocode (`App.tsx`)
```
COMPONENT App:
    STATE: isRecording, heartRate, selectedFilter, leadData[], runHistory[]
    
    ON MOUNT:
        connect WebSocket to ws://localhost:8000/ws
        
        ON message received:
            IF event == "sample":
                APPEND new data point to leadData ring buffer (keep last 5s)
                UPDATE heartRate display
            IF event == "recording_complete":
                FETCH updated run history from /runs
    
    RENDER:
        <Header showing connection status and BPM>
        
        <ControlPanel>
            port input, duration input
            <StartButton onClick → POST /start />
            <FilterSelector onChange → set selectedFilter />
        </ControlPanel>
        
        <ECGChart 
            data=leadData 
            leads=["I","II","III","aVR","aVL","aVF"]
            scrolling=true
        />
        
        <RunHistory runs=runHistory>
            FOR each run: show download links for each CSV
        </RunHistory>
```

#### `ECGChart.tsx` Pseudocode
```
COMPONENT ECGChart({ data, leads }):
    USE canvas ref for Chart.js or Plotly
    RING BUFFER of last N seconds of data (N = 5 by default)
    
    ON data change:
        UPDATE each lead's dataset in chart
        CALL chart.update("none")  // no animation for real-time
    
    RENDER 6 stacked line charts, one per lead
    Each chart:
        - X axis: time (seconds, scrolling window)
        - Y axis: amplitude (mV)
        - Color coded per lead
        - Grid lines at standard ECG intervals
```

### Option B — Web Serial API (No Backend, Chrome Only)
```
IF user is on Chrome AND grants serial permission:
    
    port = await navigator.serial.requestPort()
    await port.open({ baudRate: 115200 })
    
    reader = port.readable.getReader()
    
    WHILE recording:
        { value, done } = await reader.read()
        line = decode value as UTF-8 text
        [val1, val2] = parse CSV line
        
        derive leads, calculate HR, apply JS filter
        update chart in real time
    
    EXPORT: generate CSV in-browser using Blob API and trigger download
```

> ⚠️ Web Serial API works in Chrome/Edge only. Not supported in Firefox or Safari.  
> For a production tool, use **Option A** (backend bridge).

### Signal Processing in JavaScript
```
// Butterworth bandpass — pre-compute coefficients server-side 
// and send to frontend, then apply via biquad cascade in JS

FUNCTION applyBiquadFilter(signal, b_coeffs, a_coeffs):
    output = []
    FOR each sample:
        y = b[0]*x[n] + b[1]*x[n-1] + b[2]*x[n-2]
              - a[1]*y[n-1] - a[2]*y[n-2]
        APPEND y to output
    RETURN output

// Kalman — runs identically to MATLAB/Python logic, just in JS
FUNCTION simpleKalman(signal):
    Q=0.01, R=0.1, P=1, X=0
    RETURN signal.map(sample => {
        P = P + Q
        K = P / (P + R)
        X = X + K * (sample - X)
        P = (1 - K) * P
        RETURN X
    })

// LMS Adaptive
FUNCTION lmsFilter(signal, reference):
    mu=0.01, w=0
    RETURN signal.map((sample, n) => {
        y = sample - w * reference[n]
        w = w + mu * y * reference[n]
        RETURN y
    })
```

---

## Cross-Language Comparison

| Feature | Python | Java | Web App |
|---------|--------|------|---------|
| Serial I/O | `pyserial` ✅ easy | `jSerialComm` ✅ | Backend only ⚠️ |
| Signal Filters | `scipy` ✅ direct port | Manual or Apache Math ⚠️ | JS or server-side ⚠️ |
| IIR Filter Design | `scipy.signal` ✅ | Bilinear transform manually ❌ hard | Pre-compute coefficients ⚠️ |
| `filtfilt` (zero-phase) | Built-in ✅ | Manual implementation needed ⚠️ | Forward pass only or server ⚠️ |
| Peak Detection | `scipy.signal.find_peaks` ✅ | Custom loop ⚠️ | JS DSP libraries ⚠️ |
| Plotting | `matplotlib` ✅ | `JFreeChart` ✅ | `Chart.js/Plotly.js` ✅ |
| CSV Export | `pandas` ✅ | `OpenCSV` ✅ | `Blob` API ✅ |
| Real-time Streaming | Threading ✅ | Threads ✅ | WebSocket ✅ |
| Run Folder Logic | `pathlib` ✅ | `java.nio.file` ✅ | Backend only ✅ |
| Deployment Difficulty | 🟢 Low | 🟡 Medium | 🔴 High |
| Closest to MATLAB behavior | 🥇 Python | 🥈 Java | 🥉 Web |

---

## Recommended Path Forward

### If you want the fastest working translation:
> **→ Python**  
> SciPy's signal processing API is nearly 1:1 with MATLAB. The translation is 
> mechanical and every MATLAB function has a direct equivalent. Estimated effort: 
> **1–2 days** for a working port.

### If you want a standalone desktop application:
> **→ Java**  
> Package with Maven and a JFreeChart UI. More work for filter design, but produces 
> a self-contained `.jar` that runs anywhere with a JVM. Estimated effort: **1–2 weeks**.

### If you want a shareable, multi-user clinical tool:
> **→ Web App (FastAPI backend + React frontend)**  
> The Python backend reuses your Python translation almost entirely. The frontend 
> adds real-time visualization and download management. Estimated effort: **2–4 weeks**.

---

### Suggested First Steps (Any Language)

1. **Validate serial data format** — confirm Arduino sends `"val1,val2\n"` reliably
2. **Port lead derivation math first** — it's pure arithmetic, no library dependencies
3. **Port Kalman and LMS next** — they're custom loops, language-agnostic
4. **Tackle IIR filters last** — most library-dependent and language-specific
5. **Add HR detection** — requires a working peak finder
6. **Wire up serial I/O** — platform and OS dependent, test early
7. **Add plotting/UI last** — don't block core logic on visualization

---

*Generated from analysis of `ecg_acquisition_master_V1.m`*  
*Source pipeline: Arduino → Serial → MATLAB → 6-lead ECG + 5 filters + HR + CSV export*
