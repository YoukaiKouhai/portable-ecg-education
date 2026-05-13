clear; clc; close all;

%% ===============================
%  USER SETTINGS
%% ===============================
port = "COM5";              
baud = 115200;
record_time = 20;           
Vref = 5;                   
ADCmax = 1023;
window_sec = 3;             

%% ===============================
%  CREATE RUN FOLDER
%% ===============================
base_folder = pwd;
folder_info = dir(base_folder);
folder_names = {folder_info([folder_info.isdir]).name};
run_numbers = [0]; 
for i = 1:length(folder_names)
    name = folder_names{i};
    if length(name) >= 7 && strcmp(name(1:4), 'RUN_')
        num_part = name(5:7);
        if all(isstrprop(num_part, 'digit')), run_numbers(end+1) = str2double(num_part); end
    end
end
run_folder = fullfile(base_folder, sprintf("RUN_%03d", max(run_numbers) + 1));
mkdir(run_folder);
fprintf("Saving data to: %s\n", run_folder);

%% ===============================
%  SETUP LIVE VISUALIZATION
%% ===============================
fig = figure('Name', 'Pro ECG Monitor', 'Position', [50, 50, 1000, 800], 'Color', 'k');

titles = {'Lead I', 'Lead II', 'Lead III'};
colors = {'y', 'g', 'c'};
ax = gobjects(3,1); 
hLine = gobjects(3,1); % Use gobjects to properly preallocate graphics handles

for i = 1:3
    ax(i) = subplot(3,1,i);
    set(ax(i), 'Color', 'k', 'XColor', [0 0.5 0], 'YColor', [0 0.5 0], 'GridColor', [0 0.2 0]);
    hold(ax(i), 'on'); 
    grid(ax(i), 'on');
    hLine(i) = animatedline('Parent', ax(i), 'Color', colors{i}, 'LineWidth', 1.5);
    title(ax(i), titles{i}, 'Color', colors{i});
    ylabel(ax(i), 'mV');
end
xlabel(ax(3), 'Time (s)', 'Color', 'g');

hr_text = annotation('textbox', [0.8 0.85 0.15 0.1], 'String', 'HR: --', ...
    'Color', 'r', 'FontSize', 24, 'FontWeight', 'bold', 'EdgeColor', 'none');

%% ===============================
%  DATA COLLECTION
%% ===============================
try
    s = serialport(port, baud);
    flush(s);
    configureTerminator(s, "LF");
catch
    error("Could not open Serial Port %s. Check connection.", port);
end

raw_data = [];
time_data = [];
start_time = tic;
last_plot_update = tic;

fprintf("Recording Live... \n");

try
    while toc(start_time) < record_time
        if s.NumBytesAvailable > 0
            line = readline(s);
            vals = str2double(split(line, ","));
            
            if length(vals) == 2 && all(~isnan(vals))
                t_now = toc(start_time);
                
                % 1. Convert Raw to mV (Centered around 2.5V bias)
                mV_I  = ((vals(1)/ADCmax)*Vref - 2.5) * 1000;
                mV_II = ((vals(2)/ADCmax)*Vref - 2.5) * 1000;
                mV_III = mV_II - mV_I;
                
                % 2. Store Data
                raw_data = [raw_data; vals'];
                time_data = [time_data; t_now];
                
                % 3. Update Animated Lines (Explicit calls)
                addpoints(hLine(1), t_now, mV_I);
                addpoints(hLine(2), t_now, mV_II);
                addpoints(hLine(3), t_now, mV_III);
                
                % 4. UI Update
                if toc(last_plot_update) > 0.05
                    for i = 1:3
                        if t_now > window_sec
                            xlim(ax(i), [t_now - window_sec, t_now]);
                        else
                            xlim(ax(i), [0, window_sec]);
                        end
                    end
                    
                    % Simple HR logic
                    if length(time_data) > 100
                        recent_idx = time_data > (t_now - 2);
                        recent_sig = raw_data(recent_idx, 2); 
                        % Basic thresholding for HR
                        thresh = mean(recent_sig) + 1.2*std(recent_sig);
                        [pks, ~] = findpeaks(recent_sig, 'MinPeakHeight', thresh);
                        if length(pks) >= 2
                            set(hr_text, 'String', sprintf('HR: %d', length(pks)*30));
                        end
                    end
                    
                    drawnow limitrate;
                    last_plot_update = tic;
                end
            end
        end
    end
catch ME
    warning("Loop interrupted: %s", ME.message);
end

%% ===============================
%  POST-PROCESSING & SAVING
%% ===============================
fprintf("Processing final leads and applying filters...\n");
if isvalid(s), clear s; end

if ~isempty(raw_data)
    t = time_data;
    L1 = ((raw_data(:,1)/ADCmax)*Vref - 2.5)*1000;
    L2 = ((raw_data(:,2)/ADCmax)*Vref - 2.5)*1000;
    L3 = L2 - L1;
    aVR = -(L1 + L2)/2;
    aVL = L1 - L2/2;
    aVF = L2 - L1/2;

    final_table = table(t, L1, L2, L3, aVR, aVL, aVF, 'VariableNames',{'t','LeadI','LeadII','LeadIII','aVR','aVL','aVF'});
    writetable(final_table, fullfile(run_folder, "final_data.csv"));
    msgbox(sprintf("Data saved to %s", run_folder), "Recording Complete");
else
    disp("No data recorded.");
end