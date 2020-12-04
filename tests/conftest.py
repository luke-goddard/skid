# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from tempfile import TemporaryDirectory, NamedTemporaryFile

import pytest

@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as tempd:
        yield tempd

@pytest.fixture
def temp_file():
    with NamedTemporaryFile() as tempf:
        yield tempf.name
