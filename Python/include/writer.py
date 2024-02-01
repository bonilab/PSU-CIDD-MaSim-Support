# writer.py
#
# This module contains the functions that are used to create bash scripts to run locally or on the cluster.
import pathlib
import stat


# Prepare the script that will run on the cluster
def save_cluster(pfpr, treatments, populationBreaks, filename, prefix, username):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLib.sh\n\n")
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


# Prepare the script that will run locally
def save_local(pfpr, treatments, populationBreaks, filename, prefix):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./localCalibrationLib.sh\n\n")
        script.write("checkDependencies {}\n\n".format(prefix))

        # Print the ASC file generation commands
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(
            " ".join([str(int(x)) for x in sorted(populationBreaks)])))
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n\n".format(
            " ".join([str(int(x)) for x in sorted(pfpr.keys())])))

        # Print the zone matter
        for zone in pfpr.keys():
            script.write("run {} \"\\\"{}\\\"\" \"\\\"{}\\\"\" {}\n".format(
                zone,
                " ".join([str(int(x)) for x in sorted(populationBreaks)]),
                " ".join([str(x) for x in sorted(treatments[zone])]),
                prefix))

    # Set the file as executable
    script = pathlib.Path(filename)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)