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

import net as ownet
import core
import json


class VNextServer(object):
    def __init__(self, address, users):
        self.address = address
        self.users = users


class VMessUser(object):

    def __init__(self, id=None, email=None):
        self.id = id
        self.email = email

    def to_user(self):
        return core.User(core.ID(self.id))


class VMessInboundConfig(object):

    def __init__(self, allowed_clients):
        self.allowed_clients = allowed_clients


def load_inbound_config(cfg):
    cfg_dict = json.loads(cfg)
    # TODO: user email is null now.
    allowed_clients = [VMessUser(user['id']) for user in cfg_dict['clients']]
    return VMessInboundConfig(allowed_clients)


class VNextConfig(object):
    def __init__(self, address, port, users):
        self.address = address
        self.port = port
        self.users = users

    def to_vnext_server(self):
        users = [user.to_user() for user in self.users]
        owaddr = ownet.Address(self.address, self.port)
        return VNextServer(owaddr, users)


class VMessOutboundConfig(object):
    def __init__(self, vnextlist):
        self.vnext_list = vnextlist


def load_outbound_config(cfg):
    cfg_dict = json.loads(cfg)
    vnextlist = []
    for vnext in cfg_dict['vnext']:
        users = [VMessUser(user['id']) for user in vnext['users']]
        vnextlist.append(VNextConfig(vnext['address'], vnext['port'], users))
    return VMessOutboundConfig(vnextlist)
