clear;
% Load the data
data = csvread('data/calibration.csv', 1);
population = transpose(unique(data(:, 3)));

% Filter the plot
population = population(population == 2125);

% Filter the data
data = data(data(:, 3) == 2125, :);     % Population
data = data(data(:, 4) == 0.616, :);    % Treatment

beta = data(:, 5);      % Beta
pfpr = data(:, 7);      % PfPR


%find_beta(pfpr, beta, 21.8075, 'exp2')

f = fit(pfpr, beta, 'poly2');
plot(f, pfpr, beta);
xlabel('PfPR');
ylabel('Beta');


function [beta] = find_beta(pfprData, betaData, pfpr, func)
    % Curve fit the data provided using the function indicated
    result = fit(pfprData, betaData, func); 
    
    % Use string processing to the convert the results of fit to soemthing
    % that can be run via eval
    f = string(formula(result)); 
    names = coeffnames(result);
    vals = coeffvalues(result);
    for ndx = 1:length(names)
        f = strrep(f, string(names(ndx)), string(vals(ndx)));
    end
    
    % Plug the PfPR in for x and solve for the y (beta)
    x = pfpr;
    beta = eval(f);
end

