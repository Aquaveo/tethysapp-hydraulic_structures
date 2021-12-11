"""
********************************************************************************
* Name: __init__.py
* Author: msouff
* Created On: Dec 2, 2019
* Copyright: (c) Aquaveo 2019
********************************************************************************
"""
import argparse
from tethysapp.hydraulic_structures.cli.init_command import init_hydraulic_structures


def hydraulic_structures_command():
    """
    hydraulic_structures commandline interface function.
    """
    # Create parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands')
    # init command ----------------------------------------------------------------------------------------------------#
    init_parser = subparsers.add_parser(
        'init',
        help="Initialize the hydraulic_structures app."
    )
    init_parser.add_argument(
        'gsurl',
        help='GeoServer url to geoserver rest endpoint '
             '(e.g.: "http://admin:geoserver@localhost:8181/geoserver/rest/").'
    )
    init_parser.set_defaults(func=init_hydraulic_structures)

    # Parse commandline arguments and call command --------------------------------------------------------------------#
    args = parser.parse_args()
    args.func(args)
