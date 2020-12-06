"""
Used to generate the configuration that doxygen uses. You can find the configuration
documentation at the following locaiton: https://www.doxygen.nl/manual/config.html

Author: Luke Goddard
Date: 2020
"""

import json
import os
from logging import getLogger
from pathlib import Path
from typing import Dict, Tuple

logger = getLogger(__name__)

OUTPUT_DIRECTORY = "/tmp/skid-doxygen"
WARN_LOGFILE = "/tmp/doxygen.log"


def get(source_dir: str, user_config_location: str) -> Dict:
    """
    Get's the default inbuilt doxygen configuration and then if avaliable will load
    a user specified configuration (as json) as then override the default configuration

    ARGS:
        source_dir: Location of the source code that contains the ioctl's
        user_config_location: Location passed from cmdline args that points to a user defined config

    Raises:
        FileNotFoundError: If the user specified config is not found
        JSONDecodeError: If the config is invalid

    Returns:
        The Doxygen configuration as a dictionary
    """
    assert isinstance(source_dir, str)
    assert isinstance(user_config_location, str) or user_config_location is None

    user = dict()
    default = get_default_config(source_dir)

    if not os.path.exists(source_dir):
        raise FileNotFoundError("Fuzzing source code does not exist")

    logger.info(f"Source code location exists: {source_dir}")
    if (
        user_config_location is not None
        and os.path.exists(user_config_location)
        and os.path.isfile(user_config_location)
    ):
        user = get_users_override_config(user_config_location)
        logger.info("Setting doxygen user supplied configurations")
        for key, value in user.items():
            logger.debug(f"{key} -> {value}")
    elif user_config_location is not None:
        raise FileNotFoundError(f"Failed to find the config at {user_config_location}")

    return {**default, **user}


