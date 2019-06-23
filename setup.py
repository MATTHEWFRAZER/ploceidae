from os import path
from setuptools import setup, find_packages

with open(path.join("ploceidae", "requirements.txt")) as req:
    # handles custom package repos
    requirements = [requirement for requirement in req.read().splitlines() if not requirement.startswith("-")]

setup(name="ploceidae",
      install_requires=requirements,
      description="dependency injection library",
      keywords="dependency injection DI",
      url="https://github.com/MATTHEWFRAZER/ploceidae",
      author="Matthew Frazer",
      author_email="mfrazeriguess@gmail.com",
      packages=find_packages(),
      include_package_data=False,
      zip_safe=False,
      )


