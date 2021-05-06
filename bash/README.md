# Compute Cluster Support

The bash scripts contained within this directory are intended for use with the [Roar supercomputing cluster](https://www.icds.psu.edu/computing-services/) at Penn State. As such, they may be of limited value on other compute infrastructure, although the organization of the scripts may be useful exemplars.

## Running Replicates
Typically, a project has multiple configurations, or *studies*, that may contain changes to the underlying system intended for study as to how environmental changes (e.g., increased access to treatments) may affect the development of antimalarial resistance in the parasite. These configurations are typically run as *replicates* 50 to 100 times to ensure that there is a sufficient dataset for analysis. While these configurations may be run manually, this can quickly become a tedious task due to the numbers involved.

To allow for the necessary replicates for project's studies to be run, the `calibrationLib.sh` script contains the function `runReplicates` which a filename with replicate information and Penn State user name that jobs will run under as inputs. A simple and complete script to use the function would look like the following:

```bash
#!/bin/bash
source ./calibrationLib.sh
runReplicates 'replicates.csv' 'nittany_lion'
```

The filename must be structured in CSV format with two columns: the filename for the replicates job, and the number of replicates to run:

```csv
dha-ppq.job,50
al.job,50
```

As with the job files for the replicates, this "runner" script can be invoked via a job file and with a sufficiently large enough wall time it should be capable of running all of the replicates for a given project without intervention from users.