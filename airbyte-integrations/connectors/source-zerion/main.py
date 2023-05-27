#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zerion import SourceZerion

if __name__ == "__main__":
    source = SourceZerion()
    launch(source, sys.argv[1:])
