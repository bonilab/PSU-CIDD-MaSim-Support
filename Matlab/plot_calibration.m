% plot_calibration.m
%
% Generate a scatter plot of the EIR vs. PfPR, categorized by the popuation
% bin that the data is in.
%
% Example: plot_calibration('data/calibration.csv', [797, 1417, 2279, 3668, 6386, 12627, 25584, 53601, 117418] , 'eir')

function [] = plot_calibration(filename, population, type) 
    if strcmp(type, 'beta')
        plot_beta_calibration(filename, population);
    elseif strcmp(type, 'eir')
        plot_eir_calibration(filename, population);
    else
        error('Unknown plot type: %s', type);
    end     
end

% Load the data from the calibration file
function [data] = load(filename)
    data = readtable(filename);
    data = removevars(data, {'replicateid', 'filename'});
    data = data{:, :};
end

% Plot the beta vs. PfPR values
function [] = plot_beta_calibration(filename, population)
    labels = {};

    hold on;
    colormap('gray');
    data = load(filename);
    
    for value = population
        pfpr = data(data(:, 1) == value, 4);
        beta = data(data(:, 1) == value, 3);
        scatter(beta, pfpr, 'filled');    
        labels{end + 1} = sprintf('Population %.2d', value);
    end
    hold off;

    % Format the x-axis
    xlabel('Beta', 'fontsize', 24);
    
    format_plot(labels);
end

% Plot the EIR vs PfPR value
function [] = plot_eir_calibration(filename, population)
    labels = {};
    colors = turbo(size(population, 2) + 1);
        
    hold on;
    data = load(filename);
    for value = population
        eir = log10(data(data(:, 1) == value, 4));
        pfpr = data(data(:, 1) == value, 6);
        scatter(eir, pfpr, 12, colors(size(labels, 2) + 1, :), 'filled');    
        labels{end + 1} = sprintf('Population %.2d', value);
    end
    hold off;
    
    % Format the y-axis
    xlabel('EIR', 'fontsize', 24);
    xlim([-2 3]);
    xticks([-4 -3 -2 -1 0 1 2 3 4]);
    xticklabels({'0.0001', '0.001', '0.01', '0.1', '1', '10', '100', '1,000', '10,000'});
    
    format_plot(labels);
end

% Common function to format the plot
function [] = format_plot(labels) 
    % Add the PfPR ticks and labels
    ylabel('PfPR_{2-10}', 'fontsize', 24);
    ylim([0 100]);
    
    % Constrain the axis
    axis tight;

    % Set title, legend, and overall font size
    title({'Beta Calibration Data' 'EIR vs PfPR_{2-10}'}, 'fontsize', 36);
    legend(labels, 'Location', 'northwest', 'NumColumns', 2);
    legend('boxoff');
    plot = gca;
    plot.FontSize = 18;
end
