# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import lxml
import pytest
from skid.interface_recovery.doxygen import xml_utils
from tests.conftest import VALID_SCHEMA_LOCATION

###################### TEST GET ROOT ######################


def test_get_root_fake():
    with pytest.raises(AssertionError):
        xml_utils.get_root("/asdf/asdf/asdf/as/dfa/sf/ads")


def test_get_root_none():
    with pytest.raises(AssertionError):
        xml_utils.get_root(None)


def test_get_root_real(xml_files):
    assert xml_utils.get_root(xml_files[0]), lxml.etree.ElementTree


###################### TEST VALIDATE SCHEMA ######################


def test_validate_schema(xml_files, xml_schema):
    assert xml_utils.validate_schema(xml_files[0], xml_schema)


def test_validate_schema_is_none(xml_files):
    with pytest.raises(AssertionError):
        xml_utils.validate_schema(xml_files[0], None)


def test_validate_schema_does_not_exist(xml_schema):
    with pytest.raises(AssertionError):
        xml_utils.validate_schema("/asd/fa/sdfa/sdf/as/df", xml_schema)


###################### TEST GET SCHEMA ######################


def test_get_schema():
    assert xml_utils.get_schema(VALID_SCHEMA_LOCATION)


def test_get_schema_none():
    with pytest.raises(AssertionError):
        xml_utils.get_schema(None)


def test_get_schema_fake_location():
    with pytest.raises(AssertionError):
        xml_utils.get_schema("/asdf/as/dfa/sdf/asdf")


###################### TEST FILTER BY HEADER ######################


def test_filter_xml_list_by_header(xml_files):
    expected = ["tests/resources/example_c_file.xml"]
    assert xml_utils.filter_xml_list_by_header(xml_files, "fs.h") == tuple(expected)


def test_filter_xml_list_by_header_none(xml_files):
    assert xml_utils.filter_xml_list_by_header(xml_files, "fake_header.h") == tuple()


def test_filter_xml_list_by_header_missing_file(xml_files):
    xml_files = list(xml_files)
    xml_files.append("/asd/as/df/asdf/a")
    with pytest.raises(AssertionError):
        xml_utils.filter_xml_list_by_header(xml_files, "fs.h")


def test_filter_xml_list_by_header_no_files():
    assert xml_utils.filter_xml_list_by_header([], "fs.h") == tuple()


###################### TEST XML FILE HAS HEADER ######################


def test_filter_xml_file_by_header(xml_files):
    assert xml_utils.xml_file_has_header((xml_files[0], "fs.h")) == (True, xml_files[0])


def test_filter_xml_file_by_header_none(xml_files):
    assert xml_utils.xml_file_has_header((xml_files[0], "fake_header.h")) == (
        False,
        xml_files[0],
    )
