# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import pytest
from lxml import etree
from skid.interface_recovery.doxygen import find_structs


@pytest.fixture
def memberdef_element():
    struct_element = b"""<?xml version='1.0' encoding='UTF-8' standalone='no'?>
    <doxygen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="compound.xsd" version="1.8.20" xml:lang="en-US">
      <compounddef id="example__driver_8c" kind="file" language="C++">
        <compoundname>example_driver.c</compoundname>
          <sectiondef kind="var">
          <memberdef kind="variable" id="example__driver_8c_1af86896cad0da8791f61f01fdd0fc5205" prot="public" static="yes" mutable="no">
            <type>const struct file_operations</type>
            <definition>const struct file_operations wdt_fops</definition>
            <argsstring></argsstring>
            <name>wdt_fops</name>
            <initializer>= {
            .owner		=	THIS_MODULE,
            .llseek		=	no_llseek,
            .write		=	<ref refid="example__driver_8c_1a82ddd0af9227ef2d8eeb5b4db05feeef" kindref="member">fop_write</ref>,
            .open		=	<ref refid="example__driver_8c_1a0dc447c4c34dceb9ff45f072ba0febe1" kindref="member">fop_open</ref>,
            .release	=	<ref refid="example__driver_8c_1ad1a4c53e7240d7dfe8efa5066a834289" kindref="member">fop_close</ref>,
            .unlocked_ioctl	=	<ref refid="example__driver_8c_1a243d17718e8710d65139b4ac93320c5a" kindref="member">fop_ioctl</ref>,
            .compat_ioctl	= 	compat_ptr_ioctl,
    }</initializer>
            <briefdescription>
            </briefdescription>
            <detaileddescription>
            </detaileddescription>
            <inbodydescription>
            </inbodydescription>
            <location file="tests/resources/example_driver.c" line="234" column="13" bodyfile="tests/resources/example_driver.c" bodystart="290" bodyend="-1"/>
          </memberdef>
          </sectiondef>
      </compounddef>
    </doxygen>
    """
    root = etree.fromstring(struct_element)  # type: ignore
    for tag in root.iter("memberdef"):
        return tag


################## TEST FIND FILEOP STRUCTS ##################


def test_find_fileop_stucts(xml_files):
    expected = (
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "fop_ioctl",
            "struct_line_number": 234,
            "refid": "example__driver_8c_1a243d17718e8710d65139b4ac93320c5a",
            "struct_name": "wdt_fops",
            "fop_type": "unlocked_ioctl",
        },
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "compat_ptr_ioctl",
            "struct_line_number": 234,
            "refid": "",
            "struct_name": "wdt_fops",
            "fop_type": "compat_ioctl",
        },
    )
    assert find_structs.find_fileop_structs(xml_files) == expected


def test_find_fileop_stucts_multi(xml_files):
    xml_files = list(xml_files) + list(xml_files)
    expected = (
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "fop_ioctl",
            "struct_line_number": 234,
            "refid": "example__driver_8c_1a243d17718e8710d65139b4ac93320c5a",
            "struct_name": "wdt_fops",
            "fop_type": "unlocked_ioctl",
        },
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "compat_ptr_ioctl",
            "struct_line_number": 234,
            "refid": "",
            "struct_name": "wdt_fops",
            "fop_type": "compat_ioctl",
        },
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "fop_ioctl",
            "struct_line_number": 234,
            "refid": "example__driver_8c_1a243d17718e8710d65139b4ac93320c5a",
            "struct_name": "wdt_fops",
            "fop_type": "unlocked_ioctl",
        },
        {
            "file_path": "tests/resources/example_driver.c",
            "function": "compat_ptr_ioctl",
            "struct_line_number": 234,
            "refid": "",
            "struct_name": "wdt_fops",
            "fop_type": "compat_ioctl",
        },
    )
    assert find_structs.find_fileop_structs(xml_files) == expected


def test_find_fileop_stucts_empty():
    with pytest.raises(AssertionError):
        assert find_structs.find_fileop_structs([]) == []


################## TEST FIND FILEOP STRUCTS IN FILE ##################


def test_find_fileop_stucts_in_file(xml_files):

    xml_file = xml_files[0]
    expected = [
        {
            "function": "fop_ioctl",
            "refid": "example__driver_8c_1a243d17718e8710d65139b4ac93320c5a",
            "struct_name": "wdt_fops",
            "struct_line_number": 234,
            "file_path": "tests/resources/example_driver.c",
            "fop_type": "unlocked_ioctl",
        },
        {
            "function": "compat_ptr_ioctl",
            "refid": "",
            "struct_name": "wdt_fops",
            "struct_line_number": 234,
            "file_path": "tests/resources/example_driver.c",
            "fop_type": "compat_ioctl",
        },
    ]
    res = find_structs.find_fileop_structs_in_file(xml_file)
    assert res == expected


################## TEST IS MEMBERDEF IN FILEOPS STRUCT ##################


