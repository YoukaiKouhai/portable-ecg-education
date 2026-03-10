import os
import pandas as pd
import matplotlib.pyplot as plt

plot_5_sec = False
save_plot_5_sec = True
# ===============================
#  CONFIGURATION
# ===============================

BASE_DIR = os.getcwd()

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

runs = sorted([f for f in os.listdir(BASE_DIR) if f.startswith("RUN_")])

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
#  PLOTTING FUNCTION
# ===============================

def plot_6lead(df, title):

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
        plt.title(lead_names[i])
        plt.ylabel("Amplitude")
        plt.grid(True)

    plt.xlabel("Time (s)")
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

def plot_6lead_windows(df, title, window_sec=5, show_plot=True, save_5_10=False, save_dir=None):

    t = df.iloc[:, 0]
    lead_names = df.columns[1:]

    colors = [
        "blue",
        "red",
        "green",
        "purple",
        "orange",
        "brown"
    ]

    total_time = t.iloc[-1]
    start_time = 0

    while start_time < total_time:

        end_time = start_time + window_sec
        window_mask = (t >= start_time) & (t < end_time)
        df_window = df[window_mask]

        if df_window.empty:
            break

        t_window = df_window.iloc[:, 0]

        plt.figure(figsize=(12, 10))

        for i in range(6):
            plt.subplot(6, 1, i+1)
            plt.plot(
                t_window,
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

        # ===== SAVE ONLY 5–10 SECOND WINDOW =====
        if save_5_10 and start_time == 5 and save_dir is not None:
            filename = f"{title.replace(' ', '_')}_5_to_10_sec.png"
            save_path = os.path.join(save_dir, filename)
            plt.savefig(save_path)
            print(f"Saved 5–10 sec plot to: {save_path}")

        # ===== SHOW CONTROL =====
        if show_plot:
            plt.show()
        else:
            plt.close()

        start_time += window_sec

# ... (Keep your existing imports and configuration)

# ===============================
#  UPDATED PLOTTING FUNCTION
# ===============================

def plot_6lead_windows(df, title, window_sec=5, show_plot=True, save_plots=True, save_dir=None):
    t = df.iloc[:, 0]
    lead_names = df.columns[1:]
    colors = ["blue", "red", "green", "purple", "orange", "brown"]

    total_time = t.iloc[-1]
    start_time = 0

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

        # ===== SAVE LOGIC FOR SPECIFIC WINDOWS =====
        # Checks if current window is 5-10, 10-15, or 15-20
        target_windows = [1, 6, 12]
        
        if save_plots and (start_time in target_windows) and save_dir is not None:
            filename = f"{title.replace(' ', '_')}_{int(start_time)}_to_{int(end_time)}_sec.png"
            save_path = os.path.join(save_dir, filename)
            plt.savefig(save_path)
            print(f"Saved window plot to: {save_path}")

        # ===== SHOW CONTROL =====
        if show_plot:
            plt.show()
        else:
            plt.close()

        start_time += window_sec



# ===============================
#  LOAD + PLOT
# ===============================

# ===============================
#  UPDATED LOAD + PLOT SECTION
# ===============================

# Set show_plot to True if you want to see them pop up, 
# or False if you just want to save them to the folder.
show_on_screen = True 

if filter_choice.lower() == "a":
    for key in FILTER_FILES:
        file_path = os.path.join(run_path, FILTER_FILES[key])
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Full plot
            plot_6lead(df, f"{selected_run} - {FILTER_NAMES[key]}")
            # Windowed plots (5-10, 10-15, 15-20)
            plot_6lead_windows(
                df,
                f"{selected_run} - {FILTER_NAMES[key]}",
                window_sec=2,
                show_plot=show_on_screen,
                save_plots=True,
                save_dir=run_path
            )
else:
    # ... (Keep your existing single-filter logic, just update the function call)
    df = pd.read_csv(file_path)
    plot_6lead(df, f"{selected_run} - {FILTER_NAMES[filter_choice]}")
    plot_6lead_windows(
        df,
        f"{selected_run} - {FILTER_NAMES[filter_choice]}",
        window_sec=5,
        show_plot=show_on_screen,
        save_plots=True,
        save_dir=run_path
    )

