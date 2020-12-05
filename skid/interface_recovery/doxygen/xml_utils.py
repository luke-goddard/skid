"""
Used to parse the XML file produced by doxygen

Author: Luke Goddard
Date: 2020
"""

import os

from io import BytesIO
from logging import getLogger
from multiprocessing import Pool
from typing import Tuple

from lxml import etree  # type: ignore
from alive_progress import alive_bar # type: ignore

from skid.interface_recovery import doxygen
from skid.utils import utils

logger = getLogger(__name__)


class DoxygenMalformedXML(etree.LxmlError):
    """ Doxygen does not always generate XML files matching it's schema """


##################### OPENING XML FILES #####################


def get_root(xml_loc: str):
    """
    Get's the root node of the XML
    Raises: DoxygenMalformedXML: If the XML could not be parsed
    """
    with open(xml_loc, "rb") as xml_f:
        return etree.parse(BytesIO(xml_f.read()))


##################### SHCMEA #####################


def validate_schema(xml_loc: str, schema: etree.XMLSchema):
    """
    Given an xmlfile and a schema. This function returns True
    if the xml file matches the schema
    Raises: DoxygenMalformedXML: If the schema is malformed
    """
    assert os.path.exists(xml_loc)

    with open(xml_loc, "rb") as xml_f:
        xml_bytes = BytesIO(xml_f.read())

    try:
        xml = etree.parse(xml_bytes)
    except etree.XMLSyntaxError as e:
        logger.error(e)
        logger.warning(f"Failed to parse: {xml_loc}")
        logger.warning("Skipping this XML file")
        raise DoxygenMalformedXML(xml_loc) from e

    logger.debug(f"Validating {xml_loc}")

    if schema and not schema.validate(xml):  # type: ignore
        logger.warning(f"Validating schema failed for: {xml_loc}")
        logger.warning(schema.error_log)  # type: ignore
        logger.warning("Skipping this XML file")
        return False

    return True


def get_schema(xml_loc: str):
    """ Loads the schema produced by doxygen from disk """
    assert os.path.exists(xml_loc)
    try:
        schema_root = etree.parse(xml_loc)
    except (etree.XMLSchemaError, etree.XMLSyntaxError) as e:
        logger.warning("Doxygen failed to make an XML schema :(")
        logger.warning("Do you have space left on your device?")
        raise DoxygenMalformedXML("Schema Error") from e
    return etree.XMLSchema(schema_root)


##################### XML FILTER BY ATTRIBUTE #####################


def filter_xml_list_by_header(xml_files: Tuple[str, ...], header: str) -> Tuple[str, ...]:
    """
    Given a list of xml_file locations this function will return a new tuple
    of xml_file locations that all include the header file `header`
    """
    keep_files = list()

    title = utils.format_alive_bar_title(
        f"Finding source files that include '{header}'"
    )
    with alive_bar(len(xml_files), title=title) as bar:
        with Pool(processes=os.cpu_count()) as pool:
            for res, xml_file in pool.imap_unordered(
                xml_file_has_header, [(xml_file, header) for xml_file in xml_files]
            ):
                bar()
                if res:
                    keep_files.append(xml_file)
    return tuple(keep_files)

def xml_file_has_header(args: Tuple[str, str]) -> Tuple[bool, str]:
    assert len(args) == 2
    xml_file, header = args
    try:
        root = doxygen.xml_utils.get_root(xml_file)
    except etree.LxmlError as e:
        logger.error(e)
        return (False, xml_file)

    for element in root.iter("codeline"):
        for highlight in element.iter('highlight'):
            txt = highlight.text
            if not (txt is not None and "include" in txt and "#" in txt):
                continue
            
            if highlight.attrib["class"] != "preprocessor":
                continue

            if header in doxygen.find_structs.stringify_children(highlight):
                logger.debug(f"The following file include {header}: {xml_file}")

            return (True, xml_file)

    return (False, xml_file)
