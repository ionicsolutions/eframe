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
**EFrame** is the main experimental control GUI for the IonCavity experiments.

*EFrame* was designed and written by Tim Ballance <t.g.ballance@gmail.com>
for the UVC experiment starting in 2014. Since the summer of 2016,
Kilian Kluge <kilian.kluge@gmail.com> is the lead developer.

**List of contributors:**
    * Tim Ballance (TB)
    * Ashwin Boddeti (AB)
    * Kilian Kluge (KK)
    * Max Zawierucha (MZ)
    * Pascal Kobel (PK)
    * You?

"""
# NOTE: With dc513a29d2be25f966a4ef1036159a7ae73da7a6, core.state.State
# which was previously defined here was moved to its own file.
# In the process, core.config.XMLConfig, core.resourceManager.Resources and
# core.storage.Storage were separated from core.state.State and also moved
# to their own files.
import argparse
import logging.handlers
import os
import subprocess

from config.kafka import setup
from core.mainWindow import MainWindow
from core.exceptions import InitErrorException
from lib.kafkaLogging import KafkaLoggingHandler

if __name__ == "__main__":
    # DEFAULTS
    expFile = 'config/IRC_Experiment.conf'  # which file to load
    logLevel = logging.INFO  # general log level
    chLevel = logging.INFO  # output to sys.stdout/sys.stderr
    fhLevel = logging.WARNING  # output to log files
    thLevel = logging.WARNING  # output to "Output" tab in EFrame GUI

    # HANDLE ARGUMENTS
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true", dest="debug",
                        help="show log messages of level DEBUG")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="only show log messages of level WARNING in "
                             "console and of level ERROR in GUI")
    parser.add_argument("-l", "--loglevel", type=str, dest="loglevel",
                        help="file loglevel, e.g. DEBUG or INFO")
    parser.add_argument("-t", "--thirdparty", action="store_true",
                        dest="thirdparty",
                        help="show all third-party module log messages")
    parser.add_argument(nargs=1, action="store", dest="file",
                        help="experiment file")
    parser.add_argument("-k", "--no-kafka", action="store_true",
                        dest="nokafka",
                        help="disable Kafka log handler")

    args = parser.parse_args()

    # LOG CONFIGURATION
    if args.debug:
        logLevel = logging.DEBUG
        chLevel = logging.DEBUG

    if args.quiet:
        chLevel = logging.WARNING
        shLevel = logging.ERROR

    if args.loglevel:
        requested = args.loglevel.upper()
        if requested == "DEBUG":
            fhLevel = logging.DEBUG
        elif requested == "INFO":
            fhLevel = logging.INFO
        elif requested == "WARNING":
            fhLevel = logging.WARNING

    # THIRD-PARTY LOGGER CONFIGURATION
    # Hide INFO level logging from the requests and urllib3 package,
    # otherwise we are flooded with HTTP connection messages
    if not args.thirdparty:
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    # VERIFY EXPERIMENT FILE
    if os.path.isfile(args.file[0]):
        expFile = args.file[0]
    else:
        raise InitErrorException("'%s' is not a file.",
                                 args.file[0])

    # STARTUP DISPLAY
    # get git revision hash to log and display
    gitRevision = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).strip()
    gitBranch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()

    print("")
    print("EEEEEE  FFFFFF RRRRR     AAA    MM   MM  EEEEEE")
    print("EE      FF     RR  RR   AA AA   MMMMMMM  EE    ")
    print("EEEEEE  FFFFF  RRRRR   AA   AA  MM M MM  EEEEEE")
    print("EE      FF     RR  RR  AAAAAAA  MM   MM  EE    ")
    print("EEEEEE  FF     RR  RR  AA   AA  MM   MM  EEEEEE")
    print("")
    print("Providing Ionic Solutions Since 2014.")
    print("")
    print("Git Branch: %s" % gitBranch)
    print("Git Revision: %s" % gitRevision)
    print("")
    print("Licensed under the Apache License, Version 2.0")
    print("(c) 2014-2017 Tim Ballance, Kilian Kluge, et al.")
    print("")

    # LOGGING CONFIGURATION
    # initialize root logger
    logger = logging.getLogger()
    logger.setLevel(logLevel)

    # common format for file and console logging
    # (format for QTextEdit widget is defined in QTextEditHandler)
    fmt = "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
    datefmt = "%Y/%m/%d - %H:%M:%S"

    # log to file 'EFrame.log', each of max. 100 KB length, keep 5 backups
    if not os.path.exists("log"):
        os.mkdir("log")
    fh = logging.handlers.RotatingFileHandler("log/EFrame.log", maxBytes=100000,
                                              backupCount=5)
    fh.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(fh)
    fh.setLevel(logging.INFO)  # Ensure that we log the git revision
    logger.info("Starting EFrame git revision %s (branch: %s).",
                gitRevision, gitBranch)
    logger.info("Configuration: %s", expFile)
    fh.setLevel(fhLevel)

    # when debugging, append additional information to each entry
    if logLevel == logging.DEBUG:
        fmt += " (@%(created)f in %(filename)s l. %(lineno)d)"

    # log to sys.stdout/sys.stderr
    ch = logging.StreamHandler()
    ch.setLevel(chLevel)
    ch.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(ch)

    # log to Kafka
    if not args.nokafka:
        kfmt = "EFrame %s: " % gitBranch
        kfmt += fmt
        kh = KafkaLoggingHandler(setup["servers"], setup["topic"])
        kh.setFormatter(logging.Formatter(fmt=kfmt, datefmt=datefmt))
        kh.setLevel(logging.WARNING)
        logger.addHandler(kh)

    # The log to the output tab in EFrame requires that we have
    # an existing QTextEdit widget available. We therefore wait
    # for EFrame's GUI to be initialized. No messages will be lost.

    # START MAIN WINDOW
    # if we are running on Windows, change the appUserModelID so the taskbar
    # does not group us with other Python programs
    if os.name == "nt":
        import ctypes

        myappid = "AQO.EFrame"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    logger.info("Starting EFrame main window")
    mw = MainWindow(rootLogger=logger, thLevel=thLevel, expFile=expFile)
