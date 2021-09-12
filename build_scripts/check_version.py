#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(description='Take in develop version string')
parser.add_argument('develop_version', type=str, help='develop version')

args = parser.parse_args()

if args.develop_version is None:
    raise ValueError("develop version missing")

develop_version = args.develop_version.strip()

version_path = "version.txt"

with open(version_path, "r") as f:
    branch_version = f.readline().strip()

if develop_version != branch_version:
    raise ValueError("branch version differs from develop. branch version: {0}, develop version {1}".format(branch_version, develop_version))