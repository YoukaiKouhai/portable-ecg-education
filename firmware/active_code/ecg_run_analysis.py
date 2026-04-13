import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import time

# ===============================
#  USER CONFIGURATION
# ===============================
show_plot = True          # Set to True to display plots, False to only save
save_plots = True         # Set to True to save plots, False to not save
save_5sec_plots = False    # Set to True to save the 5-second window plots into a separate folder
plot_5_sec_window = False 
plot_live_view = False

# ===============================
#  CONFIGURATION
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Script directory:", BASE_DIR)

FILTER_FILES = {
    "1": "raw_6lead.csv",
    "2": "bandpass_filtered.csv",
    "3": "butterworth_filtered.csv",
    "4": "chebyshev_notch_filtered.csv",
    "5": "kalman_filtered.csv",
    "6": "adaptive_filtered.csv"
}

FILTER_NAMES = {
    "1": "Raw Signal",
    "2": "Bandpass Filter",
    "3": "Butterworth Filter",
    "4": "Chebyshev Notch Filter",
    "5": "Kalman Filter",
    "6": "Adaptive Filter"
}


# ===============================
#  FIND AVAILABLE RUNS
# ===============================

runs = sorted([
    f for f in os.listdir(BASE_DIR)
    if f.startswith("RUN_") and os.path.isdir(os.path.join(BASE_DIR, f))
])

if not runs:
    print("No RUN folders found.")
    exit()

print("\nAvailable Runs:")
for i, run in enumerate(runs):
    print(f"{i+1}. {run}")

run_choice = input("\nSelect run number or type 'close': ")

if run_choice.lower() == "close":
    exit()

try:
    run_index = int(run_choice) - 1
    selected_run = runs[run_index]
except:
    print("Invalid selection.")
    exit()

run_path = os.path.join(BASE_DIR, selected_run)

# Create main plots subdirectory for saving
plots_dir = os.path.join(run_path, "saved_plots")
if save_plots and not os.path.exists(plots_dir):
    os.makedirs(plots_dir)
    print(f"Created plots directory: {plots_dir}")

# Create separate folder for 5-second window plots
five_sec_plots_dir = os.path.join(run_path, "saved_plots", "5_second_windows")
if save_5sec_plots and save_plots and not os.path.exists(five_sec_plots_dir):
    os.makedirs(five_sec_plots_dir)
    print(f"Created 5-second windows directory: {five_sec_plots_dir}")

# ===============================
#  FILTER SELECTION
# ===============================

print("\nFilter Options:")
print("1 - Raw")
print("2 - Bandpass")
print("3 - Butterworth")
print("4 - Chebyshev Notch")
print("5 - Kalman")
print("6 - Adaptive")
print("a - All Filters")
print("close - Cancel")

filter_choice = input("\nChoose filter: ")

if filter_choice.lower() == "close":
    exit()


# ===============================
#  PLOTTING FUNCTIONS
# ===============================

