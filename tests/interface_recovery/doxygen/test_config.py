import pytest

from skid.interface_recovery.doxygen import config

def test_outputdir():
    assert isinstance(config.OUTPUT_DIRECTORY, str)

def test_logwarn_file():
    assert isinstance(config.WARN_LOGFILE, str)

