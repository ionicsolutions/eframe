# -*- coding: utf-8 -*-
#
#   (c) 2016-2017 Kilian Kluge
#   (c) 2014-2016 Tim Ballance
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
"""Provides access to data storage for EFrame modules.

----
data
----

The `./data/` storage area provides a consistently structured storage
space for measurement data. Modules can request the current data-path or
a filename to save to by calling :meth:`~core.storage.Storage.data`.

------
static
------

Introduced in `e25248c019ff39e9a3c98009bcfc47ab8e8f02c1`, the `./static/`
structure allows modules to save data which is not part
of the configuration, but not measurement data. One example are the
compensation matrices for the :class:`~microMotion.microMotion` module.

Static data is not restricted to any single type of file format. In
many cases, the :mod:`pickle` module is utilized. This allows modules to keep
e.g. a settings history by storing settings dictionaries in a list,
which is then pickled and stored.

In contrast to the XML configuration file accessed through
:class:`~core.config.XMLConfig`, the `./static/` structure is
not part of the git repository. Therefore, backups need to be taken
care of locally.
"""

import logging
import os
import time


class Storage:
    def __init__(self, dataPath="data"):
        self.logger = logging.getLogger("State.Storage")
        if not os.path.exists("static"):
            os.mkdir("static")

        if not os.path.exists(dataPath):
            try:
                os.mkdir(dataPath)
            except Exception as e:
                self.logger.error(
                    "Failed to create folder '%s': %s. Falling back to "
                    "local folder '.data'.", dataPath, e)
                if not os.path.exists("data"):
                    os.mkdir("data")
                dataPath = "data"
        self.dataPath = dataPath

    def data(self, moduleName, fileName=None):
        """Generate a filename to save data to."""
        path = "%s/%s" % (self.dataPath, time.strftime("%Y%m%d"))
        if not os.path.exists(path):
            os.mkdir(path)
        path += "/%s" % moduleName
        if not os.path.exists(path):
            os.mkdir(path)
        # add a timestamp
        path += "/%s" % (time.strftime("%Y%m%d-%H%M%S"))
        if fileName is not None:
            path += " - %s" % fileName
        self.logger.debug("%s" % path)
        return path

    def static(self, moduleName, fileName=None):
        """Generate a path for static data."""
        path = "static/%s" % moduleName
        if not os.path.exists(path):
            os.mkdir(path)
        if fileName is not None:
            path += "/%s" % fileName
        self.logger.debug("%s" % path)
        return path
