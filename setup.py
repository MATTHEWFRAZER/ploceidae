import os

from setuptools import setup, find_packages

package_name = "ploceidae"
requirements_file = "requirements.txt"
if not os.path.exists(requirements_file):
      # when we deploy this, this is where requirements will be
      requirements_file = os.path.join("{0}.egg-info".format(package_name), "requires.txt")

with open(requirements_file) as req:
    # handles custom package repos
    requirements = [requirement for requirement in req.read().splitlines() if not requirement.startswith("-")]

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
      version="1.0.8",
      classifiers=[
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            ]
      )


