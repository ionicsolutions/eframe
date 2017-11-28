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
"""Collection of commonly used functions which make EFrame more robust."""
import traceback
from functools import wraps


def singleshot(func):
    """Catch exceptions from methods called via :meth:`QTimer.singleShot`.

    This decorator should be applied to all methods which are called
    via :meth:`QTimer.singleShot` as these "threads" otherwise fail silently.

    .. note :: This decorator should only be used as an additional safety
               net. Exceptions which can be thrown during normal operation,
               e.g. connection failures, should be handled by the class
               method. This decorator's only purpose is to notify the
               user that a singleShot "thread" has malfunctioned and give
               access to and log the stack trace.
    """

    @wraps(func)
    def inner_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.logger.critical("singleShot call to %s failed: %s: %s",
                                 func, e.__class__.__name__, e.message)
            self.logger.error("%s", traceback.format_exc())

    return inner_func
