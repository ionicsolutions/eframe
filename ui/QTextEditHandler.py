# -*- coding: utf-8 -*-
#
#   (c) 2016-2017 Kilian Kluge
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
A :class:`logging.Handler` class for displaying log messages in a
:class:`QtGui.QTextEdit` widget.

Based on the example given in `this Stackoverflow post \
<https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget>`_.

Written by Kilian Kluge for use in EFrame.
"""
import logging
import logging.handlers
import sys
from PyQt4 import QtGui


class QTextEditHandler(logging.Handler):
    """Display log messages in a :class:`QtGui.QTextEdit` widget.

    :param: textEdit: Instance of :class:`QTextEdit` to log to.
    """
    def __init__(self, textEdit):
        logging.Handler.__init__(self)
        # format the output
        fmt = "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
        datefmt = "%H:%M:%S"
        self.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        self.fontColors = { "DEBUG" : "gray",
                            "INFO" : "black",
                            "WARNING" : "orange",
                            "ERROR" : "red",
                            "CRITICAL" : "red" }
        # configure the textEdit (most of the details are still handled in
        # EFrame_UI.py)
        self.textEdit = textEdit
        self.textEdit.setReadOnly(True)

    def emit(self, record):
        color = self.fontColors[record.levelname]
        charFormat = QtGui.QTextCharFormat()
        charFormat.setForeground(QtGui.QBrush(QtGui.QColor(color)))
        self.textEdit.setCurrentCharFormat(charFormat)
        self.textEdit.append(self.format(record))
        
        
def _logMe():
    """Add log entries to test the handler."""
    logger.info("Solange Norwegen nicht untergeht,")
    logger.warning("gilt hier warten, und weiter rufen:")
    logger.debug("LAND IN SICHT!")
    logger.error("Du kannst nicht bleiben, kannst nicht gehen,")
    logger.critical("dich nicht ertragen, gerade, wenn mir die Worte fehlen.")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = QtGui.QWidget()
    gridLayout = QtGui.QGridLayout(widget)

    textEdit = QtGui.QTextEdit(widget)
    gridLayout.addWidget(textEdit,0,0,1,0)

    button = QtGui.QPushButton(widget)
    button.setText("Log")
    button.clicked.connect(_logMe)
    gridLayout.addWidget(button,1, 0, 1, 1)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    th = QTextEditHandler(textEdit)
    th.setLevel(logging.DEBUG)
    logger.addHandler(th)

    widget.show()
    sys.exit(app.exec_())
