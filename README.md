# PSU-CIDD-MaSim-Support

This repository contains analysis and support scripts used for modeling the prevalence of malaria (*P. falciparum*) in various countries using the main malarial simulation. Generally the code is organized with the assumption that most scripts will be written in Python; however, a subdirectory for Matlab code is included which contains some useful functions for plotting various data points from the simulation related to calibration and validation.

The main repository for the simulation can be found at [rjzupko/PSU-CIDD-Malaria-Simulation](https://github.com/rjzupkoii/PSU-CIDD-Malaria-Simulation) or [maciekboni/PSU-CIDD-Malaria-Simulation](https://github.com/maciekboni/PSU-CIDD-Malaria-Simulation).

---

### Repository Organization

`/` - The root directory contains scripts that may be run from the command line that of use with the simulation.

`bash/` - This directory contains Bash scripts as well as job files that may be manipulated by the Bash scripts to run replicates on the [Roar Supercomputer](https://www.icds.psu.edu/computing-services/roar-user-guide/).

`matlab/` - This directory contains Matlab functions that can be used to generate plots for various comparison points used for model calibration and validation.

`python/` - This directory contains the Python scripts that invoked by the `bash` scripts in the root directory of this repository. \
`python/include/` - This directory contains Python scripts that contain shared code and cannot be run on their own.

`.pep8speaks.yml` - Configuration file for [pep8speaks](https://github.com/OrkoHunter/pep8speaks) which uses codes from [pycodestyle](https://github.com/PyCQA/pycodestyle/blob/master/docs/intro.rst).

### Dependencies

The following dependencies need to be installed for all of the Python scripts to operate and can be installed individually via `pip install`: 

- jenkspy: https://pypi.org/project/jenkspy/
- numpy : https://pypi.org/project/numpy/

Or, all the dependencies can be installed via `pip install` using the `Python/requirements.txt` file:

```bash
pip install -r requirements.txt
```

The MATLAB calibration validation scripts require the Signal Processing Toolbox be installed and were last updated with MATLAB R2021b.

### Usage
Presently these scripts are only tested to run on Linux or Windows vis the Windows Subsystem for Linux. In order to run these scripts you will first need to `git clone` the repository to your local computer. Once cloned you can access them by adding them to the `PATH` variable:

**Per Session**, from the root of the repository
```bash
PATH=$PATH:`pwd`
```

**Via Configuration**
1. Open `.bashrc` (`vi ~/.bashrc`)
2. Add the line `PATH=$PATH:path_to_repository` where `path_to_repository` is the full path to the root of the repository.
3. Save and close
4. Reload `.bashrc` (`source ~/.bashrc`)

# Sources

Adam Auton (2021). Red Blue Colormap (https://www.mathworks.com/matlabcentral/fileexchange/25536-red-blue-colormap), MATLAB Central File Exchange. Retrieved August 9, 2021.
