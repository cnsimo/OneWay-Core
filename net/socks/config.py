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


JSON_AUTH_METHOD_NO_AUTH = 'noauth'
JSON_AUTH_METHOD_USER_PASS = 'password'


class SocksConfig(object):

    def __init__(self, username='', password=''):
        self.username = username.decode() if isinstance(username, bytes) else username
        self.password = password.decode() if isinstance(password, bytes) else password
        if username == '':
            self.auth_method = 'noauth'
        else:
            self.auth_method = 'password'


def load_config(cfg):
    cfg_dict = json.loads(str(cfg))
    if cfg_dict['auth'] == JSON_AUTH_METHOD_NO_AUTH:
        return SocksConfig()
    return SocksConfig(username=cfg_dict['user'], password=cfg_dict['pass'])
