# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import pytest
from skid.interface_recovery.doxygen import find_structs


################## TEST FIND FILEOP STRUCTS ##################

def test_find_fileop_stucts(xml_files):
    expected = (
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "fop_ioctl",
            "struct_line_number": 234,
            "refid": "example__driver_8c_1a243d17718e8710d65139b4ac93320c5a",
            "struct_name": "wdt_fops",
        },
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "compat_ptr_ioctl",
            "struct_line_number": 234,
            "refid": "",
            "struct_name": "wdt_fops",
        },
    )
    assert find_structs.find_fileop_structs(xml_files) == expected


def test_find_fileop_stucts_empty():
    with pytest.raises(AssertionError):
        assert find_structs.find_fileop_structs([]) == []


################## TEST FIND FILEOP STRUCTS IN FILE ##################

#TODO

################## TEST IS MEMBERDEF IN FILEOPS STRUCT ##################

#TODO

################## TEST PARSE IOCTL FILEOPS ##################

#TODO

################## TEST PARSE MEMBERDEF ##################

#TODO

################## TEST STRINGIFY CHILDREN ##################

#TODO

################## TEST GET MEMBERDEF LOCATIONS ##################

#TODO

################## TEST PARSE REFID ##################

#TODO

################## TEST PARSE FUNCTION NAMES ##################

#TODO

################## TEST CONVERT LINE TO DICT ##################

#TODO

################## TEST LOG RESULTS ##################

#TODO

