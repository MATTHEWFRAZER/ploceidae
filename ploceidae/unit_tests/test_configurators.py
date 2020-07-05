from ploceidae.core.configurators import BasicConfigurator

class TestConfigurators:
    def test_multiple_instances_of_basic_configurators_do_not_share_the_same_dependency_graph_manager(self):
        basic_configurator1 = BasicConfigurator()
        basic_configurator2 = BasicConfigurator()
        assert basic_configurator1.dependency_graph_manager is not basic_configurator2.dependency_graph_manager