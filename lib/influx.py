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
import influxdb


class Influx(object):
    def __init__(self):
        self.influx = influxdb.InfluxDBClient(database="eframe")

    def message(self, title, text, type_):
        """Write a message which can be displayed as an event in Grafana."""
        message = {"measurement": "event",
                   "fields": {"title": title, "message": text},
                   "tags": {"type": type_}
                   }
        self.influx.write_points([message])

    def measurement(self, measurement, value, unit, module, tags=None):
        """Write a single measurement point.

        If more than the standard tags *unit* and *module* are needed,
        provide a *tags* dictionary with the additional entries.
        """
        message = {"measurement": measurement,
                   "fields": {"value": value},
                   "tags": {"unit": unit, "module": module}}
        if tags is not None:
            message["tags"].update(tags)
        self.influx.write_points([message])

    def custom(self, measurement, fields, tags, module):
        """Write a custom data point.

        *fields* and *tags* are the dictionaries for the corresponding
        InfluxDB entries.
        """
        message = {"measurement": measurement,
                   "fields": fields,
                   "tags": tags}
        message["tags"]["module"] = module
        self.influx.write_points([message])