def plot_6lead(df, title, save_dir=None, show=True, save=False):
    """
    Plot 6-lead ECG with heart rate detection
    
    Parameters:
    - df: DataFrame with time and lead data
    - title: Plot title
    - save_dir: Directory to save the plot (if None, saves to run_path/plots)
    - show: Boolean to display the plot
    - save: Boolean to save the plot
    """
    t = df.iloc[:, 0]
    lead_names = df.columns[1:]

    # Color mapping in correct lead order
    colors = [
        "blue",     # Lead I
        "red",      # Lead II
        "green",    # Lead III
        "purple",   # aVR
        "orange",   # aVL
        "brown"     # aVF
    ]

    plt.figure(figsize=(12, 10))

    for i in range(6):
        plt.subplot(6, 1, i+1)
        plt.plot(t, df.iloc[:, i+1], color=colors[i], linewidth=1.2)
        plt.ylabel("Amplitude")
        apply_ecg_grid(plt.gca())
        
        if i == 1:  # Lead II used for HR detection
            try:
                peaks, HR = detect_heart_rate(t, df.iloc[:, i+1])
                if len(peaks) > 0:
                    plt.scatter(t.iloc[peaks], df.iloc[peaks, i+1],
                                color="red", zorder=3, s=20)
                    plt.title(f"{lead_names[i]} | HR: {HR:.1f} BPM")
                else:
                    plt.title(f"{lead_names[i]} | HR: N/A (No peaks detected)")
            except Exception as e:
                print(f"Warning: Could not detect heart rate for {title}: {e}")
                plt.title(f"{lead_names[i]} | HR: N/A (Detection error)")
        else:
            plt.title(lead_names[i])

    plt.xlabel("Time (s)")
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save the plot if requested
    if save and save_dir is not None:
        # Create filename from title
        filename = f"{title.replace(' ', '_').replace('/', '_')}_full.png"
        save_path = os.path.join(save_dir, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved full plot to: {save_path}")
    
    # Show the plot if requested
    if show:
        plt.show()
    else:
        plt.close()

def plot_6lead_windows(df, title, window_sec=5, show_plot=True, save_plot=False, save_dir=None):
    """
    Plot 6-lead ECG in time windows (specific windows only: 1, 5, 10, 15 sec)
    
    Parameters:
    - df: DataFrame with time and lead data
    - title: Plot title
    - window_sec: Window size in seconds
    - show_plot: Boolean to display plots
    - save_plot: Boolean to save plots
    - save_dir: Directory to save plots
    """
    t = df.iloc[:, 0]
    lead_names = df.columns[1:]
    colors = ["blue", "red", "green", "purple", "orange", "brown"]

    total_time = t.iloc[-1]
    start_time = 0
    
    # Target windows to save (can be modified)
    target_windows = [1, 5, 10, 15]  # Save these specific windows

    while start_time < total_time:
        end_time = start_time + window_sec
        window_mask = (t >= start_time) & (t < end_time)
        df_window = df[window_mask]

        if df_window.empty:
            start_time += window_sec
            continue

        plt.figure(figsize=(12, 10))

        for i in range(6):
            plt.subplot(6, 1, i+1)
            plt.plot(
                df_window.iloc[:, 0],
                df_window.iloc[:, i+1],
                color=colors[i],
                linewidth=1.2
            )
            plt.title(lead_names[i])
            plt.ylabel("Amplitude")
            plt.grid(True)

        plt.xlabel("Time (s)")
        plt.suptitle(f"{title} | {start_time:.1f}s to {end_time:.1f}s")
        plt.tight_layout()

        # Save logic for specific windows
        if save_plot and save_dir is not None:
            # Check if current window is in target windows (with some tolerance)
            should_save = any(abs(start_time - target) < 0.1 for target in target_windows)
            
            if should_save:
                filename = f"{title.replace(' ', '_').replace('/', '_')}_{int(start_time)}_to_{int(end_time)}_sec.png"
                save_path = os.path.join(save_dir, filename)
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"Saved specific window plot to: {save_path}")

        # Show or close the plot
        if show_plot:
            plt.show()
        else:
            plt.close()

        start_time += window_sec

def plot_all_5sec_windows(df, title, save_dir=None, show_plot=False, save_plot=False):
    """
    Plot and save ALL 5-second windows of the ECG data into a separate folder
    
    Parameters:
    - df: DataFrame with time and lead data
    - title: Base title for plots
    - save_dir: Directory to save plots (should be the 5_second_windows folder)
    - show_plot: Boolean to display plots
    - save_plot: Boolean to save plots
    """
    # Only proceed if save_plot is True
    if not save_plot:
        print("5-second window saving is disabled.")
        return 0
    
    t = df.iloc[:, 0]
    lead_names = df.columns[1:]
    colors = ["blue", "red", "green", "purple", "orange", "brown"]
    
    total_time = t.iloc[-1]
    window_sec = 5
    start_time = 0
    window_count = 0
    
    print(f"\n{'='*60}")
    print(f"SAVING ALL 5-SECOND WINDOWS for {title}")
    print(f"{'='*60}")
    
    while start_time < total_time:
        end_time = start_time + window_sec
        window_mask = (t >= start_time) & (t < end_time)
        df_window = df[window_mask]
        
        if df_window.empty:
            start_time += window_sec
            continue
        
        plt.figure(figsize=(12, 10))
        
        for i in range(6):
            plt.subplot(6, 1, i+1)
            plt.plot(
                df_window.iloc[:, 0],
                df_window.iloc[:, i+1],
                color=colors[i],
                linewidth=1.2
            )
            plt.title(lead_names[i])
            plt.ylabel("Amplitude")
            plt.grid(True)
        
        plt.xlabel("Time (s)")
        window_title = f"{title} | Window {window_count+1}: {start_time:.1f}s to {end_time:.1f}s"
        plt.suptitle(window_title, fontsize=12)
        plt.tight_layout()
        
        # Save the window plot if requested
        if save_plot and save_dir is not None:
            # Create a clean filename
            clean_title = title.replace(' ', '_').replace('/', '_').replace('-', '_')
            filename = f"{clean_title}_window_{window_count+1}_{int(start_time)}_to_{int(end_time)}_sec.png"
            save_path = os.path.join(save_dir, filename)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved window {window_count+1}: {filename}")
        
        # Show or close the plot
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        start_time += window_sec
        window_count += 1
    
    print(f"\n✓ Completed: Saved {window_count} total 5-second windows to:")
    print(f"  {save_dir}")
    print(f"{'='*60}\n")
    return window_count

