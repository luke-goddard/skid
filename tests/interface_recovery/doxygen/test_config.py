# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import json
import logging
import os

import pytest

from skid.interface_recovery.doxygen import config


@pytest.fixture
def good_config(temp_file):
    data = {"TAB_SIZE": 69}
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=4)
    yield temp_file


@pytest.fixture
def bad_config(temp_file):
    with open(temp_file, "w") as f:
        f.write("Hello")
    yield temp_file


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
        config.get(1, "s")


def test_get_config_bad_user_config():
    with pytest.raises(AssertionError):
        config.get("s", 1)


def test_get_config_fake_source_path():
    with pytest.raises(FileNotFoundError):
        config.get("/s/as/df/as/df", "/")


def test_get_config_fake_config_path():
    with pytest.raises(FileNotFoundError):
        config.get("/", "/s/as/df/as/df")


def test_get_config_real(good_config):
    dconfig = config.get(".", good_config)
    assert isinstance(dconfig, dict)
    assert "INPUT" in dconfig
    assert dconfig["INPUT"] == "."
    assert dconfig["TAB_SIZE"] == 69


def test_get_config_bad(bad_config):
    with pytest.raises(json.JSONDecodeError):
        config.get(".", bad_config)


#################### GET CONFIG ####################


def test_generate_default_config():
    conf = config.get_default_config("")
    assert isinstance(conf, dict)
    assert len(conf) > 10


#################### WRITE CONFIG ####################


def test_write_config(temp_file):
    dconfig = {"test": 1}
    config.write(dconfig, temp_file)
    assert os.path.exists(temp_file)

    with open(temp_file, "r") as f:
        data = f.read()
        assert data == "TEST = 1\n"


def test_write_config_non_dict():
    with pytest.raises(AssertionError):
        config.write("a", "/aa")


#################### CONVERT CONFIE ####################


def test_convert_conf():
    dconfig = {"test": 1}
    expected = ("TEST = 1\n",)
    assert config.convert_conf(dconfig) == expected


def test_convert_config_non_dict():
    with pytest.raises(AssertionError):
        config.convert_conf(1)
