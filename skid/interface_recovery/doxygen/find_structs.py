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

import os
import json

from logging import getLogger
from typing import Tuple, List, Dict
from multiprocessing import Pool

from lxml import etree
from alive_progress import alive_bar

from skid.utils import utils
from skid.interface_recovery.doxygen import xml_parser

logger = getLogger(__name__)

POSSIBLE_IOCTL_NAMES = {".unlocked_ioctl", ".compat_ioctl"}


def find_fileop_structs(xml_files: Tuple[str, ...])-> Tuple[Dict[str, str], ...]:
    """
    Itterates through all xml files and returns all file_operations
    structs that contain ioctl
    """
    assert len(xml_files) > 0
    assert isinstance(xml_files[0], str)

    struct_elements = []

    # Multiprocessed loading bar
    with Pool(processes=os.cpu_count()) as pool:

        bar_tit = utils.format_alive_bar_title("Finding file_operations structs")
        with alive_bar(len(xml_files), title=bar_tit) as bar:

            # Run tasks
            for structs in pool.imap_unordered(find_fileop_structs_in_file, xml_files):
                bar()
                struct_elements += structs

        logger.debug(f"Found {len(struct_elements)} ioctl file_operations handler function pointers")

    # Log results
    if len(struct_elements) == 0:
        logger.fatal("No ioctl file_operations structs could be found in the source code")
    else:
        logger.debug(json.dumps(struct_elements, indent=4))

    return tuple(struct_elements)


def find_fileop_structs_in_file(xml_file: str) -> List[etree.XMLSchema]:
    """ Loop's through all member definitions in the XML looking for relevant structs """
    structs = []
    logger.debug(f"Finding structs in {xml_file}")

    # Failed to parse XML
    try:
        root = xml_parser.get_root(xml_file)
    except etree.LxmlError as e:
        logger.error(e)
        return structs

    # Find all member definitions
    for element in root.iter("memberdef"):

        # Check if it's a file_operations struct
        if not is_memberdef_a_file_ops_struct(element):
            continue

        # Get the string representation of the struct
        struct = parse_member_definitions(element)

        for line in struct.splitlines():

            # check to see if struct contains ioctl
            struct_words = set(line.split())
            if len(struct_words - POSSIBLE_IOCTL_NAMES) == len(struct_words):
                continue

            line_number = get_memberdef_location(element)
            logger.debug(f"Found fops struct: {line_number}")

            struct_name = element.find("name").text
            structs.append(convert_line_to_dict(line, struct_name, line_number))

    return structs


def is_memberdef_a_file_ops_struct(element: etree.Element) -> bool:
    """ Determines if the member definition is relevant to us """
    if element.attrib["kind"] != "variable":
        return False

    for node in element.iter("type"):
        if node.text is None or "file_operations" not in node.text:
            return False

    required_tags = {"initializer", "type"}
    actual_tags = {child.tag for child in element.iterchildren()}

    if len(required_tags - actual_tags) > 0:
        return False

    return True


def parse_member_definitions(element: etree.Element, strip_xml=False) -> str:
    """
    Returns the string for the c code,
    this has embbeded XML in it to remove it set strip_xml = True
    Note:
       <initializer>= {
           .open       = <ref refid="dfl-fme-main_8c_1ac26cb73e6fab57e3020f1ac7dc4961a8" kindref="member">fme_open</ref>,
           .unlocked_ioctl = <ref refid="dfl-fme-main_8c_1a1657ada1fdafea4ec33299b88dcdb622" kindref="member">fme_ioctl</ref>,
       }</initializer>
    """
    # Should only be one initializer
    for init in element.iter("initializer"):
        logger.debug(etree.tostring(element).decode('utf-8'))
        if strip_xml:
            return "".join(init.itertext()).strip()
        return stringify_children(init)


def stringify_children(node: etree.Element) -> str:
    """
    The XML contains hard to parse embbeded XML/string for example this function
    just parses all of it as a single string
    """
    text = node.text
    if text is None:
        text = ""
    for child in node:
        text += etree.tostring(child, encoding="unicode")
    return text


def get_memberdef_location(element: etree.Element) -> str:
    """ Finds the source code location and line number for the struct """
    for location in element.iter("location"):
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
        return line.split("refid=\"")[1].split('"')[0]
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
        return line.split("\">")[-1].split("</ref>")[0]
    except IndexError:
        return ""


def convert_line_to_dict(line: str, struct_name: str, line_number:str) -> Dict[str, str]:
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
    return {"function": function, "refid": refid, "struct_name": struct_name, "line_number": line_number}
