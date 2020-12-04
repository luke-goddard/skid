# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import pytest

from skid.utils import utils


############# TEST GLOBALS #############

def test_format_ljust():
    assert isinstance(utils.FORMAT_LJUST, int)
    assert utils.FORMAT_LJUST > 10
    assert utils.FORMAT_LJUST < 100

############# TEST IS VERBOSE #############

# Not sure how to test this

def test_verbose():
    assert not utils.is_verbose()

############# TEST FORMAT ALIVE BAR #############

def test_format_alive_bar_non_str():
    with pytest.raises(AssertionError):
        utils.format_alive_bar_title(1)

def test_format_alive_bar():
    sformat = utils.format_alive_bar_title(" ")
    assert isinstance(sformat, str)
    assert len(sformat) > utils.FORMAT_LJUST

