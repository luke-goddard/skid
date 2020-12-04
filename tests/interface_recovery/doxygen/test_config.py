# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import json
import logging
import os

from tempfile import NamedTemporaryFile

import pytest

from skid.interface_recovery.doxygen import config


@pytest.fixture
def good_config():
    data = {"TAB_SIZE": 69}
    with NamedTemporaryFile() as tempf:
        with open(tempf.name, "w") as f:
            json.dump(data, f, indent=4)
        yield tempf.name


@pytest.fixture
def bad_config():
    with NamedTemporaryFile() as tempf:
        with open(tempf.name, "w") as f:
            f.write("Hello")
        yield tempf.name


#################### GLOBALS ####################


def test_outputdir():
    assert isinstance(config.OUTPUT_DIRECTORY, str)


def test_logwarn_file():
    assert isinstance(config.WARN_LOGFILE, str)


def test_logger():
    assert isinstance(config.logger, logging.Logger)


#################### GET CONFIG ####################


def test_get_config_bad_source():
    with pytest.raises(AssertionError):
        config.get_config(1, "s")


def test_get_config_bad_user_config():
    with pytest.raises(AssertionError):
        config.get_config("s", 1)


def test_get_config_fake_source_path():
    with pytest.raises(FileNotFoundError):
        config.get_config("/s/as/df/as/df", "/")


def test_get_config_fake_config_path():
    with pytest.raises(FileNotFoundError):
        config.get_config("/", "/s/as/df/as/df")


def test_get_config_real(good_config):
    dconfig = config.get_config(".", good_config)
    assert isinstance(dconfig, dict)
    assert "INPUT" in dconfig
    assert dconfig["INPUT"] == "."
    assert dconfig["TAB_SIZE"] == 69


def test_get_config_bad(bad_config):
    with pytest.raises(json.JSONDecodeError):
        config.get_config(".", bad_config)


#################### GET CONFIG ####################


def test_generate_default_config():
    conf = config.generate_default_config("")
    assert isinstance(conf, dict)
    assert len(conf) > 10


#################### WRITE CONFIG ####################


def test_write_config():
    dconfig = {"test": 1}
    wloc = "/tmp/asdfoapsdofasdf"
    config.write_configuration(dconfig, wloc)
    assert os.path.exists(wloc)

    with open(wloc, "r") as f:
        data = f.read()
        assert data == "TEST = 1\n"

    os.remove(wloc)


def test_write_config_non_dict():
    with pytest.raises(AssertionError):
        config.write_configuration("a", "/aa")


#################### CONVERT CONFIE ####################


def test_convert_conf():
    dconfig = {"test": 1}
    expected = ("TEST = 1\n",)
    assert config.convert_conf(dconfig) == expected


def test_convert_config_non_dict():
    with pytest.raises(AssertionError):
        config.convert_conf(1)
