% parse_name.m
%
% Generate the name (title) and filename to use based upon the input filename 
function [name, file] = parse_name(file)
    prefix = strrep(file, '-frequency-map.csv', '');
    switch prefix
        case 'rwa-slow'
            name = 'with 0.0001983 Mutation Rate';
            file = 'de-novo-0.0001983';
        case 'rwa-fast'
            name = 'with 0.001983 Mutation Rate';
            file = 'de-novo-0.001983';       
        otherwise
            error("No mapping for prefix %s", prefix);
    end
end

