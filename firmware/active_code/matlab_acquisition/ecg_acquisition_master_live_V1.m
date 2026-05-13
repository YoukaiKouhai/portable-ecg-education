clear; clc; close all;

%% ===============================
% USER SETTINGS
%% ===============================

use_live_acquisition = true;     % false = analyze existing RUN folders
simulate_live_view = false;   % enable playback when offline

port = "COM5";
baud = 115200;
record_time = 20;

Vref = 5;           % Arduino reference voltage
ADCmax = 1023;

%% ===============================
% CREATE RUN FOLDER (SMART VERSION)
%% ===============================

base_folder = pwd;

folder_info = dir(base_folder);
folder_names = {folder_info([folder_info.isdir]).name};

run_numbers = [];

for i = 1:length(folder_names)

    name = folder_names{i};

    if length(name) >= 7 && strcmp(name(1:4),'RUN_')

        num_part = name(5:7);

        if all(isstrprop(num_part,'digit'))
            run_numbers(end+1) = str2double(num_part);
        end

    end

end

if isempty(run_numbers)
    next_run = 1;
else
    next_run = max(run_numbers)+1;
end

run_folder = fullfile(base_folder,sprintf("RUN_%03d",next_run));
mkdir(run_folder);

fprintf("Saving data to: %s\n",run_folder);

%% ===============================
% DATA ACQUISITION OR LOAD
%% ===============================

