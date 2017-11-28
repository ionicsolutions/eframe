# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EFrame_UI.ui'
#
# Created: Fri Apr 21 14:36:20 2017
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(791, 605)
        MainWindow.setDockNestingEnabled(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidgetContents = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.OutputDock = QtGui.QDockWidget(MainWindow)
        self.OutputDock.setFloating(False)
        self.OutputDock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.OutputDock.setObjectName(_fromUtf8("OutputDock"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.outputEdit = QtGui.QTextEdit(self.dockWidgetContents_2)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        self.outputEdit.setFont(font)
        self.outputEdit.setObjectName(_fromUtf8("outputEdit"))
        self.horizontalLayout_2.addWidget(self.outputEdit)
        self.OutputDock.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.OutputDock)
        self.ScriptControlsDock = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ScriptControlsDock.sizePolicy().hasHeightForWidth())
        self.ScriptControlsDock.setSizePolicy(sizePolicy)
        self.ScriptControlsDock.setMinimumSize(QtCore.QSize(233, 73))
        self.ScriptControlsDock.setMaximumSize(QtCore.QSize(524287, 524287))
        self.ScriptControlsDock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.ScriptControlsDock.setObjectName(_fromUtf8("ScriptControlsDock"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.fileNameEdit = QtGui.QLineEdit(self.dockWidgetContents_3)
        self.fileNameEdit.setObjectName(_fromUtf8("fileNameEdit"))
        self.horizontalLayout_5.addWidget(self.fileNameEdit)
        self.widget = QtGui.QWidget(self.dockWidgetContents_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 35))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.loadFileButton = QtGui.QPushButton(self.widget)
        self.loadFileButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.loadFileButton.setObjectName(_fromUtf8("loadFileButton"))
        self.horizontalLayout_3.addWidget(self.loadFileButton)
        self.saveFileButton = QtGui.QPushButton(self.widget)
        self.saveFileButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.saveFileButton.setObjectName(_fromUtf8("saveFileButton"))
        self.horizontalLayout_3.addWidget(self.saveFileButton)
        self.runFileButton = QtGui.QPushButton(self.widget)
        self.runFileButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.runFileButton.setObjectName(_fromUtf8("runFileButton"))
        self.horizontalLayout_3.addWidget(self.runFileButton)
        self.horizontalLayout_5.addWidget(self.widget)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.ScriptControlsDock.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.ScriptControlsDock)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "EFrame. Ionic Solutions.", None))
        self.OutputDock.setWindowTitle(_translate("MainWindow", "Log", None))
        self.ScriptControlsDock.setWindowTitle(_translate("MainWindow", "Experiment File", None))
        self.loadFileButton.setText(_translate("MainWindow", "Load", None))
        self.saveFileButton.setText(_translate("MainWindow", "Save", None))
        self.runFileButton.setText(_translate("MainWindow", "Run", None))
