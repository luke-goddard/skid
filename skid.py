"""
Usage:
    skid.py --help
    skid.py ir --source <path> [--doxyconf <conf.json> -wnv -q -d]

Arguments:
    ir          interface-recovery

Options (interface-recovery):
    --source -s=<path>
    --doxyconf=<path.json>

Misc Options:
    --dont-validate -d
    --help -h
    --verbose -v
    --no-color -n
    --write-log -w
    --quite -q
"""

import logging
import random
import os

from typing import Dict

import colorlog

from docopt import docopt

from skid.interface_recovery.entry import start_interface_recovery

def setup_logger(colour=True, verbose=False, write_location="/tmp/skid.log") -> logging.Logger:
    """ Sets up the root logger and it's formatters """
    if colour:
        fmt = "%(log_color)s%(levelname)-8s%(reset)s : %(white)s%(message)s"
    else:
        fmt = "%(levelname)-8s%(reset)s : %(message)s"

    if verbose:
        lvl = logging.DEBUG
    else:
        lvl = logging.INFO

    formatter = colorlog.ColoredFormatter(
        fmt, datefmt=None, reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    )

    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(lvl)

    file_handler = logging.FileHandler(write_location, 'w+')
    file_handler_formatter = logging.Formatter('%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    file_handler.setFormatter(file_handler_formatter)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def print_ascii():
    """ print ASCII logo """
    print("                  ████████████████████████████████████")
    print("                ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒████")
    print("              ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██████")
    print("            ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████")
    print("            ██▒▒▓▓████████████████████████████▒▒▓▓██████")
    print("            ██▒▒▓▓████████████████████████████▒▒▓▓██████")
    print("            ██▒▒▓▓████████████████████████████▒▒▓▓██████")
    print("            ██▒▒▓▓xxxxxxxxxxxxxxxxxxxxxxxxxxxx▒▒▓▓██████")
    print("            ██▒▒▓▓ ███████╗██╗  ██╗██╗██████╗ ▒▒▓▓██████")
    print("            ██▒▒▓▓ ██╔════╝██║ ██╔╝██║██╔══██╗▒▒▓▓██████")
    print("            ██▒▒▓▓ ███████╗█████╔╝ ██║██║  ██║▒▒▓▓██████")
    print("            ██▒▒▓▓ ╚════██║██╔═██╗ ██║██║  ██║▒▒▓▓██████")
    print("            ██▒▒▓▓ ███████║██║  ██╗██║██████╔╝▒▒▓▓██████")
    print("            ██▒▒▓▓ ╚══════╝╚═╝  ╚═╝╚═╝╚═════╝ ▒▒▓▓██████")
    print("            ██▒▒▓▓xxxxxxxxxxxxxxxxxxxxxxxxxxxx▒▒▓▓██████")
    print("            ██▒▒▓▓████████████████████████████▒▒▓▓██████")
    print("            ██▒▒▓▓████████████████████████████▒▒▓▓██████")
    print("            ██▒▒▓▓████████████████████████████▒▒▓▓██████")
    print("            ██▒▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓██████")
    print("            ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████████")
    print("            ██████████████████████████████████████████████▓▓██")
    print("            ████████████████████████████████████████████▓▓████")
    print("        ██████████████████████████████████████████████▓▓██████")
    print("      ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████████")
    print("      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████")
    print("      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████████████▓▓▓▓████████")
    print("      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████████████▓▓▓▓████████")
    print("      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓████████")
    print("      ██▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████████")
    print("      ████████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒▒▒██████")
    print("    ██▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████▒▒████████")
    print("  ██▒▒██████████████████████████████████████████████████")
    print("██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓████")
    print("██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████")
    print("  ████████████████████████████████████████████████")

def print_ascii2():
    """ print ASCII logo 2"""
    print("              ▒▒              ▒▒")
    print("            ▒▒░░▒▒▒▒      ▒▒▒▒░░▒▒")
    print("          ▓▓░░  ░░░░▒▒▓▓▒▒░░░░  ░░▒▒")
    print("          ▓▓░░  ░░░░░░░░░░░░░░  ░░▒▒")
    print("          ▒▒░░    ░░░░░░░░░░    ░░▒▒")
    print("          ▒▒░░  ░░░░░░░░░░░░░░  ░░▒▒")
    print("            ▒▒░░░░  ░░░░░░  ░░░░▒▒")
    print("          ▒▒░░░░      ░░    ░░░░▒▒▒▒░░    ▒▒")
    print("          ▒▒░░    ██      ▓▓    ▒▒▓▓      ▒▒      ░░")
    print("        ▒▒░░░░                  ░░░░▒▒    ▒▒  ▒▒")
    print("          ▒▒░░      ██████      ░░▒▒    ▒▒░░  ▒▒")
    print("            ▒▒░░      ██      ▒▒▓▓    ▒▒░░░░  ░░")
    print("          ▒▒░░▒▒░░          ░░▒▒░░▒▒▒▒░░░░░░▒▒")
    print("          ▒▒  ░░              ▓▓░░░░▒▒▒▒▒▒▒▒░░")
    print("        ▒▒░░                ░░░░░░░░░░░░▒▒")
    print("        ▒▒▒▒▒▒            ░░░░▒▒▒▒▒▒░░░░▒▒")
    print("        ▒▒░░░░▓▓      ▒▒  ░░░░▒▒░░░░░░░░▒▒")
    print("        ▒▒░░░░▒▒      ▒▒  ░░░░▒▒  ░░░░░░▒▒")
    print("        ▒▒░░    ▓▓  ▒▒      ░░▒▒      ▒▒")
    print("          ▒▒      ▒▒          ▒▒  ▒▒  ▒▒")
    print("        ▒▒  ▒▒  ▒▒  ▒▒  ▒▒  ▒▒▒▒▒▒▒▒▒▒")
    print("        ▒▒▓▓▒▒▒▒    ▓▓▒▒▒▒▒▒")
    print("██▒▒▓▓xxxxxxxxxxxxxxxxxxxxxxxxxxxx▒▒▓▓██████")
    print("██▒▒▓▓ ███████╗██╗  ██╗██╗██████╗ ▒▒▓▓██████")
    print("██▒▒▓▓ ██╔════╝██║ ██╔╝██║██╔══██╗▒▒▓▓██████")
    print("██▒▒▓▓ ███████╗█████╔╝ ██║██║  ██║▒▒▓▓██████")
    print("██▒▒▓▓ ╚════██║██╔═██╗ ██║██║  ██║▒▒▓▓██████")
    print("██▒▒▓▓ ███████║██║  ██╗██║██████╔╝▒▒▓▓██████")
    print("██▒▒▓▓ ╚══════╝╚═╝  ╚═╝╚═╝╚═════╝ ▒▒▓▓██████")
    print("██▒▒▓▓xxxxxxxxxxxxxxxxxxxxxxxxxxxx▒▒▓▓██████")


def main(arguments: Dict):
    asciiarts = [print_ascii, print_ascii2]
    asciiarts[random.randint(0, len(asciiarts)-1)]()
    # print_ascii()
    log = setup_logger(colour=not arguments["--no-color"], verbose=arguments["--verbose"])

    try:
        if arguments["ir"]:
            start_interface_recovery(arguments)
        else:
            log.critical("No command mode found!!")
    except Exception as e: 
        log.exception(e)
        log.critical("An unexpected programing error occured")
        log.warning("You can check the log file at /tmp/skid.log")
        log.warning("Please file a bug report to -> https://github.com/luke-goddard/skid/issues/new")

    log.info("Finished")


if __name__ == "__main__":
    arguments = docopt(__doc__)
    try:
        main(arguments)
    except KeyboardInterrupt:
        os.system("killall doxygen")
