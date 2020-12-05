# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from tempfile import TemporaryDirectory, NamedTemporaryFile

import os
import pytest


TEST_RESOURCES = "tests/resources/"
VALID_SCHEMA_LOCATION = os.path.join(TEST_RESOURCES, "example_schema.xsd")
TEST_XML_FILES = ("tests/resources/example_c_file.xml",)

@pytest.fixture
def temp_dir():
    with TemporaryDirectory(prefix="/tmp/skid-deleteme") as tempd:
        yield tempd

    assert not os.path.exists(tempd)

@pytest.fixture
def temp_file():
    with NamedTemporaryFile() as tempf:
        yield tempf.name

    assert not os.path.exists(tempf.name)

@pytest.fixture
def xml_files():
    return TEST_XML_FILES
