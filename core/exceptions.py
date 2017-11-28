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


class EFrameException(Exception):
    """Base exception for all EFrame exceptions."""

    def __init__(self, msg, *args, **kwargs):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class InitErrorException(EFrameException):
    """Failed to initialize :class:`~core.state.State`."""
    pass


class DataAcquisitionError(EFrameException):
    """Failed to acquire data from experimental setup."""
    pass


class HardwareError(EFrameException):
    """A request cannot be fulfilled due to hardware problems."""
