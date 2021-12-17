% plot_population
%
% Generate a popuation reference plot based upon the validation data
% provided. The Y-axis is fixed as the popuation in millions.

function [] = plot_population(filename, startDate, scalar)
    data = readmatrix(filename);
    dates = unique(data(:, 1));
    
    population = zeros(size(dates, 1), 1);
    for ndx = 1:size(dates, 1)
        population(ndx) = sum(data(data(:, 1) == dates(ndx), 3));
    end
    
    plot(dates + datenum(startDate), (population / scalar) / 1000000);
    datetick('x', 'yyyy');
    axis tight;
    
    ylabel('Population (Millions)');
    xlabel('Model Year');
end