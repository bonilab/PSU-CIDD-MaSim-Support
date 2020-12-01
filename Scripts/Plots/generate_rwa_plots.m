% generate_rwa_plots.m
%
% Generate heatmaps and frequency plot based upon the data downloaded by 
% the Python loader script.
addpath('include');
clear;

DIRECTORY = '../Loader/out';
FREQUENCY = '../Loader/out/*frequency*.csv';

STARTDATE = '2009-1-1';
if ~exist('out', 'dir'), mkdir('out'); end

% NOTE for most of these the default image size is 2560 x 1440 at 300 DPI
%      exact sizes can be changed though
plot_heatmaps(FREQUENCY, STARTDATE);
plot_district_frequency(DIRECTORY, STARTDATE);
plot_regional_frequency(DIRECTORY, STARTDATE);
plot_national_frequency(DIRECTORY, STARTDATE);