def get_default_config(source_dir: str) -> Dict:
    """
    Generates the default configuration for doxygen
    Args: source_dir: Location of the source code to be indexed
    Returns: Dictionary with the default configuration for doxygen
    """
    return {
        "DOXYFILE_ENCODING": "UTF-8",
        "PROJECT_NAME": f'"{OUTPUT_DIRECTORY}"',
        "OUTPUT_DIRECTORY": '"/tmp/skid-doxygen"',
        "ALLOW_UNICODE_NAMES": "YES",
        "OUTPUT_LANGUAGE": "English",
        "OUTPUT_TEXT_DIRECTION": "None",
        "BRIEF_MEMBER_DESC": "NO",
        "REPEAT_BRIEF": "YES",
        "ALWAYS_DETAILED_SEC": "YES",
        "INLINE_INHERITED_MEMB": "YES",
        "FULL_PATH_NAMES": "YES",
        "SHORT_NAMES": "NO",
        "INHERIT_DOCS": "YES",
        "SEPARATE_MEMBER_PAGES": "NO",
        "TAB_SIZE": "4",
        "OPTIMIZE_OUTPUT_FOR_C": "YES",
        "OPTIMIZE_OUTPUT_JAVA": "NO",
        "OPTIMIZE_FOR_FORTRAN": "NO",
        "OPTIMIZE_OUTPUT_VHDL": "NO",
        "OPTIMIZE_OUTPUT_SLICE": "NO",
        "MARKDOWN_SUPPORT": "YES",
        "TOC_INCLUDE_HEADINGS": "5",
        "AUTOLINK_SUPPORT": "YES",
        "BUILTIN_STL_SUPPORT": "NO",
        "CPP_CLI_SUPPORT": "NO",
        "SIP_SUPPORT": "NO",
        "IDL_PROPERTY_SUPPORT": "YES",
        "DISTRIBUTE_GROUP_DOC": "YES",
        "GROUP_NESTED_COMPOUNDS": "YES",
        "SUBGROUPING": "YES",
        "INLINE_GROUPED_CLASSES": "YES",
        "INLINE_SIMPLE_STRUCTS": "YES",
        "TYPEDEF_HIDES_STRUCT": "NO",
        "LOOKUP_CACHE_SIZE": "0",
        "NUM_PROC_THREADS": "0",
        "DOT_NUM_THREADS": "0",
        "EXTRACT_ALL": "YES",
        "EXTRACT_PRIVATE": "YES",
        "EXTRACT_PRIV_VIRTUAL": "YES",
        "EXTRACT_PACKAGE": "YES",
        "EXTRACT_STATIC": "YES",
        "EXTRACT_LOCAL_CLASSES": "YES",
        "EXTRACT_LOCAL_METHODS": "YES",
        "EXTRACT_ANON_NSPACES": "YES",
        # "RESOLVE_UNNAMED_PARAMS": "YES",
        "HIDE_UNDOC_MEMBERS": "NO",
        "HIDE_UNDOC_CLASSES": "NO",
        "HIDE_FRIEND_COMPOUNDS": "NO",
        "HIDE_IN_BODY_DOCS": "NO",
        "INTERNAL_DOCS": "YES",
        "CASE_SENSE_NAMES": "YES",
        "HIDE_SCOPE_NAMES": "NO",
        "HIDE_COMPOUND_REFERENCE": "NO",
        "SHOW_INCLUDE_FILES": "YES",
        "SHOW_GROUPED_MEMB_INC": "YES",
        "FORCE_LOCAL_INCLUDES": "YES",
        "INLINE_INFO": "YES",
        "SORT_MEMBER_DOCS": "NO",
        "SORT_BRIEF_DOCS": "NO",
        "SORT_MEMBERS_CTORS_1ST": "NO",
        "SORT_GROUP_NAMES": "NO",
        "SORT_BY_SCOPE_NAME": "NO",
        "STRICT_PROTO_MATCHING": "NO",
        "GENERATE_TODOLIST": "YES",
        "GENERATE_TESTLIST": "YES",
        "GENERATE_BUGLIST": "YES",
        "GENERATE_DEPRECATEDLIST": "YES",
        "MAX_INITIALIZER_LINES": "30",
        "SHOW_USED_FILES": "YES",
        "SHOW_FILES": "YES",
        "SHOW_NAMESPACES": "YES",
        "QUIET": "NO",
        "WARNINGS": "YES",
        "WARN_LOGFILE": WARN_LOGFILE,
        "WARN_IF_UNDOCUMENTED": "NO",
        "WARN_IF_DOC_ERROR": "YES",
        "WARN_NO_PARAMDOC": "NO",
        "WARN_AS_ERROR": "NO",
        "WARN_FORMAT": '"$file:$line: $text"',
        "INPUT": source_dir,
        "INPUT_ENCODING": "UTF-8",
        "FILE_PATTERNS": "*.c \\\n\t\t\t*.h",
        "RECURSIVE": "YES",
        "EXCLUDE_SYMLINKS": "NO",
        "EXAMPLE_PATTERNS": "*",
        "EXAMPLE_RECURSIVE": "NO",
        "FILTER_SOURCE_FILES": "NO",
        "SOURCE_BROWSER": "YES",
        "INLINE_SOURCES": "NO",
        "STRIP_CODE_COMMENTS": "NO",
        "REFERENCED_BY_RELATION": "YES",
        "REFERENCES_RELATION": "NO",
        "REFERENCES_LINK_SOURCE": "YES",
        "SOURCE_TOOLTIPS": "YES",
        "USE_HTAGS": "NO",
        "VERBATIM_HEADERS": "YES",
        "ALPHABETICAL_INDEX": "YES",
        "COLS_IN_ALPHA_INDEX": "5",
        "GENERATE_HTML": "NO",
        "HTML_OUTPUT": "html",
        "HTML_FILE_EXTENSION": ".html",
        "HTML_COLORSTYLE_HUE": "220",
        "HTML_COLORSTYLE_SAT": "100",
        "HTML_COLORSTYLE_GAMMA": "80",
        "HTML_TIMESTAMP": "NO",
        "HTML_DYNAMIC_MENUS": "YES",
        "HTML_DYNAMIC_SECTIONS": "NO",
        "HTML_INDEX_NUM_ENTRIES": "100",
        "GENERATE_DOCSET": "NO",
        "DOCSET_FEEDNAME": '"Doxygen generated docs"',
        "DOCSET_BUNDLE_ID": "org.doxygen.Project",
        "DOCSET_PUBLISHER_ID": "org.doxygen.Publisher",
        "DOCSET_PUBLISHER_NAME": "Publisher",
        "GENERATE_HTMLHELP": "NO",
        "GENERATE_CHI": "NO",
        "BINARY_TOC": "NO",
        "TOC_EXPAND": "NO",
        "GENERATE_QHP": "NO",
        "QHP_NAMESPACE": "org.doxygen.Project",
        "QHP_VIRTUAL_FOLDER": "doc",
        "GENERATE_ECLIPSEHELP": "NO",
        "ECLIPSE_DOC_ID": "org.doxygen.Project",
        "DISABLE_INDEX": "NO",
        "GENERATE_TREEVIEW": "YES",
        "ENUM_VALUES_PER_LINE": "4",
        "TREEVIEW_WIDTH": "250",
        "EXT_LINKS_IN_WINDOW": "NO",
        "HTML_FORMULA_FORMAT": "png",
        "FORMULA_FONTSIZE": "10",
        "FORMULA_TRANSPARENT": "YES",
        "USE_MATHJAX": "NO",
        "MATHJAX_FORMAT": "HTML-CSS",
        "MATHJAX_RELPATH": "https://cdn.jsdelivr.net/npm/mathjax@2",
        "SEARCHENGINE": "YES",
        "SERVER_BASED_SEARCH": "NO",
        "EXTERNAL_SEARCH": "NO",
        "SEARCHDATA_FILE": "searchdata.xml",
        "GENERATE_LATEX": "NO",
        "MAKEINDEX_CMD_NAME": "makeindex",
        "LATEX_MAKEINDEX_CMD": "makeindex",
        "COMPACT_LATEX": "NO",
        "PAPER_TYPE": "a4",
        "GENERATE_RTF": "NO",
        "RTF_OUTPUT": "rtf",
        "COMPACT_RTF": "NO",
        "RTF_HYPERLINKS": "NO",
        "GENERATE_MAN": "NO",
        "GENERATE_XML": "YES",
        "XML_OUTPUT": "xml",
        "XML_PROGRAMLISTING": "YES",
        "XML_NS_MEMB_FILE_SCOPE": "YES",
        "ENABLE_PREPROCESSING": "NO",
        "MACRO_EXPANSION": "NO",
        "EXPAND_ONLY_PREDEF": "NO",
        "SEARCH_INCLUDES": "YES",
        "SKIP_FUNCTION_MACROS": "YES",
        "ALLEXTERNALS": "NO",
        "EXTERNAL_GROUPS": "YES",
        "EXTERNAL_PAGES": "YES",
        "CLASS_DIAGRAMS": "YES",
        "HIDE_UNDOC_RELATIONS": "YES",
        "HAVE_DOT": "NO",
        "CLASS_GRAPH": "YES",
        "COLLABORATION_GRAPH": "YES",
        "GROUP_GRAPHS": "YES",
        "UML_LOOK": "NO",
        "UML_LIMIT_NUM_FIELDS": "10",
        # "DOT_UML_DETAILS": "NO",
        # "DOT_WRAP_THRESHOLD": "17",
        "TEMPLATE_RELATIONS": "NO",
        "INCLUDE_GRAPH": "YES",
        "INCLUDED_BY_GRAPH": "YES",
        "CALL_GRAPH": "NO",
        "CALLER_GRAPH": "NO",
        "GRAPHICAL_HIERARCHY": "YES",
        "DIRECTORY_GRAPH": "YES",
        "DOT_IMAGE_FORMAT": "png",
        "INTERACTIVE_SVG": "NO",
        "DOT_GRAPH_MAX_NODES": "50",
        "MAX_DOT_GRAPH_DEPTH": "0",
        "DOT_TRANSPARENT": "NO",
        "DOT_MULTI_TARGETS": "NO",
        "GENERATE_LEGEND": "YES",
        "DOT_CLEANUP": "YES",
    }


