# -*- coding: utf-8 -*-
#
#   (c) 2017 Kilian Kluge
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Helper methods for handling data produced by EFrame modules."""
import numpy as np
import json


def load(filename, usecols=None, comments="#", header_lines=0):
    """Load data and status from a text file as produced by EFrame modules."""
    with open(filename, "r") as datafile:
        header = [line.lstrip("%s" % comments).rstrip()
                  for line in datafile if line[0] == comments]

    try:
        status = json.loads("".join(header[:-header_lines]))
    except ValueError:
        status = {}
        
    data = np.loadtxt(filename, usecols=usecols, comments=comments)
    data = np.transpose(data)

    return data, status
