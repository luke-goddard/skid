"""
Used to find structs in XML produced by doxygen

This module will find and parse member definitions in xml and test to see if it's a file_operations struct with ioctl
for example:

<memberdef kind="variable" id="alim1535__wdt_8c_1a0c9322444b2fd836b301f4f17dbc9727" prot="public" static="yes" mutable="no">
        <type>const struct file_operations</type>
        <definition>const struct file_operations ali_fops</definition>
        <argsstring/>
        <name>ali_fops</name>
        <initializer>= {
        .owner          = THIS_MODULE,
        .llseek         = no_llseek,
        .write          = <ref refid="alim1535__wdt_8c_1a9565a8b19f6235a2c7d17a20beba97dc" kindref="member">ali_write</ref>,
        .unlocked_ioctl = <ref refid="alim1535__wdt_8c_1a1838d5548ab68027163a91b8dc87a337" kindref="member">ali_ioctl</ref>,
        .compat_ioctl   = compat_ptr_ioctl,
        .open           = <ref refid="alim1535__wdt_8c_1a6ac9756cd2929187c53508cfd5b5ae60" kindref="member">ali_open</ref>,
        .release        = <ref refid="alim1535__wdt_8c_1a572795dc2ffb18095159cd3e52b57516" kindref="member">ali_release</ref>,
}</initializer>
        <location file="/home/luke/documents/c/linux/drivers/watchdog/alim1535_wdt.c" line="314" column="19" ="-1"/>
      </memberdef>

Note: Some redundant information has been stripped from the above for brevity

Author: Luke Goddard
Date: 2020
"""

import json
import os
from logging import getLogger
from multiprocessing import Pool
from typing import Dict, List, Tuple

from alive_progress import alive_bar  # type: ignore
from lxml import etree
from skid.interface_recovery.doxygen import xml_parser
from skid.utils import utils

logger = getLogger(__name__)

POSSIBLE_IOCTL_NAMES = {".unlocked_ioctl", ".compat_ioctl"}


########## LIST OF XML ##########


def find_fileop_structs(xml_files: Tuple[str, ...]) -> Tuple[Dict[str, str], ...]:
    """
    Itterates through all xml files and returns all file_operations
    structs that contain ioctl
    """
    assert len(xml_files) > 0
    assert isinstance(xml_files[0], str)

    struct_elements = []
    bar_tit = utils.format_alive_bar_title("Finding file_operations structs")

    # Multiprocessed loading bar
    with Pool(processes=os.cpu_count()) as pool:
        with alive_bar(len(xml_files), title=bar_tit) as bar:

            for structs in pool.imap_unordered(
                find_fileop_structs_in_file, xml_files
            ):  # type: List[Dict[str, str]]
                bar()
                struct_elements += structs

        logger.debug(
            f"Found {len(struct_elements)} ioctl file_operations handler function pointers"
        )

    log_results(struct_elements)
    return tuple(struct_elements)  # type: ignore


########## SINGLE XML FILE ##########


def find_fileop_structs_in_file(xml_file: str) -> List[Dict[str, str]]:
    """ Loop's through all member definitions in the XML looking for relevant structs """
    try:
        logger.debug(f"Finding structs in {xml_file}")
        root = xml_parser.get_root(xml_file)
    except etree.LxmlError as e:
        logger.error(e)
        return list()

    return [
        subelement
        for element in root.iter("memberdef")
        if is_memberdef_a_file_ops_struct(element)
        for subelement in parse_ioctl_file_operations(element)
    ]


########## SINGLE XML ELEMENT ##########


def is_memberdef_a_file_ops_struct(element: etree.Element) -> bool:  # type: ignore
    """ Determines if the member definition is relevant to us """
    if element.attrib["kind"] != "variable":  # type: ignore
        return False

    for node in element.iter("type"):  # type: ignore
        if node.text is None or "file_operations" not in node.text:
            return False

    required_tags = {"initializer", "type"}
    actual_tags = {child.tag for child in element.iterchildren()}  # type: ignore

    return not len(required_tags - actual_tags) > 0


########## STRUCTS ##########


