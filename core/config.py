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
"""Provide access to module-level configuration.

The configuration for all EFrame modules is stored in a single XML file,
whose content is parsed and generated by each module (see
:meth:`modules.baseModule.baseModule.parseConfig` and
:meth:`~modules.baseModule.baseModule.saveConfig`).
"""
import logging
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString as MDParseString
import traceback


class XMLConfig:
    """Provide access to the configuration stored in an EFrame XML file."""

    def __init__(self, modules):
        self.logger = logging.getLogger("State.XMLConfig")
        self.modules = modules
        self.currentFileName = None
        self.configTree = None
        self.configRoot = None

        # WINDOW GEOMETRY
        self.defaultGeometry = (1024, 768, 50, 50)
        self.width, self.height, self.x, self.y = self.defaultGeometry

        # STORAGE
        self.dataPath = "data"

    def loadXML(self):
        """Load and parse the XML config file for the current configuration."""
        if self.currentFileName is None:
            self.logger.error("No experiment configuration loaded. Cannot "
                              "parse XML configuration.")
            return

        self.logger.debug("Loading file '%s.xml'.", self.currentFileName)
        try:
            self.configTree = ET.parse("%s.xml" % self.currentFileName)
        except IOError:
            self.logger.error("Could not read '%s.xml'. Might be missing."
                              "Creating a new XML configuration which will "
                              "be written to '%s.xml' upon 'Save'.",
                              self.currentFileName, self.currentFileName)
            self.configTree = ET.ElementTree()
        except ET.ParseError:
            self.logger.error("Could not parse '%s.xml'.",
                              self.currentFileName)
        else:
            self.configRoot = self.configTree.getroot()
            self._loadWindowGeometry()
            self._loadStorageConfiguration()

    def _loadWindowGeometry(self):
        geometryElement = self.configRoot.find("geometry")
        if geometryElement is not None:
            try:
                self.width = int(geometryElement.get("width"))
                self.height = int(geometryElement.get("height"))
                self.x = int(geometryElement.get("x"))
                self.y = int(geometryElement.get("y"))
            except (ValueError, TypeError):
                self.logger.error("Invalid or missing geometry configuration.")
                self.logger.debug("%s", geometryElement)
                self.width, self.height, self.x, self.y = self.defaultGeometry
        else:
            self.logger.warning("Found no window geometry, using defaults.")
            self.width, self.height, self.x, self.y = self.defaultGeometry

    def _loadStorageConfiguration(self):
        storageElement = self.configRoot.find("storage")
        if storageElement is not None:
            dataPath = storageElement.get("dataPath")
            if dataPath is not None:
                self.dataPath = dataPath

    def saveXML(self):
        """Save the XML config file."""
        if self.currentFileName is None:
            self.logger.warning("No experiment loaded, doing nothing.")
            return

        oldModules = []
        if self.configRoot is not None:
            oldModules = self.configRoot.findall('module')

        # Create a new root element
        self.configRoot = ET.Element("config")

        # Save the window geometry
        geometryElement = ET.Element("geometry")
        geometryElement.set("width", str(self.width))
        geometryElement.set("height", str(self.height))
        geometryElement.set("x", str(self.x))
        geometryElement.set("y", str(self.y))
        self.configRoot.append(geometryElement)

        for name, module in self.modules.iteritems():
            try:
                module.saveConfig()
            except Exception as e:
                self.logger.error("Failed to save configuration for module %s",
                                  name)
                self.logger.error(traceback.format_exc())
                continue

            try:
                self.configRoot.append(module.XMLConfig)
            except ET.ParseError:
                self.logger.error("ParseError in XMLConfig for module '%s' "
                                  "at %s, ignoring config.",
                                  module._name, module)

        self.configTree = ET.ElementTree()
        self.configTree._setroot(self.configRoot)

        # Add any old definitions which were not rewritten
        savedModuleList = [
            element.get("name") for element in
            self.configRoot.findall("module")]
        for element in oldModules:
            if element.get("name") not in savedModuleList:
                self.configRoot.append(element)

        dataString = ET.tostring(self.configRoot)
        dataString = dataString.replace("\n", "")
        dataString = dataString.replace("\t", "")
        xmlOutput = MDParseString(dataString).toprettyxml()

        with open("%s.xml" % self.currentFileName, "w") as f:
            f.write(xmlOutput)

    def get(self, module):
        """Return config XML tree for the given module."""
        self.configRoot = self.configTree.getroot()
        if self.configRoot is not None:
            moduleConfig = self.configRoot.findall(
                "./module[@name='%s']" % (module._name))
            if not moduleConfig:
                config = None
            elif len(moduleConfig) == 1:
                config = moduleConfig[0]
            else:
                self.logger.warning("%d instances of configuration for module "
                                    "'%s' in XML file, using first.",
                                    len(moduleConfig), module)
                config = moduleConfig[0]
        else:
            config = None
        return config
