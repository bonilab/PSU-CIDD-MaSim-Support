# utility.py
#
# Various utility functions for Python

import sys

# Progress bar for console applications
#
# Adopted from https://stackoverflow.com/a/37630397/1185
def progressBar(current, total, barLength = 20):
    percent = float(current) / total
    arrow = '-' * int(round(percent * barLength)-1) + '>'
    spaces = ' ' * (barLength - len(arrow))

    if int(percent) != 1:
        sys.stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()
    else:
        print "\rProgress: [{0}] {1}%".format('-' * barLength, int(round(percent * 100)))

    