#!/usr/bin/env python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import os
import sys
import json
import enum
import pickle
import shutil
import bisect
import zipfile
import logging
import subprocess
from pprint import pprint
from collections import deque
from datetime import datetime, date, time, timedelta
sys.path.append("/home/alex/yandex/avin-dev/avin/")
from avin.const import UTC
import avin

logger = logging.getLogger("LOGGER")


class UEncoder(json.JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()

def UDecoder(dict_obj):
    # One practice
    for k, v in dict_obj.items():
        if isinstance(v, str) and "+00:00" in v:
            try:
                dict_obj[k] = datetime.datetime.fromisoformat(v)
            except:
                pass
    # Two practice
    if "dt" in dict_obj:
        dict_obj["dt"] = datetime.datetime.fromisoformat(dict_obj["dt"])
    return dict_obj


if __name__ == "__main__":
    ...

