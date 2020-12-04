"""
This module is the interface recovery entry point.

Important kernel functions Notes:

    inlucde: <linux/fs.h>

    register_chardev(unsigned int major, const *char name, struct file_operations *fops);
        create and register a cdev occupying a range of minors
        e.g: register_chrdev(USB_MAJOR, "usb", &usb_fops);


    register_chardev_region(dev_t from, unsigned count, const char *name);
        register a range of device numbers from, ...(from+count)
        e.g: register_chrdev_region(MKDEV(TTYAUX_MAJOR, 0), 1, "/dev/tty");


    alloc_chardev_region(dev_t *dev, unsigned baseminor, unsigned count, const char *name);
        register a range of char device numbers
        e.g: alloc_chrdev_region(&pi433_dev, 0, N_PI433_MINORS, "pi433");

    inlucde: <linux/cdev.h>

    cdev_alloc();
        allocate a cdev structure


    cdev_init(struct cdev *cdev, const struct file_operations *fops);
        initializes a cdev structure and assign the file_operations struct to it


    cdev_add(struct cdev *cdev, struct file_operations *fops);
        adds a char device to the system, once this is done the device driver is fully
        functional. So this would be the last step


Author: Luke Goddard
Date: 2020
"""

from typing import Dict, Any
from logging import getLogger

from skid.interface_recovery.doxygen import doxygen

logger = getLogger(__name__)

def start_interface_recovery(args: Dict[str, Any]) -> bool:
    """ Starts the interface_recovery mode """

    print("")
    logger.info("Starting Interface Recovery Mode")
    logger.info("================================")

    source_location = args["--source"]
    user_config_location = args["--doxyconf"]

    if not doxygen.configure(source_location, user_config_location):
        logger.critical("Failed to configure doxygen")
        return False

    if not doxygen.run():
        return False

    xml_files = doxygen.get_all_xml_files()

    if not args["--dont-validate"]:
        schema = doxygen.get_schema()
        xml_files = doxygen.filter_xml_files_bad_schema(xml_files, schema)

    doxygen.find_all_device_names(xml_files)
    doxygen.find_fileop_structs(xml_files)

    # device_register_functions = doxygen.find_device_register_functions(
    # ioctl_handers = doxygen.find_ioctl_handers(fileop_structs)

    return True


