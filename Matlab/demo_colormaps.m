% demo_colormaps.m
%
% Demonstrate the colormaps that are included in the repository.
addpath('colormaps');

files = dir('colormaps/*.m');
for ndx = 1:length(files)
    
    % Generate the colormap
    name = strrep(files(ndx).name, '.m', '');
    handle = str2func(name);
    map = handle();
    
    % Generate a demo contour plot
    ax(ndx) = subplot(length(files), 1, ndx);
    hold on;
    fcontour(@(x,y) sin(3*x).*cos(x+y),[0 3 0 3],'Fill','on','LineColor','k')
    colormap(ax(ndx), map);
    colorbar('Ticks', []);
    title(name)
    hold off;
end
