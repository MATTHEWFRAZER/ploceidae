from ploceidae.core.configurators import BasicConfigurator

basic_configurator = BasicConfigurator(ploceidae_setup_module="ploceidae.unit_tests.test_project.ploceidae_setup")
fake_dependency_wrapper_with_setup = basic_configurator.get_dependency_wrapper()
fake_container_with_setup = basic_configurator.get_container()
