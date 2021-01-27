% plot_district_frequency.m
%
% This function generates frequency plots at a district level based upon 
% the data files in the supplied directory.


% Main entry point for the function, scans the supplied directory for
% subdirectories organized by mutation rate.
function [] = plot_district_frequency(directory, startDate)
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
    files = dir(fullfile(directory, '*.csv'));
    for ndx = 1:length(files)
        
        % Load the data, note the unique days
        filename = fullfile(files(ndx).folder, files(ndx).name);
        data = csvread(filename, 1, 0);
        dn = prepareDates(filename, 2, startDate);
        
        % Load the replicates to the subplots based upon the district
        for district = transpose(unique(data(:, 3)))
            % Apply the name and correct sort
            [name, sort] = get_location_name(district);
            subplot(6, 5, sort);
            title(name);
            
            hold on;          
            plot(dn, data(data(:, 3) == district, 7) ./ data(data(:, 3) == district, 4));
            
            % Make sure the date labels are correct
            xlim([min(dn), max(dn)]);     
            datetick('x', 'yyyy');
        end        
    end

    % Apply the common labels
    handle = axes(gcf, 'visible', 'off'); 
    handle.XLabel.Visible = 'on';
    handle.YLabel.Visible = 'on';
	handle.FontSize = 22;
    ylabel(handle, '561H Frequency');
    xlabel(handle, 'Model Year');
    
    % Apply the title
    sgtitle({sprintf('561H Frequency %s (%d Replicates)', ...
        plotTitle, length(files))}, 'FontSize', 24);
    
    % Save and close
    set(gcf, 'Position',  [0, 0, 2560, 1440]);
    print('-dtiff', '-r300', sprintf('out/%s-frequency-districts.png', file));
    clf;
    close;  
end