"""
Random utility functions

Author: Luke Goddard
Date: 2020
"""

import logging

FORMAT_LJUST = 75
FORMAT_PREFIX = '--------->'

logger = logging.getLogger(__name__)

def is_verbose() -> bool:
    """ Should be set to True if -v was passed to skid """
    root_logger = logging.getLogger("")
    assert len(root_logger.handlers) >= 2
    return root_logger.handlers[1].level == logging.DEBUG

def format_alive_bar_title(title: str) -> str:
    """ Formats the ascii bar title """
    assert isinstance(title, str)
    return FORMAT_PREFIX + title.ljust(FORMAT_LJUST, '-')

