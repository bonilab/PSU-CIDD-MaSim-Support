% get_location_region.m
%
% Get the region name and sort order / id from the file.
function [name, sort] = get_location_region(index)
    % Determine where the location file is
    filename = strrep(mfilename('fullpath'), mfilename, 'rwa_political.csv');
    
    % Open and return the name and sort order
    data = readtable(filename);
    name = string(table2cell(data(index, 2)));
    sort = cell2mat(table2cell(data(index, 3)));
end