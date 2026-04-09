clear; clc; close all;

%% ===============================
%  USER SETTINGS
%% ===============================

port = "COM3";              % Change to your Arduino port
baud = 115200;
record_time = 20;           % seconds to record

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
%  SERIAL CONNECTION
%% ===============================

s = serialport(port, baud);
flush(s);

fprintf("Recording...\n");

data = [];
start_time = tic;

while toc(start_time) < record_time
    line = readline(s);
    values = str2double(split(line, ","));
    
    if length(values) == 2 && all(~isnan(values))
        data = [data; values']; %#ok<AGROW>
    end
end

clear s

fprintf("Recording complete.\n");

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
%  HEART RATE CALCULATION
%% ===============================

% Use Lead II for HR detection
[peaks, locs] = findpeaks(leadII, ...
    'MinPeakDistance', round(0.4*Fs), ...
    'MinPeakHeight', mean(leadII) + std(leadII));

RR_intervals = diff(locs)/Fs;
HR = 60 / mean(RR_intervals);

fprintf("Estimated Heart Rate: %.1f BPM\n", HR);

%% ===============================
%  SAVE RAW 6-LEAD CSV
%% ===============================

raw_table = table(t, leadI, leadII, leadIII, aVR, aVL, aVF);
writetable(raw_table, fullfile(run_folder, "raw_6lead.csv"));

%% ===============================
%  FILTERS
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
%  6-LEAD PLOT
%% ===============================

figure;
leads = {leadI, leadII, leadIII, aVR, aVL, aVF};
names = {'Lead I','Lead II','Lead III','aVR','aVL','aVF'};

for i = 1:6
    subplot(6,1,i)
    plot(t, leads{i})
    title(names{i})
    ylabel('mV')
end
xlabel('Time (s)')
sgtitle('Raw 6-Lead ECG')

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