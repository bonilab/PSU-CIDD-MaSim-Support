% plot_national_frequency.m
%
% This function generates frequency plots at the national level based upon 
% the data files in the supplied directory.


% Generate plots based upon the summary input files
function [] = plot_national_frequency(directory, startDate)
    files = dir(directory);
    for ndx = 1:length(files)
        % Skip anything that is not the directories we are looking for
        if ~files(ndx).isdir, continue; end
        if strcmp(files(ndx).name(1), '.'), continue; end

        % Plot the national summary and district summary
        filename = fullfile(files(ndx).folder, files(ndx).name);
        [plotTitle, file] = parse_name(files(ndx).name);        
        generate(filename, startDate, plotTitle, file);
    end
end

% Generates a single plot based upon the data files in the supplyed
% subdirectory, saves the plot to disk.
function [] = generate(directory, startDate, plotTitle, file)
    
    hold on;
    
    replicates = 0;
    files = dir(fullfile(directory, '*.csv'));
    for ndx = 1:length(files)
        % Load the data, note the unique days
        filename = fullfile(files(ndx).folder, files(ndx).name);
        data = csvread(filename, 1, 0);
        days = transpose(unique(data(:, 2)));
        
        % Allocate the arrays
        frequency = zeros(size(days, 2), 1);
        occurrences = zeros(size(days, 2), 1);
        
        % Get the data, format the date in the process
        for ndy = 1:length(days)
            frequency(ndy) = sum(data(data(:, 2) == days(ndy), 7)) / sum(data(data(:, 2) == days(ndy), 4));
            occurrences(ndy) = sum(data(data(:, 2) == days(ndy), 5));
            days(ndy) = addtodate(datenum(startDate), days(ndy), 'day');
        end
                
        % Plot the data
        yyaxis left;
        plot(days, frequency, '-');
        yyaxis right;
        plot(days, log10(occurrences), '.-');
        
        % Update the replicate count
        replicates = replicates + 1;
    end
    
    hold off;

    % Add labels, title, apply formatting
    datetick('x', 'yyyy');
    xlabel('Model Year');
    yyaxis left;
    ylabel('580Y Frequency');
    yyaxis right;
    ylabel('Occurances of 580Y (log10)');    

    % Apply the title
    sgtitle({sprintf('580Y Frequency %s (%d Replicates)', ...
        plotTitle, length(files))}, 'FontSize', 24);  
    
    graphic = gca;
    graphic.FontSize = 22;
    
    % Save and close
    set(gcf, 'Position',  [0, 0, 2560, 1440]);
    print('-dtiff', '-r300', sprintf('out/%s-frequency-replicates.png', file));
    clf;
    close;    
end