def get_users_override_config(config_location: str) -> Dict:
    """
    If the user specified a config then load it. No error checking is done to the config, it's up to the user
    to read the config documentation at https://www.doxygen.nl/manual/config.html
    Raises:
        FileNotFoundError: If the config file is not found
        ValueError: If config is not in valid json
    Returns: The user supplied doxygen configuration as a dictionary
    """

    assert config_location is not None
    assert isinstance(config_location, str)

    if not os.path.exists(config_location):
        raise FileNotFoundError(
            f"The doxygen configuration file does not exist at the location: {config_location}"
        )

    try:
        with open(config_location, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.critical("Config file is not in valid JSON format")
        raise e

    return config


def write(config: Dict, write_location: str) -> bool:
    """
    This function takes the dictionary of key, values used to configure Doxygen and then writes
    the configuration file to disk

    Args:
        config: The merged user defined and default doxygen config as a dictionary
        write_location: Location to write the doxygen config to disk

    Returns: True if successful and False if not
    """
    assert isinstance(config, dict)

    logger.info(f"Writing doxygen configuration file to: {write_location}")

    # Check we can write to that location
    dirname = os.path.dirname(write_location)
    if not os.path.exists(dirname):
        logger.debug(f"Creating directory {dirname}")
        try:
            Path(dirname).mkdir(parents=True)
        except OSError as e:
            logger.critical(f"Failed to create the directory: {dirname}")
            logger.critical(
                f"Failed to write the configuration file to: {write_location}"
            )
            logger.critical(e)
            return False

    # Write the config file
    try:
        with open(write_location, "w") as file_handler:
            str_conf = convert_conf(config)
            file_handler.writelines(str_conf)
            _ = [logger.debug(x.strip()) for x in str_conf]  # type: ignore
    except OSError as e:
        logger.critical(
            f"Failed to write the doxygen configuration file to: {write_location}"
        )
        logger.critical(e)
        return False

    return True


def convert_conf(config: Dict) -> Tuple[str, ...]:
    """
    Converts the Doxygen config from a dict to a string that the doxygen program can parse
    Returns: A tuple where each elemente is a line to write to disk
    """
    assert isinstance(config, dict)
    return tuple([f"{key.upper()} = {value}\n" for key, value in config.items()])