def test_is_memberdef_is_fileops_struct(memberdef_element):
    assert find_structs.is_memberdef_a_file_ops_struct(memberdef_element)


def test_is_memberdef_is_fileops_struct_bad_kind(memberdef_element):
    memberdef_element.attrib["kind"] = "a"
    assert not find_structs.is_memberdef_a_file_ops_struct(memberdef_element)


def test_is_memberdef_is_fileops_struct_bad_type_none(memberdef_element):
    for node in memberdef_element.iter("type"):  # type: ignore
        node.text = None
    assert not find_structs.is_memberdef_a_file_ops_struct(memberdef_element)


def test_is_memberdef_is_fileops_struct_bad_type_upper(memberdef_element):
    for node in memberdef_element.iter("type"):  # type: ignore
        node.text = "FILE_OPERATIONS"
    assert not find_structs.is_memberdef_a_file_ops_struct(memberdef_element)


def test_is_memberdef_is_fileops_struct_bad_tag_no_type(memberdef_element):
    first = True
    for child in memberdef_element.iterchildren():  # type: ignore
        if first:
            child.tag = "initializer"
            first = False
        else:
            child.tag = "a"
    assert not find_structs.is_memberdef_a_file_ops_struct(memberdef_element)


def test_is_memberdef_is_fileops_struct_bad_tag_no_initializer(memberdef_element):
    first = True
    for child in memberdef_element.iterchildren():  # type: ignore
        if first:
            child.tag = "type"
            first = False
        else:
            child.tag = "a"
    assert not find_structs.is_memberdef_a_file_ops_struct(memberdef_element)


def test_is_memberdef_is_fileops_struct_none():
    with pytest.raises(AssertionError):
        find_structs.is_memberdef_a_file_ops_struct(None)


################## TEST PARSE IOCTL FILEOPS ##################


def test_parse_ioctl_file_ops(memberdef_element):
    expected = [
        {
            "function": "fop_ioctl",
            "refid": "example__driver_8c_1a243d17718e8710d65139b4ac93320c5a",
            "struct_name": "wdt_fops",
            "struct_line_number": 234,
            "file_path": "tests/resources/example_driver.c",
            "fop_type": "unlocked_ioctl",
        },
        {
            "function": "compat_ptr_ioctl",
            "refid": "",
            "struct_name": "wdt_fops",
            "struct_line_number": 234,
            "file_path": "tests/resources/example_driver.c",
            "fop_type": "compat_ioctl",
        },
    ]
    assert find_structs.parse_ioctl_file_operations(memberdef_element) == expected


################## TEST PARSE MEMBERDEF ##################


def test_parse_member_definitions_no_strip_valid(memberdef_element):
    expected = """= {
            .owner              =       THIS_MODULE,
            .llseek             =       no_llseek,
            .write              =       <ref xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" refid="example__driver_8c_1a82ddd0af9227ef2d8eeb5b4db05feeef" kindref="member">fop_write</ref>,
            .open               =       <ref xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" refid="example__driver_8c_1a0dc447c4c34dceb9ff45f072ba0febe1" kindref="member">fop_open</ref>,
            .release    =       <ref xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" refid="example__driver_8c_1ad1a4c53e7240d7dfe8efa5066a834289" kindref="member">fop_close</ref>,
            .unlocked_ioctl     =       <ref xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" refid="example__driver_8c_1a243d17718e8710d65139b4ac93320c5a" kindref="member">fop_ioctl</ref>,
            .compat_ioctl       =       compat_ptr_ioctl,
    }"""
    assert (
        find_structs.parse_member_definitions(memberdef_element).split()
        == expected.split()
    )


def test_parse_member_definitions_strip_valid(memberdef_element):
    expected = """= {
            .owner              =       THIS_MODULE,
            .llseek             =       no_llseek,
            .write              =       fop_write,
            .open               =       fop_open,
            .release    =       fop_close,
            .unlocked_ioctl     =       fop_ioctl,
            .compat_ioctl       =       compat_ptr_ioctl,
    }"""
    assert (
        find_structs.parse_member_definitions(memberdef_element, strip_xml=True).split()
        == expected.split()
    )


def test_parse_member_definitions_strip_none():
    with pytest.raises(AssertionError):
        find_structs.parse_member_definitions(None)


################## TEST STRINGIFY CHILDREN ##################