def parse_ioctl_file_operations(struct_xml: etree.Element):  # type: ignore
    """
    For each line in the struct, test to see if it's an ioctl
    operation and if it is then return the parsed version
    of that struct as a dictionary. This happends for each line
    that is found to be an ioctl file_operation function

    Param struct_xml:
        This is the current XML element that represents an unknown
        struct

    Return:
        List of dictionaries parsed by the convert_line_to_dict
        function
    """
    ioctl_ops = list()
    for line in parse_member_definitions(struct_xml).splitlines():

        # check to see if struct contains ioctl
        struct_words = set(line.split())
        if len(struct_words - POSSIBLE_IOCTL_NAMES) == len(struct_words):
            continue

        # log findings
        line_number = get_memberdef_location(struct_xml)
        logger.debug(f"Found fops struct: {line_number}")

        struct_name = struct_xml.find("name").text  # type: ignore
        ioctl_ops.append(convert_line_to_dict(line, struct_name, line_number))

    return ioctl_ops


########## PARSING STRUCT ##########


def parse_member_definitions(element: etree.Element, strip_xml=False) -> str:  # type: ignore
    """
    Returns the string for the c code,
    this has embbeded XML in it to remove it set strip_xml = True
    Note:
       <initializer>= {
           .open       = <ref refid="dfl-fme-main_8c_1ac26cb73e6fab57e3020f1ac7dc4961a8" kindref="member">fme_open</ref>,
           .unlocked_ioctl = <ref refid="dfl-fme-main_8c_1a1657ada1fdafea4ec33299b88dcdb622" kindref="member">fme_ioctl</ref>,
       }</initializer>
    """
    text = ""
    for init in element.iter("initializer"):  # type: ignore
        if strip_xml:
            text += "".join(init.itertext()).strip()
        text += stringify_children(init)

    return text


def stringify_children(node: etree.Element) -> str:  # type: ignore
    """
    The XML contains hard to parse embbeded XML/string for example this function
    just parses all of it as a single string
    """
    text = node.text  # type: ignore
    if text is None:
        text = ""
    for child in node:  # type: ignore
        text += etree.tostring(child, encoding="unicode")
    return text


def get_memberdef_location(element: etree.Element) -> str:  # type: ignore
    """ Finds the source code location and line number for the struct """
    for location in element.iter("location"):  # type: ignore
        floc = location.attrib["file"]
        line = location.attrib["line"]
        return f"{floc}:{line}"


def parse_ref_id(line: str) -> str:
    """
    Given a line such as

    .unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,

    This function returns the refid: at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c
    Note: On error "" is returned
    """
    try:
        return line.split('refid="')[1].split('"')[0]
    except IndexError:
        return ""


def parse_function_name(line: str) -> str:
    """
    Given a line such as

    .unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,

    This function retuns the function name: at91_wdt_ioctl
    Note: On error "" is returned
    """
    try:
        return line.split('">')[-1].split("</ref>")[0]
    except IndexError:
        return ""


########## FORMAT AGRIGATED FILE OP INFO ##########


def convert_line_to_dict(
    line: str, struct_name: str, line_number: str
) -> Dict[str, str]:
    """
    Given a line such as

    .unlocked_ioctl = <ref xmlns:xsi="" refid="at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c" kindref="member">at91_wdt_ioctl</ref>,

    This function retuns a dictionary such as:
        {'refid': 'at91rm9200__wdt_8c_1a0f82b8fa55a637eab5b42397bb13ae6c', 'function': 'at91_wdt_ioctl'}
    """
    refid = parse_ref_id(line)
    if refid == "":
        function = max(line.split("=")[1].split(",")[0].split())
    else:
        function = parse_function_name(line)
    return {
        "function": function,
        "refid": refid,
        "struct_name": struct_name,
        "line_number": line_number,
    }


def log_results(struct_elements: List[Dict]):
    """ Log the results found """
    # Log results
    if len(struct_elements) == 0:
        logger.critical("No file_operations structs could be found in the source code")
        return
    logger.debug(json.dumps(struct_elements, indent=4))
