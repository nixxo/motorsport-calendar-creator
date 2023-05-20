import argparse
import os
from .motogp import gp_main
from .worldsbk import sbk_main

global ROOT_DIR
__version__ = "0.1.0"


def main():
    parser = argparse.ArgumentParser(
        prog=f"Motorsport Calendar Creator {__version__}",
        description="The program scrapes motogp.com or worldsbk.com for schedule \
                    and creates an ICS file importable in your Calendar app.",
        epilog="Text at the bottom of help",
    )
    parser.add_argument(
        "--motogp", action="store_true", help="process motogp.com website"
    )
    parser.add_argument(
        "--sbk", action="store_true", help="process worldsbk.com website"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print out debug info while processing data",
    )
    parser.add_argument("-o", "--output-dir", help="output directory")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()

    ROOT_DIR = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.realpath(args.output_dir or f"{ROOT_DIR}/../data")
    if args.motogp:
        gp_main(output_dir, args.debug)
    if args.sbk:
        sbk_main(output_dir, args.debug)
