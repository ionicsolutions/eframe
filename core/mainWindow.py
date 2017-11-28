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
import logging
import logging.handlers
import os
import time
import traceback

from PyQt4 import QtGui, QtCore

import ui.EFrame_UI as EFrame_UI
from core.state import State
from ui.QTextEditHandler import QTextEditHandler


class MainWindow:
    """Display EFrame's main window."""

    def __init__(self, rootLogger, thLevel, expFile):
        self.experiment = None
        self.logger = logging.getLogger("mainWindow")

        self.prepareGUI()

        # add logging to output tab (using the global logger)
        rootLogger.debug("Add GUI log handler.")
        th = QTextEditHandler(self.ui.outputEdit)
        th.setLevel(thLevel)
        rootLogger.addHandler(th)

        # initialize state
        self.s = State(self.mainWindow)

        # display main window
        self.mainWindow.closeEvent = self.closeEvent
        self.mainWindow.show()

        # initialize GUI update
        self.updateInterval = 200  # ms
        self.running = False
        self.startUpdate()

        self.ui.fileNameEdit.setText(expFile)

        self.app.exec_()

    def prepareGUI(self):
        self.logger.info("Start to initialize GUI.")
        self.app = QtGui.QApplication([""])

        self.mainWindow = QtGui.QMainWindow()
        self.mainWindow.setWindowIcon(QtGui.QIcon("ui/icon.png"))

        self.app.setActiveWindow(self.mainWindow)
        self.ui = EFrame_UI.Ui_MainWindow()
        self.ui.setupUi(self.mainWindow)

        self.ui.loadFileButton.clicked.connect(self.loadFile)
        self.ui.saveFileButton.clicked.connect(self.saveFile)
        self.ui.runFileButton.clicked.connect(self.runFile)

    def closeEvent(self, event):
        self.stopUpdate()
        self.s.removeAllModules()

    def startUpdate(self):
        if self.running:
            self.logger.warning("Already running GUI update.")
        else:
            self.running = True
            QtCore.QTimer.singleShot(self.updateInterval, self.update)

    def stopUpdate(self):
        self.running = False

    def update(self):
        """ Update the mainWindow GUI and all module GUIs.

            This is called by :meth:`.updateTimer` at a default interval of 200
             ms. We dynamically adjust the update interval
            between 200 and 500 ms. This is also useful to optimize modules and
            to investigate where e.g. blocking calls to remote servers cause
            unnecessary delays.

            Note that module-level update methods should never query remote
            hosts and should avoid calling methods from other EFrame modules.
            Ideally, all values to be set in the GUI should be read from a local
            dictionary or list. See the documentation for
            :meth:`~baseModule.baseModule.update` for details on this, where
            some underlying restrictions due to Python's implementation are
            discussed as well.
        """
        if self.running:
            start = time.time()
            try:
                self.s.updateAllModules()
            except Exception as e:
                self.logger.critical(
                    "Unhandled exception during GUI update: %s", e)
                self.logger.error(traceback.format_exc())
            finally:
                delta = (time.time() - start) * 1000  # duration in ms
                self._computeUpdateInterval(delta)
                wait = max(delta - self.updateInterval, 0)
                QtCore.QTimer.singleShot(wait, self.update)
        else:
            self.logger.info("GUI update thread stopped.")

    def _computeUpdateInterval(self, delta):
        if delta < 0.35 * self.updateInterval:
            if self.updateInterval > 200:
                if 0.85 * self.updateInterval > 200.0:
                    self.updateInterval = int(0.85 * self.updateInterval)
                else:
                    self.updateInterval = 200
                self.logger.debug("Reducing GUI updateInterval to %d ms.",
                                  self.updateInterval)
        elif delta < 0.5 * self.updateInterval:
            self.logger.info("GUI update took %d ms (> 35/100).", delta)
            if self.updateInterval * 1.15 < 500 and delta < 500:
                self.updateInterval = max(int(self.updateInterval * 1.15),
                                          delta)
                self.logger.debug("Increasing GUI updateInterval to %d ms.",
                                  self.updateInterval)
            else:
                self.updateInterval = 500
                self.logger.critical("Already running at maximum GUI update"
                                     "Interval of 500 ms.")
        else:
            self.logger.warning("GUI update took %d ms (> 50/100).", delta)
            if self.updateInterval * 1.5 < 500 and delta < 500:
                self.updateInterval = max(int(self.updateInterval * 1.5), delta)
                self.logger.debug("Increasing GUI updateInterval to %d ms.",
                                  self.updateInterval)
            else:
                self.updateInterval = 500
                self.logger.critical("Already running at maximum GUI update "
                                     "interval of 500 ms.")

    def loadFile(self):
        """Load an experiment configuration."""
        fileName = QtGui.QFileDialog.getOpenFileName(
            parent=self.mainWindow, caption="Load File",
            directory="config/", filter="*.conf")

        if str(fileName).strip() != "":
            self.ui.fileNameEdit.setText(fileName)
        else:
            self.logger.error("'%s' is not a valid filename.", fileName)

    def saveFile(self):
        """Save an experiment configuration."""
        fileName = str(self.ui.fileNameEdit.text())
        if fileName.strip() != "":
            self.logger.info("Saving configuration for %s.", fileName)
            # save the XML configuration
            self.storeGeometry()
            self.s.config.currentFileName = fileName
            self.s.config.saveXML()
            # save the window state
            self.saveWindowState()
            self.logger.info("Done saving.")
        else:
            self.logger.error("'%s' is not a valid filename.", fileName)

    def storeGeometry(self):
        self.s.config.width = self.mainWindow.geometry().width()
        self.s.config.height = self.mainWindow.geometry().height()
        self.s.config.x = self.mainWindow.x()
        self.s.config.y = self.mainWindow.y()

    def saveWindowState(self):
        """Save the GUI state (i.e. position of widgets) to fileName.layout."""
        fileName = self.s.config.currentFileName
        if fileName is None:
            self.logger.warning("No window state to save. Need to run an "
                                "experiment first.")
        else:
            fileName = "%s.layout" % fileName
            try:
                with open(fileName, "w") as f:
                    f.write(self.mainWindow.saveState())
            except IOError:
                self.logger.error("Failed to write '%s'.", fileName)
            else:
                self.logger.info("Wrote window state to '%s'.", fileName)

    def loadWindowState(self):
        """Load a GUI state."""
        self.stopUpdate()
        fileName = self.s.config.currentFileName
        if fileName is None:
            self.logger.warning("No window state to load. Please specify a "
                                "configuration file first.")
        else:
            fileName = "%s.layout" % fileName
            try:
                with open(fileName, "r") as f:
                    data = f.read()
            except IOError:
                self.logger.warning("No window state found for configuration"
                                    "'%s'.", fileName)
            else:
                self.mainWindow.restoreState(data)
                self.logger.info("Loaded window state from '%s'.", fileName)
        self.s.loadingCompleted.emit()
        self.startUpdate()

    def reloadModule(self, name):
        self.stopUpdate()
        self.saveWindowState()
        self.s.reloadModule(name)
        QtCore.QTimer.singleShot(1, self.loadWindowState)

    def runFile(self):
        """Run an experiment."""
        fileName = str(self.ui.fileNameEdit.text()).strip()
        dirPath, expName = os.path.split(fileName)

        # ensure the file is a .conf file, then strip the extension
        if expName[-5:] != '.conf':
            self.logger.error(
                "Bad extension. Experiment configuration needs to"
                "be a .conf file. Submitted filename: '%s'.", fileName)
            return
        else:
            expName = expName[:-5]

        self.logger.info("Clear state...")
        self.stopUpdate()
        self.s.removeAllModules()
        self.app.processEvents()

        self.logger.info("Starting experiment configuration '%s'.", expName)
        self.ui.fileNameEdit.setText(fileName)

        try:
            with open(fileName, "r") as config:
                toBeLoaded = [line.strip() for line in config
                              if not line.strip()[0] == "#"]
        except IOError:
            self.logger.error("Cannot read file %s.", fileName)
            return

        self.logger.info("Loading XML configuration file.")
        self.s.config.currentFileName = fileName
        self.s.config.loadXML()

        self.logger.debug("Restoring window geometry and position.")
        self.mainWindow.resize(self.s.config.width, self.s.config.height)
        self.mainWindow.move(self.s.config.x, self.s.config.y)

        self.logger.info("Loading %d modules.", len(toBeLoaded))
        try:
            for moduleName in toBeLoaded:
                if self.s.loaded(moduleName):
                    # this can happen through baseModule.requiresModule()
                    self.logger.debug("Module %s is already loaded.",
                                      moduleName)
                else:
                    self.s.addModule(moduleName)
        except Exception as e:
            self.logger.error("Caught exception during initialization: "
                              "'%s: %s'.",
                              e.__class__.__name__, e.message)
            self.logger.error("%s", traceback.format_exc())


        self.logger.debug("Restoring window state.")
        # TB: This does not work properly if it is done directly, but
        # calling it in a single shot timer seems to fix this
        # https://bugreports.qt-project.org/browse/QTBUG-15080
        # This is apparently not the whole story. I also had to change the
        # names of the objects to avoid using the name 'remoteControl'.
        # KK: Maybe we can run processEvents instead of the singleShot?
        QtCore.QTimer.singleShot(1, self.loadWindowState)
