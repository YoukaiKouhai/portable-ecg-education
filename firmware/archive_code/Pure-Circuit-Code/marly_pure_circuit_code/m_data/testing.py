import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections

# ---------- SETTINGS ----------
SERIAL_PORT = 'COM3'  # Change this to your Arduino port (e.g., 'COM4' or '/dev/ttyUSB0')
BAUD_RATE = 115200
WINDOW_SIZE = 1000    # Number of data points to show on screen (approx 2 seconds)

# Data buffers
ecg_data = collections.deque([0] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
time_data = collections.deque([0] * WINDOW_SIZE, maxlen=WINDOW_SIZE)

# Initialize Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

# ---------- PLOT SETUP ----------
fig, ax = plt.subplots(figsize=(12, 6))
line, = ax.plot([], [], color='#e74c3c', linewidth=1.5) # Hospital Red ECG line
ax.set_ylim(-200, 200) # Adjust based on your filtered signal amplitude
ax.set_title("Live ECG Feed (Butterworth 2nd Order Filtered)")
ax.set_xlabel("Samples")
ax.set_ylabel("Filtered Amplitude")
ax.grid(True, which='both', linestyle='--', alpha=0.5)

def update(frame):
    if ser.in_waiting:
        line_raw = ser.readline().decode('utf-8', errors='ignore').strip()
        
        # Parse the "ECG:value,SR:value" format
        try:
            # Split by comma, then split by colon to get the numbers
            parts = line_raw.split(',')
            ecg_val = float(parts[0].split(':')[1])
            # sr_val = float(parts[1].split(':')[1]) # Optional: Use for monitoring
            
            ecg_data.append(ecg_val)
            line.set_data(range(len(ecg_data)), ecg_data)
            ax.set_xlim(0, len(ecg_data))
            
        except (IndexError, ValueError):
            pass # Skip malformed lines

    return line,

# Use FuncAnimation for smooth live plotting
ani = FuncAnimation(fig, update, interval=1, blit=True, cache_frame_data=False)

plt.tight_layout()
plt.show()
ser.close()