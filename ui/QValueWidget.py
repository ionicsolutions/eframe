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
import math

from PyQt4 import QtGui, QtCore
from QDoubleSpinBoxWithFocus import QDoubleSpinBoxWithFocus


class QValueWidget(QtGui.QWidget):
    """Custom widget for entry and display of numbers.

    A :class:`.QValueWidget` consists of a text label and a spin box.
    It supports limits on its range, the display of a unit, and several
    custom signals.

    :param label: Text to the left of the box. Hidden if empty.
    :param minValue:
    :param maxValue:
    :param stepSize:
    :param initialValue:
    :param parent: Parent widget.
    :param buttonSymbols:
    :param hideLabel: Force label to be hidden.
    :param forcedDecimalPlaces: If not set, the number of decimal places
                                is calculated based on the step size.
    :param toolTip:
    :param unit:
    :type label: str
    :type hideLabel: bool
    """
    valueChanged = QtCore.pyqtSignal((float,), (str, float,))
    receivedFocus = QtCore.pyqtSignal()
    lostFocus = QtCore.pyqtSignal()

    def __init__(self, label, minValue, maxValue, stepSize, initialValue,
                 parent=None,
                 buttonSymbols=QtGui.QAbstractSpinBox.UpDownArrows,
                 hideLabel=False, forcedDecimalPlaces=None, toolTip=None,
                 unit=None):
        super(self.__class__, self).__init__(parent)
        self.hbox = QtGui.QHBoxLayout(self)
        self.hbox.setSpacing(0)
        self.hbox.setMargin(0)

        self.labelText = label
        self.logger = logging.getLogger("valueWidget %s" % self.labelText)

        if not hideLabel and label:
            self.label = QtGui.QLabel("%s:" % self.labelText, self)
            self.label.setAlignment(
                QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.hbox.addWidget(self.label)

        self.spinBox = QDoubleSpinBoxWithFocus(self)
        self.spinBox.valueChanged.connect(self.valueChangedEvent)
        self.spinBox.receivedFocus.connect(self.receivedFocus)
        self.spinBox.lostFocus.connect(self.lostFocus)

        if buttonSymbols is None:
            self.spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        else:
            self.spinBox.setButtonSymbols(buttonSymbols)

        self.setRange(minValue, maxValue)

        if stepSize <= 0:
            raise ValueError(
                "Step size cannot be negative. Was initialized "
                "with a stepsize of %0.4f" % stepSize)
        self.spinBox.setSingleStep(stepSize)

        if forcedDecimalPlaces is None:
            if stepSize < 1.0:
                self.spinBox.setDecimals(
                    math.ceil(math.log(1.0 / stepSize, 10)))
            else:
                self.spinBox.setDecimals(0)
        else:
            self.spinBox.setDecimals(int(forcedDecimalPlaces))

        if unit is not None:
            self.spinBox.setSuffix(" %s" % unit)

        if toolTip is not None:
            self.hbox.setToolTip(toolTip)

        if isinstance(initialValue, float) or isinstance(initialValue, int):
            self.spinBox.setValue(initialValue)
        else:
            self.spinBox.setValue(minValue)

        self.spinBox.setKeyboardTracking(False)

        self.hbox.addWidget(self.spinBox)
        self.setLayout(self.hbox)

    def setValue(self, value, force=False):
        """Set the value of the spin box.

        If *force* is *False*, the value will not be set if the spin box
        has the focus.
        """
        if self.spinBox.hasFocus() and not force:
            pass  # if the spinbox is being edited by the user, don't update
        else:
            if isinstance(value, float) or isinstance(value, int):
                self.spinBox.blockSignals(True)
                self.spinBox.setValue(value)
                self.spinBox.blockSignals(False)
            else:
                self.logger.error("Value %s has invalid type %s.",
                                  value, type(value))
                self.spinBox.clear()

    def value(self):
        """Return the current value."""
        return self.spinBox.value()

    def getValue(self):
        """Return the current value."""
        return self.spinBox.value()

    def clear(self):
        """Clear the value."""
        self.spinBox.clear()

    def setReadOnly(self, readOnly):
        """Set the box read-only."""
        self.spinBox.setReadOnly(readOnly)

    def valueChangedEvent(self, value):
        self.valueChanged[str, float].emit(self.labelText, value)
        self.valueChanged[float].emit(value)

    def setEnabled(self, enabled):
        """Enable or disable the widget."""
        self.spinBox.setEnabled(enabled)

    def setRange(self, newMinimum, newMaximum):
        if newMinimum <= newMaximum:
            self.spinBox.setMinimum(newMinimum)
            self.spinBox.setMaximum(newMaximum)
        else:
            self.spinBox.setMinimum(newMaximum)
            self.spinBox.setMaximum(newMinimum)