def detect_heart_rate(t, signal):
    """Detect heart rate from ECG signal with error handling"""
    # Convert to numpy arrays
    t = np.array(t)
    signal = np.array(signal)
    
    # Check for NaN or Inf values
    if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
        print("Warning: Signal contains NaN or Inf values")
        return np.array([]), 0
    
    # Check signal length
    if len(signal) < 50:  # Need at least 50 samples (0.1 seconds at 500Hz)
        print(f"Warning: Signal too short for heart rate detection (length: {len(signal)})")
        return np.array([]), 0
    
    # Remove DC component
    signal = signal - np.mean(signal)
    
    # Sampling rate (try to infer from time vector if possible)
    if len(t) > 1:
        fs = int(1.0 / np.median(np.diff(t))) if np.median(np.diff(t)) > 0 else 500
    else:
        fs = 500  # Default
    
    # Ensure fs is reasonable
    if fs < 100 or fs > 2000:
        print(f"Warning: Unusual sampling rate {fs} Hz, using 500 Hz")
        fs = 500
    
    # Create time array
    time = np.arange(len(signal)) / fs
    
    try:
        # QRS Bandpass Filter (5–15 Hz)
        nyquist = fs / 2
        if 5/nyquist >= 1 or 15/nyquist >= 1:
            print(f"Warning: Filter frequencies out of range (fs={fs}Hz)")
            return np.array([]), 0
        
        b, a = butter(2, [5/nyquist, 15/nyquist], btype='band')
        
        # Check if signal is long enough for filtfilt
        padlen = 3 * max(len(a), len(b))
        if len(signal) <= padlen:
            print(f"Warning: Signal length ({len(signal)}) <= padlen ({padlen}), using lfilter instead")
            from scipy.signal import lfilter
            ecg = lfilter(b, a, signal)
        else:
            ecg = filtfilt(b, a, signal)
        
        # Square signal (emphasize R peaks)
        ecg = ecg ** 2
        
        # Adaptive threshold
        threshold = np.mean(ecg) + 1.5 * np.std(ecg)
        
        # Find peaks
        min_distance = int(0.4 * fs)  # Minimum 400ms between peaks (max 150 BPM)
        peaks, properties = find_peaks(
            ecg,
            height=threshold,
            distance=min_distance
        )
        
        if len(peaks) < 2:
            return peaks, 0
        
        # Calculate heart rate
        duration = time[-1] - time[0]
        if duration > 0:
            HR = len(peaks) * 60 / duration
        else:
            HR = 0
        
        return peaks, HR
        
    except Exception as e:
        print(f"Error in heart rate detection: {e}")
        return np.array([]), 0

def apply_ecg_grid(ax):
    """Apply ECG-style grid to axis"""
    # Major grid = 5 mm
    ax.grid(which="major", color="#ff9999", linewidth=1, alpha=0.7)
    # Minor grid = 1 mm
    ax.grid(which="minor", color="#ffcccc", linewidth=0.5, alpha=0.5)
    ax.minorticks_on()

