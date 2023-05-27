#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_binance import SourceBinance

if __name__ == "__main__":
    source = SourceBinance()
    launch(source, sys.argv[1:])
