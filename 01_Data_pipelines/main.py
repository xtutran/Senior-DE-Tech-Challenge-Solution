# -*- coding: utf-8 -*-

"""
Main PySpark driver to process the application data.
"""
from __future__ import print_function

import argparse
import logging

from module.transformer import Transformer


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        type=str,
                        help="Raw application data",
                        required=True)
    parser.add_argument("--output",
                        type=str,
                        help="Output directory",
                        required=True)
    parser.add_argument("--format",
                        type=str,
                        help="Input data format",
                        default="csv")
    parser.add_argument("--stats",
                        type=bool,
                        help="True to generate statistic data",
                        default=False)
    parser.add_argument("--etl-time",
                        type=str,
                        help="ETL run time, format: YYYYmmdddHHMMSS",
                        default=None)

    arguments, _ = parser.parse_known_args()
    logging.getLogger(__name__).info(f"Input arguments: {arguments}")
    transformer = Transformer(
        input_path=arguments.input,
        output_path=arguments.output,
        file_fmt=arguments.format,
        etl_time=arguments.etl_time
    )
    if arguments.stats:
        transformer.load().transform().stats().store()
    else:
        transformer.load().transform().store()


if __name__ == '__main__':
    main()
