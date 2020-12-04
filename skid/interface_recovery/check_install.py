"""
Checks that the system has the required dependencies installed

Author: Luke Goddard
Date: 2020
"""

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)

NOT_FOUND_ERR_MSG = lambda tool: f"Failed to find {tool}, is it installed?"


def check_dependencies() -> bool:
    """
    Returns True if the current environment has all the required dependencies
    for the interface recovery page
    """
    print("")
    logger.info("System Configuration")
    logger.info("====================")
    log_environment_config()
    res = check_doxygen() and check_clang()

    return res


def log_environment_config() -> None:
    """ Log the runtime environment for bug reports """
    logger.info(f"Machine: {platform.machine()}")
    logger.info(f"Version: {platform.version()}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"System: {platform.system()}")
    logger.info(f"Processor: {platform.processor()}")


def check_doxygen() -> bool:
    """
    Checks that the current environment has doxygen installed. In future we could
    check that the required version is installed
    """
    proc = subprocess.run(
        ["doxygen", "--version"], check=False, capture_output=True, text=True
    )

    if proc.returncode != 0:
        logger.critical(NOT_FOUND_ERR_MSG("doxygen"))
        return False

    sproc = proc.stdout.split(" ")
    logger.info(f"Found Doxygen version {sproc[0]}")
    return True


def check_clang() -> bool:
    """ Checks that clang is installed in the current environment """
    proc = subprocess.run(["clang", "-v"], check=False, capture_output=True, text=True)

    if proc.returncode != 0:
        logger.critical(NOT_FOUND_ERR_MSG("clang"))
        return False

    try:
        clang_version = proc.stderr.splitlines()[0].split(" ")[2]
        logger.info(f"Found Clang version {clang_version}")
    except IndexError:
        logger.warning("Failed to get the clang version")

    return True
