function c = whitebluered(m)
    %WHITEBLUERED    White, to blue, to red color map.
    %   WHITEBLUERED(M), is an M-by-3 matrix that defines a colormap.
    %   The colors begin with white to blue, range through shades of
    %   blue to red, and then through shades of red to bright red.
    %   WHITEBLUERED, by itself, is the same length as the current figure's
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
        red = [gradient; flipud(gradient)];
        green = (m:-1:1)' / max(m, 1);
        blue = [ones(m * 0.5, 1); gradient]; 
    else
        % From [1 1 1] to [0 0.5 1], then [0 0.5 1] to [1 0 0];
        gradient = ((floor(m * 0.5)):-1:1)' / max(floor(m * 0.5), 1);         
        red = [1; gradient; flipud(gradient)];
        green = (m:-1:1)' / max(m, 1);
        blue = [1; ones(floor(m * 0.5), 1); gradient]; 
    end        
    c = [red green blue];
end
    