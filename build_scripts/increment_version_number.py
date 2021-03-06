#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(description='Take in version increment type and output a newly incremented version')
parser.add_argument('version_increment', type=str, choices=["major", "minor", "patch"],
                    help='type of version increment')

args = parser.parse_args()

version_path = "version.txt"

if args.version_increment is None:
    raise ValueError("version increment is missing")

version = None
with open(version_path, "r") as f:
    version = f.readline()

version_numbers = list(map(int, version.split(".")))

if len(version_numbers) != 3:
    raise ValueError("version.txt is malformed. contents of version.txt: {0}".format(version))

if args.version_increment == "major":
    version_numbers[0] += 1
elif args.version_increment == "minor":
    version_numbers[1] += 1
elif args.version_increment == "patch":
    version_numbers[2] += 1
else:
    raise ValueError("invalid version increment {0}".format(args.version_increment))

with open(version_path, "w") as f:
    f.write("{0}.{1}.{2}".format(*version_numbers))