"""
Random utility functions

Author: Luke Goddard
Date: 2020
"""

import logging


logger = logging.getLogger(__name__)

def is_verbose() -> bool:
    """ Should be set to True if -v was passed to skid """
    return logging.getLogger("").handlers[1].level == logging.DEBUG

def format_alive_bar_title(title: str) -> str:
    # return '=========' + title.ljust(75, '-')
    return '---------> ' + title.ljust(75, '-')

