# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

from skid.interface_recovery import check_install


# Not really much we can test here because it's environment dependent

def test_log_environment():
    assert check_install.log_environment_config() is None

def test_check_dep():
    assert isinstance(check_install.check_dependencies(), bool)

def test_check_doxygen():
    assert isinstance(check_install.check_doxygen(), bool)

def test_check_clang():
    assert isinstance(check_install.check_clang(), bool)

