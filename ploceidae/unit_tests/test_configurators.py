import pytest

from ploceidae.utilities.importlib_utilities import ploceidae_import_module
from ploceidae.core.configurators import BasicConfigurator
from ploceidae.container import container

from ploceidae.unit_tests.test_project.fake_main import fake_dependent_no_setup, fake_dependent_with_setup
from ploceidae.unit_tests.test_project.fake_configurator_no_setup import fake_container_no_setup
from ploceidae.unit_tests.test_project.fake_configurator_with_setup import fake_container_with_setup

class TestConfigurators:
    def test_multiple_instances_of_basic_configurators_do_not_share_the_same_dependency_graph_manager(self):
        basic_configurator1 = BasicConfigurator()
        basic_configurator2 = BasicConfigurator()
        assert basic_configurator1.dependency_graph_manager is not basic_configurator2.dependency_graph_manager

    @pytest.mark.parametrize("error_to_throw", [ValueError, ModuleNotFoundError])
    def test_importlib_fails(self, monkeypatch, error_to_throw):
        ploceidae_setup_module = "fails"

        def throw(_):
            raise error_to_throw()

        try:
            monkeypatch.setattr(container, ploceidae_import_module.__name__, throw)
            basic_configurator_local = BasicConfigurator(ploceidae_setup_module=ploceidae_setup_module)
            basic_configurator_local.get_container().wire_dependencies(lambda: 5)
        except ValueError as ex:
            assert str(ex).startswith("ploceidae setup {0} could not be imported:".format(ploceidae_setup_module))
        else:
            pytest.fail()

    def test_no_ploceidae_file_provided(self):
        try:
            basic_configurator_local = BasicConfigurator()
            basic_configurator_local.get_container().wire_dependencies(lambda: 5)
        except ValueError as ex:
            pytest.fail(str(ex))

    @pytest.mark.xfail(raises=ValueError)
    def test_without_setup(self):
        assert fake_container_no_setup.wire_dependencies(fake_dependent_no_setup) == 16

    def test_with_setup(self):
        assert fake_container_with_setup.wire_dependencies(fake_dependent_with_setup) == 16

