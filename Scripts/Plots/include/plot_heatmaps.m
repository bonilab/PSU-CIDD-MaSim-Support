% plot_heatmaps.m
%
% This function generates heatmaps at the national level based upon the
% frequency files at the supplied path with filter.

% Main entry point for the function, scans the supplied path and filter for
% files to generate heatmaps from. 
function [] = plot_heatmaps(directory, startdate)
    files = dir(directory);
    for ndx = 1:length(files)
        filename = fullfile(files(ndx).folder, files(ndx).name);
        [name, file] = parse_name(files(ndx).name);
        parse_file(filename, name, startdate);
        set(gcf, 'Position',  [0, 0, 2560, 1440]);
        print('-dtiff', '-r300', sprintf('out/%s-heatmap.png', file));
        clf;
        close;
    end
end

% Generate multiple subplots that contain heatmaps at fixed intervals, note
% that the dates are controled by the loader
function [] = parse_file(filename, name, startdate) 
    raw = csvread(filename, 1, 0);
    days = unique(raw(:, 1));

    ndx = 1;
    for day = transpose(days)
        subplot(2, 2, ndx);
        generate(raw, day, startdate);
        ndx = ndx + 1;
    end
    
    sgtitle(sprintf("580Y Frequency %s", name), 'FontSize', 24);
end

% Generate a single heatmap for the given date
function [hm] = generate(raw, date, startDate)
    % Prepare the data structure
    rows = max(raw(:, 3) + 1);
    cols = max(raw(:, 2) + 1);
    map = NaN(rows, cols);

    % Load the data on to the map structure
    data = raw(raw(:, 1) == date, :);
    for values = transpose(data)
        row = values(3) + 1;
        col = values(2) + 1;
        map(row, col) = values(4);    
    end
    
    % Covert the data, prepare the title
    days = addtodate(datenum(startDate), date, 'day');
    title = datestr(datetime(days, 'ConvertFrom', 'datenum'), 'mmmm yyyy');

    % Plot the heatmap and color bar
    hm = heatmap(map, 'MissingDataColor', [1.0 1.0 1.0]);
    hm.Colormap = colormap(flipud(autumn));
	caxis(hm, [min(raw(:, 4)) max(raw(:, 4))]);
    
    % Apply the formatting
    graphic = gca;
    graphic.FontSize = 22;    
    hm.Title = title;
    hm.XDisplayLabels = repmat(' ', cols, 1); 
    hm.YDisplayLabels = repmat(' ', rows, 1);
    grid off;
end