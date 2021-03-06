import os

from setuptools import setup, find_packages

package_name = "ploceidae"
requirements_file = "requirements.txt"
build_version_txt = "build_version.txt"

if not os.path.exists(requirements_file):
      # when we deploy this, this is where requirements will be
      requirements_file = os.path.join("{0}.egg-info".format(package_name), "requires.txt")

with open(requirements_file) as req:
    # handles custom package repos
      requirements = [requirement for requirement in req.read().splitlines() if not requirement.startswith("-")]

if not os.path.exists(build_version_txt):
      with open(os.path.join("{0}.egg-info".format(package_name), "PKG-INFO")) as pkg_info:
            pkg_info.readline()
            pkg_info.readline()
            build_number = pkg_info.readline().split(":")[1]

else:
      with open(build_version_txt) as build_file:
            release_number = build_file.readline()
            build_number_split = release_number.split(".")
            build_number = "{0}.{1}.{2}.{3}".format(*build_number_split)

setup(name=package_name,
      install_requires=requirements,
      description="dependency injection library",
      keywords="dependency injection DI",
      url="https://github.com/MATTHEWFRAZER/ploceidae",
      author="Matthew Frazer",
      author_email="mfrazeriguess@gmail.com",
      packages=find_packages(),
      include_package_data=False,
      zip_safe=False,
      version=build_number,
      classifiers=[
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            ]
      )