def test_stringify_children(memberdef_element):
    expected = """<type xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">const struct file_operations</type>
            <definition xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">const struct file_operations wdt_fops</definition>
            <argsstring xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
            <name xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">wdt_fops</name>
            <initializer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">= {
            .owner              =       THIS_MODULE,
            .llseek             =       no_llseek,
            .write              =       <ref refid="example__driver_8c_1a82ddd0af9227ef2d8eeb5b4db05feeef" kindref="member">fop_write</ref>,
            .open               =       <ref refid="example__driver_8c_1a0dc447c4c34dceb9ff45f072ba0febe1" kindref="member">fop_open</ref>,
            .release    =       <ref refid="example__driver_8c_1ad1a4c53e7240d7dfe8efa5066a834289" kindref="member">fop_close</ref>,
            .unlocked_ioctl     =       <ref refid="example__driver_8c_1a243d17718e8710d65139b4ac93320c5a" kindref="member">fop_ioctl</ref>,
            .compat_ioctl       =       compat_ptr_ioctl,
    }</initializer>
            <briefdescription xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            </briefdescription>
            <detaileddescription xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            </detaileddescription>
            <inbodydescription xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            </inbodydescription>
            <location xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" file="tests/resources/example_driver.c" line="234" column="13" bodyfile="tests/resources/example_driver.c" bodystart="290" bodyend="-1"/>
    """
    assert (
        find_structs.stringify_children(memberdef_element).split() == expected.split()
    )


################## TEST GET MEMBERDEF LOCATIONS ##################


def test_get_memberdef_location(memberdef_element):
    floc, linenum = find_structs.get_memberdef_location(memberdef_element)
    assert floc == "tests/resources/example_driver.c"
    assert linenum == 234


################## TEST PARSE REFID ##################


def test_parse_refid_valid():
    line = '.unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,'
    assert (
        find_structs.parse_ref_id(line)
        == "at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"
    )


def test_parse_refid_valid_no_kind_ref():
    line = '.unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"> at91_wdt_ioctl</ref>,'
    assert (
        find_structs.parse_ref_id(line)
        == "at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"
    )


def test_parse_refid_valid_close_function():
    line = '.refid= <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"> at91_wdt_ioctl</ref>,'
    assert (
        find_structs.parse_ref_id(line)
        == "at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"
    )


def test_parse_refid_valid_close_function_double():
    line = '.refid= <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"> refid</ref>,'
    assert (
        find_structs.parse_ref_id(line)
        == "at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c"
    )


def test_parse_refid_none():
    with pytest.raises(AssertionError):
        find_structs.parse_ref_id(None)


def test_parse_refid_empty():
    line = '.refid= <ref xmlns:xsi="" refid</ref>,'
    assert find_structs.parse_ref_id(line) == ""


def test_parse_refid_empty_line():
    line = ""
    assert find_structs.parse_ref_id(line) == ""


def test_parse_refid_non_str():
    with pytest.raises(AssertionError):
        find_structs.parse_ref_id(1)


################## TEST PARSE FUNCTION NAMES ##################


def test_parse_function_name_valid():
    line = '.unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,'
    assert find_structs.parse_function_name(line) == "at91_wdt_ioctl"


def test_parse_function_name_none():
    with pytest.raises(AssertionError):
        find_structs.parse_function_name(None)


def test_parse_function_name_empty():
    line = '.unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member"></ref>'
    assert find_structs.parse_function_name(line) == ""


def test_parse_function_name_empty_line():
    line = ""
    assert find_structs.parse_function_name(line) == ""


def test_parse_function_name_non_str():
    with pytest.raises(AssertionError):
        find_structs.parse_function_name(1)


################## TEST PARSE FUNCTION OPERATION ##################


def test_parse_function_operation_valid():
    line = '.unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,'
    assert find_structs.parse_fop_type(line) == "unlocked_ioctl"


def test_parse_function_operation_spaces():
    line = '     .unlocked_ioctl     = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,'
    assert find_structs.parse_fop_type(line) == "unlocked_ioctl"


def test_parse_function_operation_too_close():
    line = '.unlocked_ioctl= <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,'
    assert find_structs.parse_fop_type(line) == "unlocked_ioctl"


def test_parse_function_operation_none():
    with pytest.raises(AssertionError):
        find_structs.parse_fop_type(None)


def test_parse_function_operation_empty():
    line = '= <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member"></ref>'
    assert find_structs.parse_fop_type(line) == ""


def test_parse_function_operation_empty_line():
    line = ""
    assert find_structs.parse_fop_type(line) == ""


def test_parse_function_operation_non_str():
    with pytest.raises(AssertionError):
        find_structs.parse_fop_type(1)


################## TEST CONVERT LINE TO DICT ##################


def test_convert_line_to_dictionary():
    line = '.unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,'
    expected = {
        "function": "at91_wdt_ioctl",
        "refid": "at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c",
        "struct_name": "wdt_fops",
        "struct_line_number": 1,
        "file_path": "test",
        "fop_type": "unlocked_ioctl",
    }
    res = find_structs.convert_line_to_dict(line, "wdt_fops", "test", 1)
    assert res == expected

def test_convert_line_to_dictionary_no_refid():
    line = '.unlocked_ioctl = at91_wdt_ioctl</ref>,'
    expected = {
        "function": "at91_wdt_ioctl",
        "refid": "",
        "struct_name": "wdt_fops",
        "struct_line_number": 1,
        "file_path": "test",
        "fop_type": "unlocked_ioctl",
    }
    res = find_structs.convert_line_to_dict(line, "wdt_fops", "test", 1)
    assert res == expected

