#!/usr/bin/python

import subprocess

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os

    DEVNULL = open(os.devnull, 'wb')

version_path = "version.txt"
build_type = "rc"

with open(version_path, "r") as f:
    version = f.readline()

build_number = 0
tag = "{0}-{1}.{2}".format(version, build_type, build_number)

# TODO: revisit
# while ideally, I would like separation between one liners and scripts in our build process
# this was the simplest way I could think of to implement this
# because it is done this way, it forces us to pay attention to the order in which we call into this script
while subprocess.call(["git", "rev-parse", "--verify", tag], stdout=DEVNULL, stderr=DEVNULL) == 0:
    build_number += 1
    tag = "{0}-{1}.{2}".format(version, build_type, build_number)

print(tag)