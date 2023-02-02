import argparse
from .motogp import gp_main
from .worldsbk import sbk_main

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
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()
    if args.motogp:
        gp_main()
    if args.sbk:
        sbk_main()
