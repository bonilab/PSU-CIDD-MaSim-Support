# MATLAB Documentation

## Functions

The following .m files are intended to be used as functions either from other scripts, or by themselves within MATLAB

### plot_population.m

This function generates a basic plot from the model validation data of the population growth. Three input parameters are required:

- `filename` is the validation file created by `getverificationstudy`
- `startDate` is the model start date in YYYY-MM-DD format
- `scalar` is the population scaling parameter (`artificial_rescaling_of_population_size` in the YAML configuration file)

An example of a call to the function is:

```Matlab
plot_population('verification-data.csv', '2021-12-17', 0.25);
```

### plot_validation.m

This function offers two methods for generating figures from model validation data. Two input files are required:

- `modelData` which is created by `getverificationstudy`
- `referenceData` which should contain the population weighted <em>Pf</em>PR<sub>2-10</sub> values in the second column, and the administrative district identifier in column one

The basic version for calling the function is:

```Matlab
plot_validation('cases', 'verification-data.csv', 'weighted_pfpr.csv')
```

However, the function supports variable arguments with the following name-value pairs, where the name is case-sensitive:

**ci** - Credible interval data as an array where the first index is the value, and the second and third indices are the lower and upper bounds, respectively.\
**country** - The name of the country as a string, also appends the title to the figure.\
**treated** (_default: 1.0_) - The percentage of the total clinical cases that were treated, as a decimal. This adjustment is intended for when the reported count of individuals receiving treatment includes both public and private market drugs.
