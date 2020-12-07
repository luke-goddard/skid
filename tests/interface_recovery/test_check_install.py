# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods

import subprocess

from unittest import mock

from skid.interface_recovery import check_install

class Proc:
    def __init__(self, ret, err):
        self.returncode = ret
        self.stderr = err

# Not really much we can test here because it's environment dependent

def test_log_environment():
    assert check_install.log_environment_config() is None

def test_check_dep():
    assert isinstance(check_install.check_dependencies(), bool)

def test_check_doxygen():
    assert isinstance(check_install.check_doxygen(), bool)

def test_check_doxygen_error():
    with mock.patch('subprocess.run', side_effect=subprocess.SubprocessError):
        assert not check_install.check_doxygen()

def test_check_doxygen_bad_ret():
    with mock.patch('subprocess.run', return_value=Proc(-1, "")):
        assert not check_install.check_doxygen()

def test_check_clang():
    assert isinstance(check_install.check_clang(), bool)

def test_check_clang_error():
    with mock.patch('subprocess.run', side_effect=subprocess.SubprocessError):
        assert not check_install.check_clang()

def test_check_clang_bad_ret():
    with mock.patch('subprocess.run', return_value=Proc(-1, "")):
        assert not check_install.check_clang()

def test_check_clang_bad_ver():
    with mock.patch('subprocess.run', return_value=Proc(0, "")):
        assert check_install.check_clang()
