# writer.py
#
# This module contains the functions that are used to create bash scripts to 
# run locally or on the cluster. The functions are intentionally pretty similar
# since it's unclear how much they might drift over time as local versus 
# cluster environments change.
import pathlib
import stat


# Prepare the script that will run the initial beta sweep on the cluster
def run_cluster(pfpr, treatments, populationBreaks, filename, prefix, username):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationCluster.sh\n\n")
        script.write("checkDependencies {}\n\n".format(prefix))

        # Print the ASC file generation commands
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(
            " ".join([str(int(x)) for x in sorted(populationBreaks)])))
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n\n".format(
            " ".join([str(int(x)) for x in sorted(pfpr.keys())])))

        # Print the zone matter
        for zone in pfpr.keys():
            script.write("run {} \"\\\"{}\\\"\" \"\\\"{}\\\"\" {} {}\n".format(
                zone,
                " ".join([str(int(x)) for x in sorted(populationBreaks)]),
                " ".join([str(x) for x in sorted(treatments[zone])]),
                prefix, username))

    # Set the file as executable
    script = pathlib.Path(filename)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)

# Prepare the script that will use a CSV file to refine the betas on the cluster
def reduce_cluster(filename, prefix, population, zones, reduction, username):
    with open(filename, "w") as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationCluster.sh\n")
        script.write("checkDependencies {}\n".format(prefix))

        # Print the ASC file generation commands
        value = " ".join([str(int(x)) for x in sorted(population)])
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(value.strip()))
        value = " ".join([str(int(x)) for x in sorted(zones.keys())])
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n".format(value.strip()))

        # Print the run command for the script
        script.write("runCsv '{}' {} {}\n".format(reduction, prefix, username))

    # Set the file as executable
    script = pathlib.Path(filename)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)            


# Prepare the script that will use a CSV file to refine the betas  locally
def reduce_local(filename, prefix, population, zones, reduction):
    with open(filename, "w") as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLocal.sh\n")
        script.write("set_spooler\n")
        script.write("check_dependencies {}\n".format(prefix))

        # Print the ASC file generation commands
        value = " ".join([str(int(x)) for x in sorted(population)])
        script.write("generate_asc \"\\\"{}\\\"\"\n".format(value.strip()))
        value = " ".join([str(int(x)) for x in sorted(zones.keys())])
        script.write("generate_zone_asc \"\\\"{}\\\"\"\n".format(value.strip()))

        # Print the run command for the script
        script.write("run_csv '{}' {}\n".format(reduction, prefix))

    # Set the file as executable
    script = pathlib.Path(filename)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)   

# Prepare the script that will run the initial beta sweep locally
def run_local(pfpr, treatments, populationBreaks, filename, prefix):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLocal.sh\n\n")
        script.write("set_spooler\n")
        script.write("check_dependencies {}\n\n".format(prefix))

        # Print the ASC file generation commands
        script.write("generate_asc \"\\\"{}\\\"\"\n".format(
            " ".join([str(int(x)) for x in sorted(populationBreaks)])))
        script.write("generate_zone_asc \"\\\"{}\\\"\"\n\n".format(
            " ".join([str(int(x)) for x in sorted(pfpr.keys())])))

        # Print the zone matter
        for zone in pfpr.keys():
            script.write("run_sweep {} \"\\\"{}\\\"\" \"\\\"{}\\\"\" {}\n".format(
                zone,
                " ".join([str(int(x)) for x in sorted(populationBreaks)]),
                " ".join([str(x) for x in sorted(treatments[zone])]),
                prefix))

    # Set the file as executable
    script = pathlib.Path(filename)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)