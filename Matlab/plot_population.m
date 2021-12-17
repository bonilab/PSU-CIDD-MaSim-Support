% plot_population
%
% Generate a popuation reference plot and final year metrics  based upon
% the validation data provided. The Y-axis is fixed as the popuation in 
% millions.
function [] = plot_population(filename, startDate, scalar)

    % Read the data and parse out the monthly population
    data = readmatrix(filename);
    dates = unique(data(:, 1));
    population = zeros(size(dates, 1), 1);
    for ndx = 1:size(dates, 1)
        population(ndx) = sum(data(data(:, 1) == dates(ndx), 3));
    end
        
    % Generate the plot
    plot(dates + datenum(startDate), (population / scalar) / 1000000);
    datetick('x', 'yyyy');
    axis tight;
    
    % Label the axis
    ylabel('Population (Millions)');
    xlabel('Model Year');

    % Calcluate the percent growth
    growth = ((population(end) - population(end - 12)) / population(end - 12)) * 100;
    
    % Report the final metrics
    lastDate = datetime(dates(end) + datenum(startDate), 'ConvertFrom', 'datenum');
    lastDate.Format = 'yyyy-MM-dd';
    fprintf('Population in %s\n', lastDate);
    fprintf('Real Simulated Population: %d\n', population(end));
    fprintf('Scaled Simulated Population: %d\n', population(end) / scalar);
    fprintf('Final Year Growth: %f%%\n', growth);    
end