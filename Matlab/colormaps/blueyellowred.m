function c = blueyellowred(m)
    %BLUEYELLOWRED    Blue, to yellow, to red color map.
    %   BLUEYELLOWRED(M), is an M-by-3 matrix that defines a colormap.
    %   The colors begin with blue, range through shades of yellow-blue to 
    %   yellow-red, and then through shades of red to bright red.
    %   BLUEYELLOWRED, by itself, is the same length as the current figure's
    %   colormap. If no figure exists, MATLAB creates one.
    %
    %   For example, to reset the colormap of the current figure:
    %
    %             colormap(redblue)
    %
    %   See also HSV, GRAY, HOT, BONE, COPPER, PINK, FLAG, 
    %   COLORMAP, RGBPLOT.
    %
    %   Based on the REDBLUE function by Adam Auton, 9th October 2009
    if nargin < 1, m = size(get(gcf,'colormap'),1); end
    if (mod(m, 2) == 0)
        % From [1 1 1] to [0 0.5 1], then [0 0.5 1] to [1 0 0];
        gradient = ((m * 0.5):-1:1)' / max(m * 0.5, 1);                
        red = [flipud(gradient); ones(m * 0.5, 1)];
        green = [flipud(gradient); gradient];
        blue = [gradient; zeros(m * 0.5, 1)];
    else
        % From [1 1 1] to [0 0.5 1], then [0 0.5 1] to [1 0 0];        
        gradient = ((floor(m * 0.5)):-1:1)' / max(floor(m * 0.5), 1);                
        red = [flipud(gradient); 1; ones(floor(m * 0.5), 1)];
        green = [flipud(gradient); 1; gradient];
        blue = [gradient; 0; zeros(floor(m * 0.5), 1)];        
    end        
    c = [red green blue];
end
    