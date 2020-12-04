# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import os
import logging 

from skid.interface_recovery.doxygen import doxygen


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
    if os.path.exists(doxygen.DOXYCONF_LOCATION):
        os.remove(doxygen.DOXYCONF_LOCATION)

    assert not doxygen.configure(f_source, u_config)

    if os.path.exists(doxygen.DOXYCONF_LOCATION):
        os.remove(u_config)

def test_real_configure():
    f_source = "."
    u_config = None
    if os.path.exists(doxygen.DOXYCONF_LOCATION):
        os.remove(doxygen.DOXYCONF_LOCATION)

    assert doxygen.configure(f_source, u_config)
    assert os.path.exists(doxygen.DOXYCONF_LOCATION)

    os.remove(doxygen.DOXYCONF_LOCATION)


################## TEST OVERWRITE ##################


