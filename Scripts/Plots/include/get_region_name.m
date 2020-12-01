% getRegionName.m
%
% Get the region name and sort order / id from the file.
function [name, sort] = get_region_name(index)
    % Determine where the location file is
    filename = strrep(mfilename('fullpath'), mfilename, 'rwa_political.csv');
    
    % Open and return the name and sort order
    data = readtable(filename);
    name = string(data(data.PROVINCE_SORT == index, 2).PROVINCE{1});
    sort = index;
end