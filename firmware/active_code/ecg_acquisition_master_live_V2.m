clear; clc; close all;

%% ===============================
%  USER SETTINGS
%% ===============================

port = "COM5";              % Change to your Arduino port
baud = 115200;
record_time = 20;           % seconds to record
buffer_size = 500;          % Number of samples to show in live view

%% ===============================
%  CREATE RUN FOLDER (SMART VERSION)
%% ===============================

base_folder = pwd;

% Get all folders
folder_info = dir(base_folder);
folder_names = {folder_info([folder_info.isdir]).name};

run_numbers = [];

for i = 1:length(folder_names)
    name = folder_names{i};
    
    % Check if name starts with 'RUN_'
    if length(name) >= 7 && strcmp(name(1:4), 'RUN_')
        
        % Extract the 3-digit number after RUN_
        num_part = name(5:7);
        
        if all(isstrprop(num_part, 'digit'))
            run_numbers(end+1) = str2double(num_part); %#ok<SAGROW>
        end
    end
end

if isempty(run_numbers)
    next_run = 1;
else
    next_run = max(run_numbers) + 1;
end

% Create new folder
run_folder = fullfile(base_folder, sprintf("RUN_%03d", next_run));
mkdir(run_folder);

fprintf("Saving data to: %s\n", run_folder);

%% ===============================
%  SETUP LIVE VISUALIZATION
%% ===============================

% Create figure for hospital-style monitoring
figure('Name', 'Live ECG Monitoring', 'Position', [100, 100, 1200, 800], 'Color', 'k');

% Lead II subplot (main monitoring lead)
ax_lead2 = subplot(3,1,1);
set(ax_lead2, 'Color', 'k', 'XColor', 'g', 'YColor', 'g', 'FontSize', 12);
title('Lead II - Primary Monitoring Lead', 'Color', 'g', 'FontSize', 14);
ylabel('Voltage (mV)', 'Color', 'g');
grid on;
set(ax_lead2, 'GridColor', [0.3, 0.3, 0.3]);
hold(ax_lead2, 'on');

% Lead I subplot
ax_lead1 = subplot(3,1,2);
set(ax_lead1, 'Color', 'k', 'XColor', 'g', 'YColor', 'g', 'FontSize', 12);
title('Lead I', 'Color', 'g', 'FontSize', 14);
ylabel('Voltage (mV)', 'Color', 'g');
grid on;
set(ax_lead1, 'GridColor', [0.3, 0.3, 0.3]);
hold(ax_lead1, 'on');

% Lead III subplot
ax_lead3 = subplot(3,1,3);
set(ax_lead3, 'Color', 'k', 'XColor', 'g', 'YColor', 'g', 'FontSize', 12);
title('Lead III', 'Color', 'g', 'FontSize', 14);
xlabel('Time (seconds)', 'Color', 'g');
ylabel('Voltage (mV)', 'Color', 'g');
grid on;
set(ax_lead3, 'GridColor', [0.3, 0.3, 0.3]);
hold(ax_lead3, 'on');