if use_live_acquisition

    s = serialport(port,baud);
    flush(s);

    fprintf("Recording with live ECG display...\n");

    data = [];

    % ===== Create live ECG figure =====
    figure('Name','Live ECG Monitor','Color','w',...
        'Units','normalized','Position',[0.1 0.1 0.8 0.8])

    tiledlayout(6,1)

    ax(1)=nexttile; h(1)=animatedline('Color','k','LineWidth',1); title("Lead I")
    ax(2)=nexttile; h(2)=animatedline('Color','k','LineWidth',1); title("Lead II")
    ax(3)=nexttile; h(3)=animatedline('Color','k','LineWidth',1); title("Lead III")
    ax(4)=nexttile; h(4)=animatedline('Color','k','LineWidth',1); title("aVR")
    ax(5)=nexttile; h(5)=animatedline('Color','k','LineWidth',1); title("aVL")
    ax(6)=nexttile; h(6)=animatedline('Color','k','LineWidth',1); title("aVF")

    for i=1:6
        grid(ax(i),'on')
        hold(ax(i),'on')
        ylabel(ax(i),'mV')
    end
    xlabel(ax(6),'Time (s)')

    start_time = tic;

    % ===== Parameters =====
    window = 2;              % scrolling window in seconds
    update_interval = 0.1;   % seconds between plot updates
    next_update = update_interval;

    % Buffers
    signal_buffer = [];
    time_buffer = [];

    while toc(start_time) < record_time

        line = readline(s);
        values = str2double(split(line,","));

        if length(values)==2 && all(~isnan(values))

            leadI_raw = values(1);
            leadII_raw = values(2);

            % store raw data
            data = [data; values'];

            % convert ADC → mV (centered around 0)
            leadI = (leadI_raw/ADCmax)*Vref;
            leadII = (leadII_raw/ADCmax)*Vref;

            leadI = (leadI - 2.5)*1000;
            leadII = (leadII - 2.5)*1000;

            % derived leads
            leadIII = leadII - leadI;
            aVR = -(leadI + leadII)/2;
            aVL = leadI - leadII/2;
            aVF = leadII - leadI/2;

            t_now = toc(start_time);

            % store in buffer
            signal_buffer = [signal_buffer; leadI leadII leadIII aVR aVL aVF];
            time_buffer = [time_buffer; t_now];

            % update plot only every update_interval
            if t_now >= next_update
                for i = 1:6
                    addpoints(h(i), time_buffer, signal_buffer(:,i));
                    % scrolling window
                    if t_now > window
                        xlim(ax(i), [t_now-window t_now]);
                    end
                end
                drawnow limitrate;

                % clear buffer
                signal_buffer = [];
                time_buffer = [];

                next_update = t_now + update_interval;
            end
        end
    end

    clear s
    fprintf("Recording complete\n")

else

    fprintf("Offline mode: select a RUN CSV file\n")

    [file,path] = uigetfile("*.csv","Select ECG CSV file");

    if isequal(file,0)
        error("No file selected.")
    end

    filepath = fullfile(path,file);

    fprintf("Loading: %s\n",filepath)

    T = readtable(filepath);

    vars = lower(T.Properties.VariableNames);

    if all(ismember({'leadi','leadii'},vars))

        leadI_raw  = T{:,strcmp(vars,'leadi')};
        leadII_raw = T{:,strcmp(vars,'leadii')};

    else
        error("CSV does not contain Lead I and Lead II columns.")
    end

    if any(strcmp(vars,'t'))
        t = T{:,strcmp(vars,'t')};
        record_time = t(end);
    else
        error("CSV must contain time column 't'")
    end

    data = [leadI_raw leadII_raw];

end


%% ===============================
% SIMULATED LIVE ECG VIEW (6-LEAD)
%% ===============================

if ~use_live_acquisition && simulate_live_view

    fprintf("Starting simulated live ECG playback...\n")

    Fs = length(data) / record_time;

    % Convert ADC -> mV (adjust if using 3.3V board)
    Vref = 5;
    ADCmax = 1023;

    leadI_live  = (data(:,1)/ADCmax)*Vref;
    leadII_live = (data(:,2)/ADCmax)*Vref;

    % Remove DC offset
    leadI_live  = leadI_live - mean(leadI_live);
    leadII_live = leadII_live - mean(leadII_live);

    % Convert to millivolts
    leadI_live  = leadI_live * 1000;
    leadII_live = leadII_live * 1000;

    % Derived leads
    leadIII_live = leadII_live - leadI_live;
    aVR_live = -(leadI_live + leadII_live)/2;
    aVL_live = leadI_live - leadII_live/2;
    aVF_live = leadII_live - leadI_live/2;

    N = length(leadI_live);

    window = 2;   % seconds

    figure('Name','Portable ECG Monitor','Color','w',...
       'Units','normalized','Position',[0.1 0.1 0.8 0.8])

    tiledlayout(6,1)

    ax(1)=nexttile; h(1)=animatedline('Color','k','LineWidth',1); title("Lead I")
    ax(2)=nexttile; h(2)=animatedline('Color','k','LineWidth',1); title("Lead II")
    ax(3)=nexttile; h(3)=animatedline('Color','k','LineWidth',1); title("Lead III")
    ax(4)=nexttile; h(4)=animatedline('Color','k','LineWidth',1); title("aVR")
    ax(5)=nexttile; h(5)=animatedline('Color','k','LineWidth',1); title("aVL")
    ax(6)=nexttile; h(6)=animatedline('Color','k','LineWidth',1); title("aVF")

    for i=1:6
    
        ylabel(ax(i),"mV")
        grid(ax(i),'on')
        hold(ax(i),'on')
    
        % ECG grid
        ax(i).XMinorGrid = 'on';
        ax(i).YMinorGrid = 'on';
        ax(i).GridColor = [1 0.7 0.7];
        ax(i).MinorGridColor = [1 0.9 0.9];
    
        % Allow auto scaling
        ax(i).YLimMode = 'auto';
    
    end

    xlabel(ax(6),"Time (s)")

    % Heart rate display
    hr_text = annotation('textbox',[0.82 0.92 0.15 0.06],...
        'String',"HR: -- BPM",...
        'FontSize',14,...
        'FontWeight','bold',...
        'EdgeColor','none');

    t = (0:N-1)/Fs;

    block = round(Fs/20);   % update ~20 frames per second

    signal_buffer = [];
    time_buffer = [];

    startTimer = tic;

    for k = 1:block:N

        idx = k:min(k+block-1,N);

        s1 = leadI_live(idx);
        s2 = leadII_live(idx);
        s3 = leadIII_live(idx);
        s4 = aVR_live(idx);
        s5 = aVL_live(idx);
        s6 = aVF_live(idx);

        addpoints(h(1),t(idx),s1)
        addpoints(h(2),t(idx),s2)
        addpoints(h(3),t(idx),s3)
        addpoints(h(4),t(idx),s4)
        addpoints(h(5),t(idx),s5)
        addpoints(h(6),t(idx),s6)

        signal_buffer = [signal_buffer; s2];
        time_buffer = [time_buffer; t(idx)'];

        if length(signal_buffer) > Fs*3

            ecg = signal_buffer - mean(signal_buffer);

            [~,locs] = findpeaks(ecg,...
                'MinPeakDistance',round(0.4*Fs),...
                'MinPeakHeight',0.5*max(ecg));

            if length(locs) > 2
                RR = diff(time_buffer(locs));
                HR = 60/mean(RR);
                hr_text.String = sprintf("HR: %.0f BPM",HR);
            end

            signal_buffer = signal_buffer(end-Fs*3:end);
            time_buffer = time_buffer(end-Fs*3:end);

        end

        drawnow limitrate

        % Dynamic Y scaling based on recent data
        if length(signal_buffer) > Fs
        
            recent = signal_buffer(end-Fs:end);
        
            y_min = min(recent);
            y_max = max(recent);
        
            margin = 0.2*(y_max - y_min + eps);
        
            for i=1:6
                ylim(ax(i),[y_min-margin y_max+margin])
            end
        
        end

        % Maintain real-time speed
        elapsed = toc(startTimer);
        targetTime = t(idx(end));

        if targetTime > elapsed
            pause(targetTime - elapsed)
        end

        % 2-second window
        if t(idx(end)) > window
            for i=1:6
                xlim(ax(i),[t(idx(end))-window t(idx(end))])
            end
        end

    end

    fprintf("Playback finished\n")

end

%% ===============================
% RAW LEADS
%% ===============================

leadI_raw  = data(:,1);
leadII_raw = data(:,2);

N = length(leadI_raw);

Fs = N / record_time;
t = (0:N-1)'/Fs;

fprintf("Estimated Sampling Rate: %.2f Hz\n",Fs)

%% ===============================
% ADC -> MILLIVOLT CONVERSION
%% ===============================

leadI  = (leadI_raw/ADCmax)*Vref;
leadII = (leadII_raw/ADCmax)*Vref;

leadI  = leadI - mean(leadI);
leadII = leadII - mean(leadII);

leadI  = leadI*1000;
leadII = leadII*1000;

%% ===============================
% DERIVED LEADS
%% ===============================

leadIII = leadII - leadI;
aVR = -(leadI + leadII)/2;
aVL = leadI - leadII/2;
aVF = leadII - leadI/2;

%% ===============================
% SAVE RAW CSV (UNCHANGED STRUCTURE)
%% ===============================

raw_table = table(t,leadI_raw,leadII_raw,leadIII,aVR,aVL,aVF,...
    'VariableNames',{'t','leadI','leadII','leadIII','aVR','aVL','aVF'});

writetable(raw_table,fullfile(run_folder,"raw_6lead.csv"));

%% ===============================
% APPLY FILTERS TO RAW SIGNALS
%% ===============================

%% ===============================
% SIMPLE KALMAN FILTER
%% ===============================

function x_hat = simple_kalman(x)

Q = 0.001;     % process noise
R = 0.05;      % measurement noise

P = 1;
X = x(1);

x_hat = zeros(size(x));

for k = 1:length(x)

    % Prediction
    P = P + Q;

    % Kalman gain
    K = P/(P+R);

    % Update estimate
    X = X + K*(x(k)-X);

    % Update error covariance
    P = (1-K)*P;

    x_hat(k) = X;

   end

end

%% ===============================
% LMS ADAPTIVE FILTER
%% ===============================

function y = lms_filter(x,ref)

mu = 0.01;        % learning rate
w = 0;

y = zeros(size(x));

for n = 1:length(x)

    y(n) = x(n) - w*ref(n);

    w = w + mu*y(n)*ref(n);

    end

end

function [yI,yII] = bandpass_filter(xI,xII,Fs)

    bp = designfilt('bandpassiir',...
        'FilterOrder',4,...
        'HalfPowerFrequency1',0.5,...
        'HalfPowerFrequency2',40,...
        'SampleRate',Fs);

    yI = filtfilt(bp,xI);
    yII = filtfilt(bp,xII);

end

function [yI,yII] = butterworth_filter(xI,xII,Fs)

    [b,a] = butter(4,[0.5 40]/(Fs/2),'bandpass');

    yI = filtfilt(b,a,xI);
    yII = filtfilt(b,a,xII);

end

function [yI,yII] = chebyshev_notch_filter(xI,xII,Fs)

    [b,a] = cheby1(4,1,[59 61]/(Fs/2),'stop');

    yI = filtfilt(b,a,xI);
    yII = filtfilt(b,a,xII);

end

function [yI,yII] = kalman_filter_pair(xI,xII)

    yI = simple_kalman(xI);
    yII = simple_kalman(xII);

end

function [yI,yII] = adaptive_filter_pair(xI,xII,Fs,t)

    noise_ref = sin(2*pi*60*t);

    yI = lms_filter(xI,noise_ref);
    yII = lms_filter(xII,noise_ref);

end

function save_filtered(folder,filename,t,leadI,leadII)

    leadIII = leadII - leadI;
    aVR = -(leadI + leadII)/2;
    aVL = leadI - leadII/2;
    aVF = leadII - leadI/2;

    T = table(t,leadI,leadII,leadIII,aVR,aVL,aVF);

    writetable(T,fullfile(folder,filename));

end

function apply_all_filters(folder,t,leadI_raw,leadII_raw,Fs)

    fprintf("Applying filters...\n")

    % Convert ADC -> mV
    Vref = 5;
    ADCmax = 1023;

    leadI  = (leadI_raw/ADCmax)*Vref;
    leadII = (leadII_raw/ADCmax)*Vref;

    leadI  = (leadI - mean(leadI))*1000;
    leadII = (leadII - mean(leadII))*1000;

    % Apply filters
    [fI,fII] = bandpass_filter(leadI,leadII,Fs);
    save_filtered(folder,"bandpass_filtered.csv",t,fI,fII)

    [fI,fII] = butterworth_filter(leadI,leadII,Fs);
    save_filtered(folder,"butterworth_filtered.csv",t,fI,fII)

    [fI,fII] = chebyshev_notch_filter(leadI,leadII,Fs);
    save_filtered(folder,"chebyshev_notch_filtered.csv",t,fI,fII)

    [fI,fII] = kalman_filter_pair(leadI,leadII);
    save_filtered(folder,"kalman_filtered.csv",t,fI,fII)

    [fI,fII] = adaptive_filter_pair(leadI,leadII,Fs,t);
    save_filtered(folder,"adaptive_filtered.csv",t,fI,fII)

    fprintf("Filtering complete\n")

end

apply_all_filters(run_folder,t,leadI_raw,leadII_raw,Fs)

%% ===============================
% ECG FILTER PIPELINE
%% ===============================

hp = designfilt('highpassiir', ...
    'FilterOrder',4,...
    'HalfPowerFrequency',0.5,...
    'SampleRate',Fs);

lp = designfilt('lowpassiir',...
    'FilterOrder',4,...
    'HalfPowerFrequency',40,...
    'SampleRate',Fs);

notch = designfilt('bandstopiir',...
    'FilterOrder',2,...
    'HalfPowerFrequency1',59,...
    'HalfPowerFrequency2',61,...
    'SampleRate',Fs);

ecgI = filtfilt(hp,leadI);
ecgI = filtfilt(lp,ecgI);
ecgI = filtfilt(notch,ecgI);

ecgII = filtfilt(hp,leadII);
ecgII = filtfilt(lp,ecgII);
ecgII = filtfilt(notch,ecgII);

%% ===============================
% DERIVED FILTERED LEADS
%% ===============================

leadIII_f = ecgII - ecgI;
aVR_f = -(ecgI + ecgII)/2;
aVL_f = ecgI - ecgII/2;
aVF_f = ecgII - ecgI/2;

%% ===============================
% HEART RATE DETECTION
%% ===============================

Fs = 500;  % Arduino sample rate
signal = ecgII - mean(ecgII);

% Bandpass QRS
[b,a] = butter(2, [5 15]/(Fs/2), 'bandpass');
ecg_filtered = filtfilt(b, a, signal);

% Square to emphasize R
ecg_squared = ecg_filtered.^2;

% Adaptive threshold
threshold = mean(ecg_squared) + 1.5*std(ecg_squared);

% Detect R-peaks
[peaks, locs] = findpeaks(ecg_squared, ...
    'MinPeakDistance', round(0.6*Fs), ...
    'MinPeakHeight', threshold);

% RR intervals and HR
RR = diff(locs) / Fs;
HR = 60 / mean(RR);

fprintf('Detected %d R-peaks, Estimated Heart Rate: %.1f BPM\n', length(peaks), HR);

% Optional: plot
figure;
plot(signal); hold on;
plot(locs, signal(locs), 'ro');
xlabel('Samples'); ylabel('Amplitude (mV)');
title(sprintf('Lead II - R-peaks, HR = %.1f BPM', HR));
grid on;

%% ===============================
% SAVE FILTERED CSV
%% ===============================

T = table(t,ecgI,ecgII,leadIII_f,aVR_f,aVL_f,aVF_f);
writetable(T,fullfile(run_folder,"filtered_ecg.csv"));

%% ===============================
% REAL-TIME STYLE ECG PLOT
%% ===============================

figure('Color','w')

tiledlayout(6,1)

signals = {ecgI,ecgII,leadIII_f,aVR_f,aVL_f,aVF_f};
names = {'Lead I','Lead II','Lead III','aVR','aVL','aVF'};

for i=1:6

    nexttile
    plot(t,signals{i},'k')
    ylabel(names{i})
    grid on

end

xlabel('Time (s)')
title(sprintf("6-Lead ECG | HR = %.1f BPM",HR))

%exportgraphics(gcf,fullfile(run_folder,"ecg_6lead_plot.pdf"))

%% ===============================
% ECG ANNOTATION
%% ===============================

figure('Color','w')

plot(t,ecgII,'k')
hold on
plot(t(locs),ecgII(locs),'ro','MarkerFaceColor','r')

title(sprintf("Lead II with R-peak Detection | HR %.1f BPM",HR))
xlabel("Time (s)")
ylabel("mV")
grid on

%exportgraphics(gcf,fullfile(run_folder,"r_peak_annotation.pdf"))

%% ===============================
% CLINICAL STYLE ECG REPORT
%% ===============================

figure('Color','w','Position',[100 100 900 700])

tiledlayout(3,2)

leads = {ecgI,ecgII,leadIII_f,aVR_f,aVL_f,aVF_f};

for i=1:6

    nexttile
    plot(t,leads{i},'k')
    title(names{i})
    grid on

end

sgtitle(sprintf("Portable ECG Report | HR %.1f BPM",HR))

%exportgraphics(gcf,fullfile(run_folder,"ECG_REPORT.pdf"))

%% ===============================
% FILTER PERFORMANCE ANALYSIS
%% ===============================

function evaluate_filter_performance(folder,Fs)

fprintf("Evaluating filter performance...\n")

files = {
    "bandpass_filtered.csv"
    "butterworth_filtered.csv"
    "chebyshev_notch_filtered.csv"
    "kalman_filtered.csv"
    "adaptive_filtered.csv"
    };

labels = {
    "Bandpass"
    "Butterworth"
    "Chebyshev Notch"
    "Kalman"
    "Adaptive"
    };

n = length(files);

SNR = zeros(n,1);
baseline = zeros(n,1);
powerline = zeros(n,1);

for i = 1:n

    filepath = fullfile(folder,files{i});

    if ~isfile(filepath)
        warning("File missing: %s",files{i})
        continue
    end

    T = readtable(filepath);

    ecg = T.leadII;      % evaluate using Lead II

    %% --- SNR ESTIMATION ---

    signal_power = var(ecg);

    noise_est = ecg - movmean(ecg,round(Fs*0.2));

    noise_power = var(noise_est);

    SNR(i) = 10*log10(signal_power/noise_power);

    %% --- BASELINE WANDER POWER (<0.5 Hz) ---

    [b,a] = butter(2,0.5/(Fs/2),'low');

    baseline_component = filtfilt(b,a,ecg);

    baseline(i) = var(baseline_component);

    %% --- POWERLINE NOISE (60 Hz) ---

    f = abs(fft(ecg));

    freq = (0:length(f)-1)*(Fs/length(f));

    idx = find(freq>58 & freq<62);

    powerline(i) = mean(f(idx));

end

evaluate_filter_performance(run_folder,Fs)

%% ===============================
% CREATE PERFORMANCE TABLE
%% ===============================

results = table(labels,SNR,baseline,powerline,...
    'VariableNames',{'Filter','SNR_dB','BaselineDrift','PowerlineNoise'});

writetable(results,fullfile(folder,"filter_performance.csv"))

%% ===============================
% NORMALIZE SCORES FOR RANKING
%% ===============================

score = normalize(SNR) ...
      - normalize(baseline) ...
      - normalize(powerline);

results.Score = score;

results = sortrows(results,'Score','descend');

writetable(results,fullfile(folder,"filter_ranking.csv"))

%% ===============================
% COMPARISON PLOT
%% ===============================

figure('Color','w')

tiledlayout(3,1)

nexttile
bar(categorical(labels),SNR)
ylabel("SNR (dB)")
title("Signal-to-Noise Ratio")

nexttile
bar(categorical(labels),baseline)
ylabel("Baseline Drift")
title("Baseline Wander Power")

nexttile
bar(categorical(labels),powerline)
ylabel("60 Hz Noise")
title("Powerline Interference")

sgtitle("ECG Filter Performance Comparison")

exportgraphics(gcf,fullfile(folder,"filter_comparison_plot.pdf"))

fprintf("Filter evaluation complete\n")

end