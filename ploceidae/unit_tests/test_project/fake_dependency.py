from ploceidae.unit_tests.test_project.fake_configurator_no_setup import fake_dependency_wrapper_no_setup
from ploceidae.unit_tests.test_project.fake_configurator_with_setup import fake_dependency_wrapper_with_setup

@fake_dependency_wrapper_no_setup
def fake_depenency_no_setup():
    return 8

@fake_dependency_wrapper_with_setup
def fake_depenency_with_setup():
    return 8