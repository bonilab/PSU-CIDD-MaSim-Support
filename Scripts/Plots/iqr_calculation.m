% iqr_calculation.m
% 
% Scan the directory of the loader output and report the IQR for the
% replicates of each directory. 
clear;

scan('../Loader/out/');

function [] = scan(path)
    files = dir(path);
    for ndx = 1:length(files)
        if ~files(ndx).isdir, continue; end
        if strcmp(files(ndx).name(1), '.'), continue; end
        report(fullfile(files(ndx).folder, files(ndx).name), files(ndx).name);
    end
end

function [] = report(path, name)
    values = [];
        
    files = dir(fullfile(path, '*.csv'));
    for ndx = 1:length(files)
        % Load the data and discard everything but the last year
        filename = fullfile(files(ndx).folder, files(ndx).name);
        data = csvread(filename, 1, 0);
        data = data(data(:, 2) > 10958, :);

        % Find the max value for the year
        values = [values max(sum(data(:, 7)) / sum(data(:, 4)))];
    end
    
    % Find 25th, 50th, and 75th percentile of the data
    result = prctile(values, [25 50 75]);
    
	% Pretty print the results
    if strcmp(name, 'bfa-import')
        fprintf("%s: %.4e%% (%.4e%% to %.5e%%), max: %e.5%%\n", name, result(2), result(1), result(3), max(values));
        return
    end
    fprintf("%s: %.4g%% (%.4g%% to %.4g%%), max: %.4g%%\n", name, result(2), result(1), result(3), max(values));
end

