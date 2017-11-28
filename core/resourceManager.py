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
"""
Resource management was added to EFrame by Kilian Kluge.
"""
import logging
import threading
from PyQt4 import QtCore


class Resources(QtCore.QObject):

    claim_signal = QtCore.pyqtSignal()
    release_signal = QtCore.pyqtSignal()

    def __init__(self, modules):
        super(Resources, self).__init__()
        self.logger = logging.getLogger("State.Resources")
        self.modules = modules
        self.claimEvent = threading.Event()
        self.releaseEvent = threading.Event()
        self.claiming = False
        self.claimed = False
        self.remoteClaimRequested = False
        self.remoteReleaseRequested = False
        self.responseCounter = 0
        self.releasedEvents = {}
        self.unclaimedModules = []
        self.claimedResponses = {}

        self.claim_signal.connect(self.claim)
        self.release_signal.connect(self.release)

    def areClaimed(self):
        return self.claimed

    def isClaiming(self):
        return self.claiming

    def remoteClaimRequestHandled(self):
        return not self.remoteClaimRequested

    def remoteReleaseRequestHandled(self):
        return not self.remoteReleaseRequested

    def remoteClaim(self):
        if self.remoteClaimRequested:
            self.logger.warning(
                "Received request for remoteClaim while previous request "
                "has not yet been handled.")
        else:
            self.remoteClaimRequested = True

        self.claim_signal.emit()

    def remoteRelease(self):
        if self.remoteReleaseRequested:
            self.logger.warning(
                "Received request for remoteRelease while previous request "
                "has not yet been handled.")
        else:
            self.remoteReleaseRequested = True

        self.release_signal.emit()

    def claim(self):
        self.logger.info("Attempting to claim hardware Resources.")
        if self.claiming or self.claimed:
            self.logger.warning("Already claimed Resources (%s) or currently "
                                "claiming/releasing (%s).",
                                self.claimed, self.claiming)
            fakeClaimEvent = threading.Event()
            fakeClaimEvent.set()
            self.remoteClaimRequested = False
            return fakeClaimEvent
        else:
            self.logger.debug("Clearing events and variables.")
            self.claimEvent.clear()
            self.claiming = True
            self.claimed = False
            self.remoteClaimRequested = False

            self.logger.debug("Requesting claimedEvents and claimedFlags.")
            self.claimedResponses = {}
            self.unclaimedModules = []
            for module in self.modules.itervalues():
                self.claimedResponses[module] = module.claimResources()
            self.responseCounter = 0
            self.logger.debug("Starting timer for _waitForClaim.")
            QtCore.QTimer.singleShot(100, self._waitForClaim)
            return self.claimEvent

    def _waitForClaim(self):
        if self.claiming:
            self.logger.debug("Waiting for claim.")
            ready = True
            for module, event in self.claimedResponses.iteritems():
                if event.isSet():
                    if (not module.claimed) and \
                            not (module in self.unclaimedModules):
                        self.logger.warning("Could not claim %s",
                                            module._name)
                        self.logger.debug("Module instance: %s",
                                          module)
                        self.unclaimedModules.append(module)
                else:
                    ready = False

            if ready:
                self.logger.info("All modules responded to claim.")
                self.logger.info("Unclaimed: %s", self.unclaimedModules)
                if not self.unclaimedModules:
                    self.logger.info("Successfully claimed all modules.")
                    self.claimed = True
                    self.claimEvent.set()
                    self.claiming = False
                else:
                    self.logger.debug("Could not claim the following "
                                      "modules' hardware Resources: "
                                      "%s", self.unclaimedModules)
                    self.claimed = False
                    self._releaseAfterUnsuccesfulClaim()
            else:
                self.responseCounter += 1
                self.logger.debug("Claim responseCounter: %d",
                                  self.responseCounter)
                if self.responseCounter > 50:
                    unresponsiveModules = []
                    for module in self.claimedResponses:
                        if not event.isSet():
                            unresponsiveModules.append(module)
                            event.set()  # signal the module to stop trying
                    self.logger.error("Took longer than 5 seconds to claim "
                                      "resources. Still waiting for: %s",
                                      unresponsiveModules)
                    self._releaseAfterUnsuccesfulClaim()
                else:
                    self.logger.debug("Set timer for _waitForClaim.")
                    QtCore.QTimer.singleShot(100, self._waitForClaim)
        else:
            self.logger.warning("Resource claim was aborted.")
            for event in self.claimedResponses.itervalues():
                event.set()  # signal the modules to stop trying
            self.logger.info("Now trying to release Resources")
            self.claimEvent.set()
            self.claiming = False
            event = self.release()

    def release(self):
        self.logger.info("Attempting to release hardware resources.")
        if self.claiming:
            self.logger.warning("Already claiming/releasing Resources.")
            if self.releaseEvent.isSet():
                # we are likely claiming, so the caller can go on with
                # their work and will fail later
                fakeReleaseEvent = threading.Event()
                fakeReleaseEvent.set()
                self.remoteReleaseRequested = False
                return fakeReleaseEvent
            else:
                # we are releasing, so the caller might as well wait
                return self.releaseEvent
        else:
            self.logger.debug("Clearing events and variables.")
            if not self.claimed:
                self.logger.warning("Attempting to release resources "
                                    "even though not all resources are "
                                    "currently claimed.")
            self.claiming = True
            self.releaseEvent.clear()
            self.remoteReleaseRequested = False

            self.logger.debug("Requesting releasedEvents.")
            self.releasedEvents = {}
            for module in self.modules.itervalues():
                self.releasedEvents[module] = module.releaseResources()
            self.responseCounter = 0
            self.logger.debug("Starting timer for _waitForRelease.")
            QtCore.QTimer.singleShot(100, self._waitForRelease)
            return self.releaseEvent

    def _waitForRelease(self):
        if self.claiming:
            ready = True
            for module, event in self.releasedEvents.iteritems():
                if not event.isSet():
                    ready = False
            if ready:
                self.logger.info("All modules responded to release request.")
                self.claimed = False
                self.releaseEvent.set()
                self.claiming = False
                self.logger.debug("Released resources.")
            else:
                self.responseCounter =+ 1
                self.logger.debug("Release responseCounter: %d",
                                  self.responseCounter)
                if self.responseCounter > 50:
                    unresponsiveModules = []
                    for module in self.claimedResponses:
                        if not event.isSet():
                            unresponsiveModules.append(module)
                            event.set()  # signal the module to stop trying
                    self.logger.error("Took longer than 5 seconds to release "
                                      "resources. Still waiting for: %s",
                                      unresponsiveModules)
                    self.releaseEvent.set()  # unfreeze the calling module
                    self.claimed = False  # consistency
                    self.claiming = False
                    self.logger.debug("Signalled released resources.")
                else:
                    self.logger.debug("Starting timer for _waitForRelease.")
                    QtCore.QTimer.singleShot(100, self._waitForRelease)
        else:
            self.logger.error("Resource release was aborted. This should never "
                              "happen and points to a deeper issue.")
            for event in self.releasedEvents.itervalues():
                event.set()  # signal the modules to stop trying

    def _releaseAfterUnsuccesfulClaim(self):
        self.logger.info("Now trying to release Resources")
        self.claimEvent.set()
        self.claiming = False
        event = self.release()