def compare_filters(run_path, selected_run, save_dir=None, show=True, save=False):
    """Compare all filters on Lead II"""
    plt.figure(figsize=(12, 6))

    for key in FILTER_FILES:
        file_path = os.path.join(run_path, FILTER_FILES[key])
        if not os.path.exists(file_path):
            continue

        df = pd.read_csv(file_path)
        t = df.iloc[:, 0]
        leadII = df.iloc[:, 2]
        plt.plot(t, leadII, label=FILTER_NAMES[key], linewidth=1, alpha=0.8)

    plt.legend(loc='best', fontsize=10)
    plt.title(f"{selected_run} - Lead II Filter Comparison", fontsize=14, fontweight='bold')
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (mV)")
    plt.grid(True, alpha=0.3)
    
    # Save if requested
    if save and save_dir is not None:
        filename = f"{selected_run}_filter_comparison.png"
        save_path = os.path.join(save_dir, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved filter comparison to: {save_path}")
    
    # Show if requested
    if show:
        plt.show()
    else:
        plt.close()

def realtime_viewer(df):
    """Simple real-time ECG viewer simulation"""
    t = df.iloc[:, 0]
    signal = df.iloc[:, 2]   # Lead II

    window = 3
    start = 0

    plt.figure(figsize=(10, 4))
    plt.ion()  # Turn on interactive mode

    while start < len(t):
        plt.cla()
        end = start + 200
        plt.plot(t[start:end], signal[start:end], color="black", linewidth=1.5)
        plt.xlim(t[start], t[start] + window)
        plt.title("Real-Time ECG Viewer (Simulated)")
        plt.xlabel("Time (s)")
        plt.ylabel("mV")
        plt.grid(True, alpha=0.3)
        plt.pause(0.02)
        start += 5
    
    plt.ioff()
    plt.show()


# ===============================
#  LOAD + PLOT
# ===============================

print(f"\n{'='*60}")
print(f"PLOT SETTINGS")
print(f"{'='*60}")
print(f"  Show plots: {show_plot}")
print(f"  Save plots: {save_plots}")
print(f"  Save 5-second window plots: {save_5sec_plots}")
print(f"  Main save directory: {plots_dir if save_plots else 'N/A'}")
if save_5sec_plots and save_plots:
    print(f"  5-second windows directory: {five_sec_plots_dir}")
print(f"{'='*60}\n")

if filter_choice.lower() == "a":
    for key in FILTER_FILES:
        file_path = os.path.join(run_path, FILTER_FILES[key])
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            filter_name = FILTER_NAMES[key]

            print(f"\nProcessing {filter_name}...")

            # Full plot
            plot_6lead(
                df,
                f"{selected_run} - {filter_name}",
                save_dir=plots_dir if save_plots else None,
                show=show_plot,
                save=save_plots
            )

            # 5-second window plots — only if save_5sec_plots is True
            if save_5sec_plots and save_plots:
                plot_all_5sec_windows(
                    df,
                    f"{selected_run} - {filter_name}",
                    save_dir=five_sec_plots_dir,
                    show_plot=False,
                    save_plot=True
                )
            else:
                print(f"  [Skipped] 5-second window plots disabled (save_5sec_plots=False)")

    # Filter comparison plot
    compare_filters(
        run_path,
        selected_run,
        save_dir=plots_dir if save_plots else None,
        show=show_plot,
        save=save_plots
    )

else:
    if filter_choice not in FILTER_FILES:
        print("Invalid filter selection.")
        exit()

    file_path = os.path.join(run_path, FILTER_FILES[filter_choice])

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        exit()

    df = pd.read_csv(file_path)
    filter_name = FILTER_NAMES[filter_choice]

    print(f"\nProcessing {filter_name}...")

    # Full plot
    plot_6lead(
        df,
        f"{selected_run} - {filter_name}",
        save_dir=plots_dir if save_plots else None,
        show=show_plot,
        save=save_plots
    )

    # 5-second window plots — only if save_5sec_plots is True
    if save_5sec_plots and save_plots:
        plot_all_5sec_windows(
            df,
            f"{selected_run} - {filter_name}",
            save_dir=five_sec_plots_dir,
            show_plot=False,
            save_plot=True
        )
    else:
        print(f"  [Skipped] 5-second window plots disabled (save_5sec_plots=False)")

# Real-time viewer if enabled
if plot_live_view and 'df' in locals():
    realtime_viewer(df)

print("\nProcessing complete!")