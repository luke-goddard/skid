"""
This module gives a high level API for doxygen
Author: Luke Goddard
Date: 2020

Attributes:
    DOXYCONF_LOCATION: (str) Location to write the confiuration file to
    XML_LOCATION: (str) Location of the folder that contains the XML files
    SCHEMA_LOCATION: (str) Location of the XML schema produced by doxygen
"""

import logging
import os
import shutil
import subprocess
import time

from pathlib import Path
from typing import Tuple, Dict, Any

from alive_progress import alive_bar # type: ignore
from lxml import etree
from skid.interface_recovery.doxygen import config as doxyconf
from skid.interface_recovery.doxygen import find_device_name, find_structs, xml_parser
from skid.utils import utils

XML_LOCATION = os.path.join(doxyconf.OUTPUT_DIRECTORY, "xml")
SCHEMA_LOCATION = os.path.join(XML_LOCATION, "compound.xsd")
DOXYCONF_LOCATION = "/tmp/skid-doxyconf"

logger = logging.getLogger(__name__)

################## CUSTOM EXCEPTION ##################


class DoxygenException(Exception):
    """ Base exception for all doxygen related errors """


def configure(fuzz_source_location: str, user_config_location: str, conf_loc=DOXYCONF_LOCATION) -> bool:
    """
    Takes the user defined configuration for doxygen (if avaliable) and then
    merges it with the default configuration
    """
    if not os.path.exists(fuzz_source_location):
        logger.critical(
            f"Source directory does not exist at location: {fuzz_source_location}"
        )
        return False

    try:
        config_dict = doxyconf.get_config(fuzz_source_location, user_config_location)
        return doxyconf.write_configuration(config_dict, conf_loc)
    except (FileNotFoundError, ValueError, OSError) as e:
        logger.critical("Failed to configure doxygen")
        logger.exception(e)
        return False


def run() -> bool:
    """
    Runs doxygen against the source code. If doxygen returns a non zero
    exit code then this function will return False, else it will return True
    """
    assert os.path.exists(DOXYCONF_LOCATION)

    if not overwrite_prior_doxygen():
        logger.info("Using previous doxygen results")
        return True

    logger.debug("Indexing source code with doxygen, this might take a while")

    kwargs = dict() #type: Dict[str, Any]
    if not utils.is_verbose():
        kwargs = {**kwargs, "stdout": subprocess.DEVNULL}

    # Run doxy
    try:
        proc = subprocess.Popen(["doxygen", DOXYCONF_LOCATION], **kwargs)
    except subprocess.SubprocessError:
        logger.critical("Failed to run doxygen")
        return False

    # Show ascii bar
    if not utils.is_verbose():
        print("")
        bar_tit = utils.format_alive_bar_title(
            "Indexing source code, this might take a while"
        )
        with alive_bar(title=bar_tit):
            while proc.poll() is None:
                time.sleep(0.1)

    if proc.returncode != 0:
        logger.critical("Doxygen returned a non zero error code")
        logger.info(f"Try run again with -v enabled or read {doxyconf.WARN_LOGFILE}")
        return False

    logger.debug("Doxygen has finished indexing source code")
    return True


def overwrite_prior_doxygen() -> bool:
    """
    running doxygen is expensive on a large code base so this function give us the option
    of reusing the prior results or to disgard them
    """
    if not os.path.exists(doxyconf.OUTPUT_DIRECTORY):
        return True

    if len(os.listdir(doxyconf.OUTPUT_DIRECTORY)) == 0:
        return True

    logger.critical(f"Previous doxygen results found: {doxyconf.OUTPUT_DIRECTORY}")

    while True:
        answer =ask_for_overwrite()
        if answer in ["", None] or answer[0].lower() == "n":
            return False
        if answer[0].lower() == "y":

            # Delete old results
            try:
                path = Path(doxyconf.OUTPUT_DIRECTORY)
                shutil.rmtree(path)
                path.mkdir(parents=True)
            except OSError as e:
                logger.warning(f"Failed to delete old results at: {path}")
                logger.exception(e)
                raise e

            return True

def ask_for_overwrite() -> str:
    """ Just seperating this so I can mock it out of the tests """
    return input("         : Do you want to overwrite it (y/N): ")



def get_schema(schema=SCHEMA_LOCATION) -> etree.XMLSchema:
    """ Loads and returns the schema produced by doxygen """
    assert os.path.exists(schema)
    return xml_parser.get_schema(schema)


def get_all_xml_files(xml_dir=XML_LOCATION) -> Tuple[str, ...]:
    """ Returns a tuple of all XML files produced by doxygen """
    assert os.path.exists(xml_dir)
    return tuple(
        [
            os.path.join(xml_dir, f)
            for f in os.listdir(xml_dir)
            if f.endswith(".xml") and f != "index.xml"
        ]
    )


def filter_xml_files_bad_schema(
    xml_files_locs: Tuple[str, ...], schema: etree.XMLSchema
) -> Tuple[str, ...]:
    """
    Doxygen sometimes produces malformed XML files that don't match their schema
    we can drop these xml_files by checking the schema matches
    """
    assert isinstance(schema, etree.XMLSchema)
    valid_files = []
    bin_tit = utils.format_alive_bar_title("Validating file schemas")
    with alive_bar(len(xml_files_locs), title=bin_tit) as bar:
        for loc in xml_files_locs:
            assert os.path.exists(loc)
            try:
                if xml_parser.validate_schema(loc, schema):
                    valid_files.append(loc)
                else:
                    logger.warning(f"Schema validation for file {loc} failed")
            except xml_parser.DoxygenMalformedXML as e:
                logger.error(e)
            bar()
    return tuple(valid_files)


def find_fileop_structs(xml_files: Tuple[str, ...]):
    """
    Wrapper function to find the file_operations structs
    for ioctl
    """
    return find_structs.find_fileop_structs(xml_files)


def find_all_device_names(xml_files: Tuple[str, ...]):
    """
    Wrapper function to find all device names that is found in the xml files /dev/*
    """
    find_device_name.xml_list_must_include(xml_files, find_device_name.INCLUDE_FILE)
    return ""
    # return find_device_names.findall(xml_files)
