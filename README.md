# EFrame

[Kilian W. Kluge](http://github.com/ionicsolutions), Tim Ballance

`EFrame` is a GUI for the control of ion trap and other experimental physics setups which are operated using many standalone components accessed via ethernet.

## Should I use EFrame for my experiment?

You probably shouldn't. `EFrame` was written for a specific set of experiments in a unique lab environment. While modules usually allow to add interfaces for additional hardware, you should probably consider designing your own control interface which meets your specific needs. If you are starting an entirely new experiment or are looking to upgrade to a more advanced control system, we recommend checking out [ARTIQ](https://m-labs.hk/artiq/), a professionally maintained open-source control infrastructure which is used in many of the best ion trapping labs in the world and is likely to stay for a long time.

You are of course welcome to re-use code or borrow ideas from `EFrame`. We specifically recommend to check out the following parts and modules, which we believe are good solutions to commonly encountered problems:

- `remoteControl`: XML-RPC based remote interface gives access to the *state* instance and therefore allows scripts to call module methods the same way modules call each other
- `tracker`: Execute small scripts when signals are emitted by modules (can be used to generate log entries or relay control messages to other control software)

## Requirements

`EFrame` itself runs on Python 2.7 and requires [PyQt4](http://pyqt.sourceforge.net/Docs/PyQt4/installation.html), [kafka-python](https://pypi.python.org/pypi/kafka-python), and [influxdb](https://pypi.python.org/pypi/influxdb). Many modules make use of the [requests](https://pypi.python.org/pypi/requests) module for HTTP calls (sometimes through the `PyHWI` package which is not provided).

Other dependencies are module-specific and sometimes include proprietary drivers.
