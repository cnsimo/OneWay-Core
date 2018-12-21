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


import json


class User(object):
    '''User is the user account that is used for connection to a Point'''
    def __init__(self, id):
        self.id = id


class ConnectionConfig(object):
    def __init__(self, protocol, file):
        self.protocol = protocol
        self.file = file


class Config(object):
    '''Config is the config fo Point server.'''
    def __init__(self, port, inbound_config, outbound_config):
        self.port = port                       # port of this Point server
        self.inbound_config = ConnectionConfig(inbound_config['protocol'], inbound_config['file'])
        self.outbound_config = ConnectionConfig(outbound_config['protocol'], outbound_config['file'])


def load_config(cfg):
    cfg_dict = json.loads(cfg)
    return Config(cfg_dict['port'], cfg_dict['inbound'], cfg_dict['outbound'])
