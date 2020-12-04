# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import logging
import os
import shutil
from unittest.mock import patch
from tempfile import TemporaryDirectory, NamedTemporaryFile

import pytest
from lxml import etree
from skid.interface_recovery.doxygen import config, doxygen

TEST_RESOURCES = "tests/resources/"
VALID_SCHEMA_LOCATION = os.path.join(TEST_RESOURCES, "example_schema.xsd")
TEST_XML_FILES = ('tests/resources/example_c_file.xml',)


@pytest.fixture
def change_output_dir():
    try:
        before = config.OUTPUT_DIRECTORY
        with TemporaryDirectory() as tempd:
            config.OUTPUT_DIRECTORY = tempd
            yield config.OUTPUT_DIRECTORY
    finally:
        config.OUTPUT_DIRECTORY = before

@pytest.fixture
def schema():
    return doxygen.get_schema()

@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as tempd:
        yield tempd

@pytest.fixture
def temp_file():
    with NamedTemporaryFile() as tempf:
        yield tempf.name

################## TEST GLOBALS ##################


def test_xml_location():
    assert isinstance(doxygen.XML_LOCATION, str)


def test_schema_location():
    assert isinstance(doxygen.SCHEMA_LOCATION, str)


def test_doxy_conf_location():
    assert isinstance(doxygen.DOXYCONF_LOCATION, str)


def test_has_logger():
    assert isinstance(doxygen.logger, logging.Logger)


def test_doxygen_exception():
    assert issubclass(doxygen.DoxygenException, Exception)


################## TEST CONFIGURE ##################


def test_configure_fake_fuzzing_location():
    f_source = "asfdasf"
    u_config = ""
    assert not doxygen.configure(f_source, u_config)


def test_configure_real_fuzzing_location():
    f_source = "."
    u_config = ""

    try:
        os.remove(doxygen.DOXYCONF_LOCATION)
    except OSError:
        pass

    assert not doxygen.configure(f_source, u_config)

    try:
        os.remove(u_config)
    except OSError:
        pass


def test_real_configure(temp_file):
    f_source = "."
    u_config = None
    assert doxygen.configure(f_source, u_config, conf_loc=temp_file)
    assert os.path.exists(temp_file)


################## TEST OVERWRITE ##################


@patch(
    "skid.interface_recovery.doxygen.doxygen.ask_for_overwrite",
    {"method.return_value": "y"},
)
def test_overwrite_fake_yes(change_output_dir):
    assert doxygen.overwrite_prior_doxygen()


@patch(
    "skid.interface_recovery.doxygen.doxygen.ask_for_overwrite",
    {"method.return_value": "n"},
)
def test_overwrite_fake_no(change_output_dir):
    assert doxygen.overwrite_prior_doxygen()


@patch(
    "skid.interface_recovery.doxygen.doxygen.ask_for_overwrite",
    {"method.return_value": "y"},
)
def test_overwrite_yes(change_output_dir):
    try:
        os.mkdir(change_output_dir)
        assert doxygen.overwrite_prior_doxygen()
    except OSError:
        pass  # test failed
    finally:
        if os.path.exists(change_output_dir):
            shutil.rmtree(change_output_dir)


@patch(
    "skid.interface_recovery.doxygen.doxygen.ask_for_overwrite",
    {"method.return_value": "n"},
)
def test_overwrite_no(change_output_dir):
    try:
        os.mkdir(change_output_dir)
        assert doxygen.overwrite_prior_doxygen()
    except OSError:
        # Test failed
        return
    finally:
        if os.path.exists(change_output_dir):
            shutil.rmtree(change_output_dir)


################## TEST GET SCHEMA ##################


def copy_real_schema(real_schema_location, fake):
    shutil.copy(real_schema_location, fake)
    assert os.path.exists(fake)


def test_get_schema_does_not_exist():
    with pytest.raises(AssertionError):
        doxygen.get_schema("/t/s/a/d/f/")


def test_get_valid_schema():
    schema = doxygen.get_schema(schema=VALID_SCHEMA_LOCATION)
    assert isinstance(schema, etree.XMLSchema)


def test_get_missing_schema():
    with pytest.raises(AssertionError):
        doxygen.get_schema(schema="d/af/a/dsf/a")


def test_get_invalid_schema():
    try:
        schema_loc = "/tmp/del.xsd"
        copy_real_schema(VALID_SCHEMA_LOCATION, schema_loc)
        with open(schema_loc, "w+") as f:
            f.write("BAD")

        with pytest.raises(etree.LxmlError):
            doxygen.get_schema(schema=schema_loc)
    finally:
        if os.path.exists(schema_loc):
            os.remove(schema_loc)


################## TEST GET XML FILES ##################

def test_get_all_xml_files_invalid_location():
    with pytest.raises(AssertionError):
        doxygen.get_all_xml_files(xml_dir="/asdf/as/fda/sdf")

def test_get_all_xml_files_valid_location():
    files = doxygen.get_all_xml_files(xml_dir=TEST_RESOURCES)
    assert files == TEST_XML_FILES


################## TEST FILTER XML FILES ##################


def test_filter_bad_schema_no_files(schema):
    doxygen.filter_xml_files_bad_schema([], schema)

def test_filter_bad_schema_no_schema_is_none():
    with pytest.raises(AssertionError):
        doxygen.filter_xml_files_bad_schema([], None)

def test_filter_bad_schema_valid(schema):
    good = doxygen.filter_xml_files_bad_schema(TEST_XML_FILES, schema)
    assert set(good) == set(TEST_XML_FILES)

def test_filter_bad_schema_non_existant_file(schema):
    with pytest.raises(AssertionError):
        doxygen.filter_xml_files_bad_schema(list(TEST_XML_FILES) + ["fake"], schema)


################## TEST FIND FILE OP STRUCTS ##################

################## TEST FIND DEVICE NAMES ##################

