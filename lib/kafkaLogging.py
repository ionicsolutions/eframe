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
"""Kafka logging for EFrame.

Based on
https://stackoverflow.com/questions/21102293/how-to-write-to-kafka-from-python-logging-module
"""
import logging
from kafka import KafkaProducer


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, servers, topic):
        logging.Handler.__init__(self)
        self.topic = topic
        self.logger = logging.getLogger("KafkaLoggingHandler")
        try:
            self.producer = KafkaProducer(bootstrap_servers=servers)
        except Exception as e:
            self.active = False
            self.logger.warning("Could not establish connection to server.")
        else:
            self.active = True

    def emit(self, record):
        if record.name == 'kafka':
            return  # drop kafka logging to avoid infinite recursion

        if self.active:
            try:
                msg = self.format(record)
                self.producer.send(topic=self.topic, value=msg)
            except Exception as e:
                self.active = False
                self.logger.error("Sending record failed. Stopping.")

    def close(self):
        try:
            self.producer.close()
        except AttributeError:
            pass
        logging.Handler.close(self)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("KafkaTesk")
    logger.setLevel(logging.DEBUG)
    k = KafkaLoggingHandler(["192.168.32.9:9092"], "ioncavity")
    logger.addHandler(k)
    logger.info("I am here and you are not.")
    k.close()
    print("Closed")
    
    
    
    
