% get_location_name.m
%
% Get the location name from the file.
function [name, sort] = get_location_name(index)
    % Determine where the location file is
    filename = strrep(mfilename('fullpath'), mfilename, 'rwa_political.csv');
    
    % Open and return the name and sort order
    data = readtable(filename);
    name = string(table2cell(data(index, 4)));
    sort = cell2mat(table2cell(data(index, 5)));
end