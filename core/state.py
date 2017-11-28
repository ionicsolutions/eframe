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
"""
EFrame is built around a single instance of :class:`.State`.

Like *EFrame*, the `State` was designed and written by Tim Ballance.
It was improved, documented and developed further by Kilian Kluge.
"""
import copy
import json
import logging
import operator
import traceback

import config
import lib.influx as influx
import resourceManager
import storage
from PyQt4 import QtCore
from core.exceptions import InitErrorException
from lib.statusEncoder import StatusEncoder


class State(QtCore.QObject):
    """The *State* object is the core of EFrame.

    It contains and keeps track of all modules, manages their import
    and instantiation, and facilitates the communication between modules.

    Within modules, the *State* is available as `self.s`:

    .. code-block:: python

       self.s.eomManager.setPower("Microwave", 23.4)

    *State* defines the following signals:

    * **loadingCompleted**: Emitted after loading of a configuration
      into a blank state is completed.
    * **aboutToChange**: A module is about to be removed/added/reloaded.
    * **stateChanged**: A module has been removed/added/reloaded.
    """
    loadingCompleted = QtCore.pyqtSignal()
    aboutToChange = QtCore.pyqtSignal()
    stateChanged = QtCore.pyqtSignal()

    def __init__(self, mainWindow):
        super(State, self).__init__()
        self.logger = logging.getLogger("State")

        self.mw = mainWindow
        self.modules = {}
        self.requiredBy = {}

        self.config = config.XMLConfig(self.modules)
        self.resources = resourceManager.Resources(self.modules)
        self.store = storage.Storage(self.config.dataPath)
        self.influx = influx.Influx()

    def _dispatch(self, method, params):
        """Dispatch RPC calls from :class:`~modules.remoteControl.remoteControl`."""
        self.logger.info("Remote request: %s%s", method, params)
        try:
            func = operator.attrgetter(method)(self)
        except AttributeError as e:
            self.logger.error("Remote request failed: No method %s", method)
            raise e
        else:
            try:
                return func(*params)
            except Exception as e:
                self.logger.error("Remote call to %s failed: %s",
                                  method, e)
                raise e

    def __getattr__(self, name):
        try:
            return self.modules[name]
        except KeyError:
            raise AttributeError

    def updateAllModules(self):
        """Update the GUI of all visible modules.

        If there is any exception thrown during update,
        the widget is hidden.
        """
        for name, module in self.modules.iteritems():
            if module.widget.isVisible():
                try:
                    module.update()
                except Exception as e:
                    self.logger.critical(
                        "Unhandled exception during GUI update: %s", e)
                    self.logger.error(traceback.format_exc())
                    module.widget.hide()

    def getStatus(self):
        """Compile a status message of all loaded EFrame modules.

        Status messages are regularly attached to measurements to
        allow the user to e.g. take laser settings into account
        when analyzing data.

        The status message is returned as JSON, which is readily
        parsed into a Python dictionary, stored in any of the
        databases used in the IonCavity ecosystem, and human-readable.

        .. note:: If the status is stored in the header of a CSV
           file using `np.savetxt()`, it can be extracted using
           the `lib.data.load` helper function.

        The use of a custom :class:`~lib.statusEncoder.statusEncoder`
        allows for modules to pass their internal status dictionary
        (including references to non-picklable class-instances).
        """
        status = {name: module_.getStatus()
                  for name, module_ in self.modules.iteritems()
                  if module_.getStatus()}
        return json.dumps(status, indent=4, cls=StatusEncoder)

    def addModule(self, name):
        """Add module *name* to `State`.

        Dependency management is accomplished through
        :class:`modules.baseModule.baseModule.requiresModule`.
        """
        moduleObject = self.importModule(name)

        if name not in self.modules:
            self.logger.info("Adding '%s' to state.", name)
            self.modules[name] = moduleObject
        else:
            self.logger.error("A module with name '%s' is already "
                              "registered. Please choose a unique name.",
                              name)
            self.logger.debug("Existing module: %s", self.modules[name])

    def importModule(self, name):
        """Import module *name* and return an instance."""
        try:
            module_ = __import__("modules.%s.%s" % (name, name),
                                 fromlist=[name])
            reload(module_)  # ensure we don't use an old .pyc
        except ImportError as e:
            raise InitErrorException(e)

        try:
            moduleClass = getattr(module_, name)
        except AttributeError as e:
            raise InitErrorException(e)

        moduleObject = moduleClass(self)
        self.requiredBy[name] = []
        self.logger.info("Successfully imported %s", name)
        return moduleObject

    def reloadModule(self, name):
        """Reload module *name*, taking care of dependencies."""
        dependentModules = copy.copy(self.requiredBy[name])
        self.aboutToChange.emit()
        self.logger.info("Removing dependent modules.")
        for module_ in dependentModules:
            self.removeModule(module_)

        self.logger.info("Reloading module '%s'.", name)
        self.removeModule(name)
        self.addModule(self.importModule(name))

        self.logger.info("Adding dependent modules.")
        for module_ in dependentModules:
            self.addModule(module_)
        self.stateChanged.emit()

    def alive(self, moduleObject):
        """Check whether a module instance is part of the `State`.

        This can be used by threads to check if their parent module
        is still in the `State`.
        """
        return moduleObject in self.modules.values()

    def loaded(self, moduleName):
        """Check whether module *name* is registered in the `State`."""
        return moduleName in self.modules

    def removeModule(self, name):
        """Remove module *name*, removing all dependent modules first."""
        if not self.loaded(name):
            self.logger.info("'%s' is not loaded.", name)
            return

        self.logger.info("Removing '%s'.", name)

        self.logger.debug("Checking dependencies.")
        for module_ in self.requiredBy[name]:
            self.logger.info(
                "Need to remove module '%s' dependent on '%s' prior to "
                "removing '%s'.", module_, name, name)
            self.removeModule(module_)

        self.logger.debug("Call remove() method of module '%s'.", name)
        try:
            try:
                self.modules[name].remove()
            except Exception as e:
                self.logger.critical("Remove() failed for module '%s': %s",
                                     name, e)
        except KeyError:
            self.logger.error("No module '%s' registered.", name)
        else:
            self.logger.debug("Remove instance %s of '%s' from State.",
                              self.modules[name], name)
            del self.modules[name]

        for requirements in self.requiredBy.itervalues():
            try:
                requirements.remove(name)
            except ValueError:
                pass

        del self.requiredBy[name]

    def removeAllModules(self):
        """Remove all modules from the `State`."""
        self.logger.info("Removing all modules.")
        self.aboutToChange.emit()
        for module in self.modules.keys():
            self.removeModule(module)
