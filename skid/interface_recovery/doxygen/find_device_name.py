"""
All of the following can be used to register a device, to my knowlage no other functions
can be used to register devices

```
    inlucde: <linux/fs.h>

    register_chardev(unsigned int major, const char *name, struct file_operations *fops);
        create and register a cdev occupying a range of minors
        e.g: register_chrdev(USB_MAJOR, "usb", &usb_fops);


    register_chardev_region(dev_t from, unsigned count, const char *name);
        register a range of device numbers from, ...(from+count)
        e.g: register_chrdev_region(MKDEV(TTYAUX_MAJOR, 0), 1, "/dev/tty");


    alloc_chardev_region(dev_t *dev, unsigned baseminor, unsigned count, const char *name);
        register a range of char device numbers
        e.g: alloc_chrdev_region(&pi433_dev, 0, N_PI433_MINORS, "pi433");
```

This module is used to

Author: Luke Goddard
Date: 2020
"""

import os
import logging

from typing import Tuple
from multiprocessing import Pool

from lxml import etree 
from alive_progress import alive_bar # type: ignore

from skid.utils import utils
from skid.interface_recovery.doxygen import xml_parser
from skid.interface_recovery.doxygen.find_structs import stringify_children

logger = logging.getLogger(__name__)

INCLUDE_FILE = "linux/fs.h"

def xml_list_must_include(xml_files: Tuple[str, ...], header: str) -> Tuple[str, ...]:
    """
    Given a list of xml_file locations this function will return a new tuple
    of xml_file locations that all include the header file `header`
    """
    keep_files = list()

    title = utils.format_alive_bar_title(f"Finding source files that include '{header}'")
    with alive_bar(len(xml_files), title=title) as bar:
        with Pool(processes=os.cpu_count()) as pool:
            for res, xml_file in pool.imap_unordered(xml_file_includes, [(xml_file, header) for xml_file in xml_files]):
                bar()
                if res:
                    keep_files.append(xml_file)
    return tuple(keep_files)

def xml_file_includes(args: Tuple[str, str]) -> Tuple[bool, str]:
    assert len(args) == 2
    xml_file, header = args
    try:
        root = xml_parser.get_root(xml_file)
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

            if header in stringify_children(highlight):
                logger.debug(f"The following file include {header}: {xml_file}")

            return (True, xml_file)

    return (False, xml_file)




def find_all_register_chardev(xml_files: Tuple[str, ...]):
    logger.debug("Finding all register_chrdev(unsigned int major, const char *name, struct file_operations *fops)")
    pass
