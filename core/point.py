#!/usr/bin/env python

# Copyright 2018 Techliu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from .way import Way
import net as ownet
from abc import ABCMeta, abstractmethod
from collections import defaultdict
import socket
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('Point')


inbound_factories = defaultdict(lambda: None)
outbound_factories = defaultdict(lambda: None)


def register_inbound_connection_handler_factory(name, factory):
    # TODO check name
    inbound_factories[name] = factory
    return


def register_outbound_connection_handler_factory(name, factory):
    # TODO check name
    outbound_factories[name] = factory
    return


class Point(object):
    '''Point is an single server in OneWay system.'''

    def __init__(self, config):
        '''Initialize a new Point by given configuration'''
        self.port = config.port
        ich_factory = inbound_factories[config.inbound_config.protocol]
        if not ich_factory:
            logger.error('Unknown inbound connection handler factory %s' % config.inbound_config.protocol)
            return
        self.ich_factory = ich_factory
        if len(config.inbound_config.file) > 0:
            try:
                with open(config.inbound_config.file, 'r') as ich_config:
                    self.ich_config = ich_config.read()
            except FileNotFoundError:
                logger.error('Unable to read config file %s' % config.inbound_config.file)
                return
        else:
            self.ich_config = None

        och_factory = outbound_factories[config.outbound_config.protocol]
        if not och_factory:
            logger.error('Unknown outbound connection handler factory %s' % config.outbound_config.protocol)
            return
        self.och_factory = och_factory
        if len(config.outbound_config.file) > 0:
            try:
                with open(config.outbound_config.file, 'r') as och_config:
                    self.och_config = och_config.read()
            except FileNotFoundError:
                logger.error('Unable to read config file %s' % config.outbound_config.file)
                return
        else:
            self.och_config = None

    def start(self):
        '''The function starts the Point server'''
        if self.port <= 0:
            logger.error('Invaild port %d' % self.port)
            return
        inbound_connection_handler = self.ich_factory.create(self, self.ich_config)
        with inbound_connection_handler as server:
            server.allow_reuse_address = True
            server.serve_forever()

    def new_inbound_connection_accepted(self, dest):
        way = Way()
        och = self.och_factory.create(self, self.och_config, dest)
        och.start(way)
        return way


class InboundConnectionHandlerFactory(metaclass=ABCMeta):
    @abstractmethod
    def create(self, point, config):
        pass


class OutboundConnectionHandlerFactory(metaclass=ABCMeta):
    @abstractmethod
    def create(self, point, config, dest):
        pass