% Heart Rate Display (digital readout)
ax_hr = axes('Position', [0.85, 0.85, 0.1, 0.1]);
set(ax_hr, 'Color', 'k', 'XColor', 'none', 'YColor', 'none');
axis off;
hr_text = text(0.5, 0.5, 'HR: -- BPM', 'Color', 'r', 'FontSize', 18, ...
    'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'Parent', ax_hr);

% Status indicator
ax_status = axes('Position', [0.02, 0.95, 0.1, 0.03]);
set(ax_status, 'Color', 'k', 'XColor', 'none', 'YColor', 'none');
axis off;
status_text = text(0.5, 0.5, 'RECORDING', 'Color', 'g', 'FontSize', 12, ...
    'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'Parent', ax_status);

% Timer display
ax_timer = axes('Position', [0.15, 0.95, 0.1, 0.03]);
set(ax_timer, 'Color', 'k', 'XColor', 'none', 'YColor', 'none');
axis off;
timer_text = text(0.5, 0.5, '00.0 s', 'Color', 'w', 'FontSize', 12, ...
    'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'Parent', ax_timer);

drawnow;

%% ===============================
%  SERIAL CONNECTION
%% ===============================

s = serialport(port, baud);
flush(s);
configureTerminator(s, "LF");  % Set line terminator

fprintf("Recording...\n");

%% ===============================
%  DATA COLLECTION WITH LIVE VIEW
%% ===============================

data = [];
time_buffer = [];
start_time = tic;
last_update = tic;
update_rate = 0.05;  % Update display every 50ms

% Initialize display lines
line1 = plot(ax_lead1, NaN, NaN, 'y', 'LineWidth', 1.5);
line2 = plot(ax_lead2, NaN, NaN, 'g', 'LineWidth', 1.5);
line3 = plot(ax_lead3, NaN, NaN, 'c', 'LineWidth', 1.5);

% Heart rate detection variables
hr_buffer = [];
last_peak_time = 0;

fprintf("Press Ctrl+C to stop early\n");

try
    while toc(start_time) < record_time
        if s.NumBytesAvailable > 0
            line = readline(s);
            values = str2double(split(line, ","));
            
            if length(values) == 2 && all(~isnan(values))
                % Store data
                data = [data; values']; %#ok<AGROW>
                current_time = toc(start_time);
                time_buffer = [time_buffer; current_time]; %#ok<AGROW>
                
                % Heart rate detection on Lead II (values(2))
                [hr, peak_detected] = detect_heart_rate(values(2), current_time, last_peak_time);
                if peak_detected
                    last_peak_time = current_time;
                    if hr > 30 && hr < 200  % Valid physiological range
                        hr_buffer = [hr_buffer; hr]; %#ok<AGROW>
                        if length(hr_buffer) > 5
                            hr_buffer = hr_buffer(end-4:end);
                        end
                        avg_hr = mean(hr_buffer);
                        set(hr_text, 'String', sprintf('HR: %.0f BPM', avg_hr));
                        
                        % Color code heart rate
                        if avg_hr < 60
                            set(hr_text, 'Color', [1, 0.5, 0]); % Orange for bradycardia
                        elseif avg_hr > 100
                            set(hr_text, 'Color', 'r'); % Red for tachycardia
                        else
                            set(hr_text, 'Color', [0, 1, 0]); % Green for normal
                        end
                    end
                end
                
                % Update display at specified rate
                if toc(last_update) >= update_rate && length(time_buffer) > 1
                    % Keep only last buffer_size points for display
                    if length(time_buffer) > buffer_size
                        display_times = time_buffer(end-buffer_size:end);
                        display_lead1 = data(end-buffer_size:end, 1);
                        display_lead2 = data(end-buffer_size:end, 2);
                        display_lead3 = display_lead2 - display_lead1;
                    else
                        display_times = time_buffer;
                        display_lead1 = data(:, 1);
                        display_lead2 = data(:, 2);
                        display_lead3 = display_lead2 - display_lead1;
                    end
                    
                    % Update plots
                    set(line1, 'XData', display_times, 'YData', display_lead1);
                    set(line2, 'XData', display_times, 'YData', display_lead2);
                    set(line3, 'XData', display_times, 'YData', display_lead3);
                    
                    % Auto-scale axes
                    if ~isempty(display_lead1)
                        ylim(ax_lead1, [min(display_lead1)-0.2, max(display_lead1)+0.2]);
                        ylim(ax_lead2, [min(display_lead2)-0.2, max(display_lead2)+0.2]);
                        ylim(ax_lead3, [min(display_lead3)-0.2, max(display_lead3)+0.2]);
                    end
                    xlim(ax_lead1, [max(0, current_time-buffer_size/Fs_estimate), current_time]);
                    xlim(ax_lead2, [max(0, current_time-buffer_size/Fs_estimate), current_time]);
                    xlim(ax_lead3, [max(0, current_time-buffer_size/Fs_estimate), current_time]);
                    
                    % Update timer
                    set(timer_text, 'String', sprintf('%.1f s', current_time));
                    
                    last_update = toc;
                    drawnow limitrate;
                end
            end
        end
        
        % Update sampling rate estimate
        if size(data, 1) > 10
            Fs_estimate = size(data, 1) / toc(start_time);
        else
            Fs_estimate = 250;  % Default estimate
        end
    end
    
catch ME
    fprintf("Recording stopped: %s\n", ME.message);
end

%% ===============================
%  CLEANUP AND SAVE
%% ===============================

% Change status to complete
set(status_text, 'String', 'COMPLETE', 'Color', 'b');
set(timer_text, 'String', sprintf('%.1f s', record_time));
drawnow;

% Close serial port
clear s

fprintf("Recording complete. Total samples: %d\n", size(data, 1));

%% ===============================
%  EXTRACT RAW LEADS
%% ===============================

leadI  = data(:,1);
leadII = data(:,2);

N = length(leadI);

%% ===============================
%  SAMPLING RATE ESTIMATION
%% ===============================

Fs = N / record_time;
t = (0:N-1)' / Fs;

fprintf("Estimated Sampling Rate: %.2f Hz\n", Fs);

%% ===============================
%  DERIVED LEADS
%% ===============================

leadIII = leadII - leadI;
aVR = -(leadI + leadII)/2;
aVL = leadI - leadII/2;
aVF = leadII - leadI/2;

%% ===============================
%  HEART RATE CALCULATION (Final)
%% ===============================

% Use Lead II for HR detection
[peaks, locs] = findpeaks(leadII, ...
    'MinPeakDistance', round(0.4*Fs), ...
    'MinPeakHeight', mean(leadII) + std(leadII));

if length(locs) > 1
    RR_intervals = diff(locs)/Fs;
    HR = 60 / mean(RR_intervals);
    fprintf("Estimated Heart Rate: %.1f BPM\n", HR);
else
    fprintf("Insufficient peaks for heart rate calculation\n");
end

%% ===============================
%  SAVE RAW 6-LEAD CSV
%% ===============================

raw_table = table(t, leadI, leadII, leadIII, aVR, aVL, aVF);
writetable(raw_table, fullfile(run_folder, "raw_6lead.csv"));

%% ===============================
%  FILTERS (Same as original)
%% ===============================

% ----- 1. Bandpass -----
bp = designfilt('bandpassiir','FilterOrder',4, ...
    'HalfPowerFrequency1',0.5,'HalfPowerFrequency2',40, ...
    'SampleRate',Fs);

bp_I  = filtfilt(bp, leadI);
bp_II = filtfilt(bp, leadII);

% ----- 2. Butterworth -----
[b,a] = butter(4,[0.5 40]/(Fs/2),'bandpass');
but_I  = filtfilt(b,a,leadI);
but_II = filtfilt(b,a,leadII);

% ----- 3. Chebyshev Notch (60 Hz) -----
[d,c] = cheby1(4,1,[59 61]/(Fs/2),'stop');
cheb_I  = filtfilt(d,c,leadI);
cheb_II = filtfilt(d,c,leadII);

% ----- 4. Simple Kalman -----
kal_I = simple_kalman(leadI);
kal_II = simple_kalman(leadII);

% ----- 5. Adaptive (LMS Noise Reduction) -----
noise_ref = sin(2*pi*60*t);  % simulated powerline
adapt_I = lms_filter(leadI, noise_ref);
adapt_II = lms_filter(leadII, noise_ref);

%% ===============================
%  SAVE FILTERED FILES
%% ===============================

save_filtered(run_folder, "bandpass_filtered.csv", t, bp_I, bp_II);
save_filtered(run_folder, "butterworth_filtered.csv", t, but_I, but_II);
save_filtered(run_folder, "chebyshev_notch_filtered.csv", t, cheb_I, cheb_II);
save_filtered(run_folder, "kalman_filtered.csv", t, kal_I, kal_II);
save_filtered(run_folder, "adaptive_filtered.csv", t, adapt_I, adapt_II);

%% ===============================
%  FINAL 6-LEAD PLOT
%% ===============================

figure('Name', 'Final 6-Lead ECG');
leads = {leadI, leadII, leadIII, aVR, aVL, aVF};
names = {'Lead I','Lead II','Lead III','aVR','aVL','aVF'};

for i = 1:6
    subplot(6,1,i)
    plot(t, leads{i})
    title(names{i})
    ylabel('mV')
    grid on
end
xlabel('Time (s)')
sgtitle('Raw 6-Lead ECG')

%% ===============================
%  HELPER FUNCTIONS
%% ===============================

function [hr, peak_detected] = detect_heart_rate(value, current_time, last_peak_time)
    persistent last_value peak_threshold last_peak_value
    
    if isempty(last_value)
        last_value = 0;
        peak_threshold = 0.5;
        last_peak_value = 0;
    end
    
    peak_detected = false;
    hr = 0;
    
    % Simple peak detection with refractory period
    if current_time - last_peak_time > 0.3  % Refractory period of 300ms
        if value > peak_threshold && last_value <= peak_threshold
            peak_detected = true;
            if last_peak_time > 0
                rr_interval = current_time - last_peak_time;
                if rr_interval > 0.4 && rr_interval < 1.5  % Valid RR interval
                    hr = 60 / rr_interval;
                end
            end
            
            % Update threshold (adaptive)
            peak_threshold = value * 0.6;
        end
    end
    
    % Decay threshold slowly
    peak_threshold = peak_threshold * 0.995;
    
    last_value = value;
end

function x_hat = simple_kalman(x)
    Q = 0.01; R = 0.1;
    P = 1; X = 0;
    x_hat = zeros(size(x));
    for k = 1:length(x)
        P = P + Q;
        K = P/(P+R);
        X = X + K*(x(k)-X);
        P = (1-K)*P;
        x_hat(k) = X;
    end
end

function y = lms_filter(x, ref)
    mu = 0.01;
    w = 0;
    y = zeros(size(x));
    for n = 1:length(x)
        y(n) = x(n) - w*ref(n);
        w = w + mu * y(n) * ref(n);
    end
end

function save_filtered(folder, filename, t, leadI, leadII)
    leadIII = leadII - leadI;
    aVR = -(leadI + leadII)/2;
    aVL = leadI - leadII/2;
    aVF = leadII - leadI/2;
    
    T = table(t, leadI, leadII, leadIII, aVR, aVL, aVF);
    writetable(T, fullfile(folder, filename));
end