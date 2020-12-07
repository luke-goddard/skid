# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import json
import logging
import os

from unittest import mock

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


#################### GEN DEFAULT CONFIG ####################


def test_generate_default_config():
    conf = config.get_default_config("")
    assert isinstance(conf, dict)
    assert len(conf) > 10


#################### GEN DEFAULT CONFIG ####################

def test_get_user_overide_config_real(good_config):
    data = {"TAB_SIZE": 69}
    assert config.get_users_override_config(good_config) == data

def test_get_user_overide_config_fake():
    with pytest.raises(FileNotFoundError):
        config.get_users_override_config("a/sdf/asdf/a/sdf/asdf")

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


def test_write_dir_does_not_exists():
    fake_dir = "/tmp/asd/fa/df/adsf/asfd"
    fake_write = os.path.join(fake_dir, "config.json")
    assert not os.path.exists(fake_dir)
    dconfig = {"TAB_SIZE": 69}
    try:
        assert config.write(dconfig, fake_write)
        assert os.path.exists(fake_write)
        with open(fake_write, "r") as f:
            data = f.read()
            assert data == "TAB_SIZE = 69\n"
    finally:
        if os.path.exists(fake_dir):
            os.system(f"rm -rf {fake_dir}")

def test_write_dir_does_not_exists_oserror():
    fake_dir = "/tmp/asd/fa/df/adsf/asfd"
    fake_write = os.path.join(fake_dir, "config.json")
    assert not os.path.exists(fake_dir)
    dconfig = {"TAB_SIZE": 69}
    try:
        with mock.patch("skid.interface_recovery.doxygen.config.Path", side_effect=OSError):
            assert not config.write(dconfig, fake_write)
    finally:
        if os.path.exists(fake_dir):
            os.system(f"rm -rf {fake_dir}")

def test_write_oserror(temp_file):
    with mock.patch("builtins.open", side_effect=OSError):
        assert not config.write(dict(), temp_file)

#################### CONVERT CONFIE ####################


def test_convert_conf():
    dconfig = {"test": 1}
    expected = ("TEST = 1\n",)
    assert config.convert_conf(dconfig) == expected


def test_convert_config_non_dict():
    with pytest.raises(AssertionError):
        config.convert_conf(1)
