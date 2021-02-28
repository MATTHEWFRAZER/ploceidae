import argparse
import subprocess

parser = argparse.ArgumentParser(description='Take in release build number and generate a unique build number')
parser.add_argument('release_number', type=str,
                    help='release build number')

args = parser.parse_args()

if args.release_number is None:
    raise ValueError("release number is missing")

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os

    DEVNULL = open(os.devnull, 'wb')

split_build_number = args.release_number.split(".")
build_number_prefix = ".".join(split_build_number[:-1])
build_number = int(split_build_number[-1])
new_build_number = "{0}.{2}".format(build_number_prefix, build_number)

# TODO: revisit
# while ideally, I would like separation between one liners and scripts in our build process
# this was the simplest way I could think of to implement this
# because it is done this way, it forces us to pay attention to the order in which we call into this script
while subprocess.call(["git", "rev-parse", "--verify", new_build_number], stdout=DEVNULL, stderr=DEVNULL) == 0:
    build_number += 1
    new_build_number = "{0}.{2}".format(build_number_prefix, build_number)

print(new_build_number)