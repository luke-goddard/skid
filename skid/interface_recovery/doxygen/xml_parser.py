"""
Used to parse the XML file produced by doxygen 

Author: Luke Goddard
Date: 2020
"""

import os

from io import BytesIO
from logging import getLogger

from lxml import etree

logger = getLogger(__name__)

class DoxygenMalformedXML(Exception):
    """ Doxygen does not always generate XML files matching it's schema """

def get_root(xml_loc: str):
    """
    Get's the root node of the XML
    Raises: DoxygenMalformedXML: If the XML could not be parsed
    """
    with open(xml_loc, 'rb') as xml_f:
        return etree.parse(BytesIO(xml_f.read()))

def validate_schema(xml_loc: str, schema: etree.XMLSchema):
    assert os.path.exists(xml_loc)

    with open(xml_loc, 'rb') as xml_f:
        xml_bytes = BytesIO(xml_f.read())

    try:
        xml = etree.parse(xml_bytes)
    except etree.XMLSyntaxError as e:
        logger.error(e)
        logger.warning(f"Failed to parse: {xml_loc}")
        logger.warning("Skipping this XML file")
        raise DoxygenMalformedXML(xml_loc)

    logger.debug(f"Validating {xml_loc}")

    if schema and not schema.validate(xml):
        logger.warning(f"Validating schema failed for: {xml_loc}")
        logger.warning(schema.error_log)
        logger.warning("Skipping this XML file")
        return False


    return True

def get_schema(xml_loc: str):
    assert os.path.exists(xml_loc)
    try:
        schema_root = etree.parse(xml_loc)
    except (etree.XMLSchemaError, etree.XMLSyntaxError) as e:
        if "Document is empty" in e.msg:
            logger.warning("Doxygen failed to make an XML schema :(")
            logger.warning("Do you have space left on your device?")
        raise DoxygenMalformedXML("Schema Error")
    return etree.XMLSchema(schema_root)


