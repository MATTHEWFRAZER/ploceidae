from ploceidae.core.configurators import BasicConfigurator

basic_configurator = BasicConfigurator()
fake_dependency_wrapper_no_setup = basic_configurator.get_dependency_wrapper()
fake_container_no_setup = basic_configurator.get_container()
