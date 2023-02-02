# Execute with
# $ python -m motorsport_calendar_creator

import sys

if __package__ is None and not getattr(sys, "frozen", False):
    # direct call of __main__.py
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import motorsport_calendar_creator

if __name__ == "__main__":
    motorsport_calendar_creator.main()
