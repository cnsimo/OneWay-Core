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

from hashlib import md5
import binascii
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('core')


def UUID_to_ID(uuid):
    byte_groups = [8, 4, 4, 4, 12]
    err = "invalid UUID string: %s" % uuid

    text = uuid.split('-')
    if len(uuid) < 32 or len(text) != len(byte_groups):
        return None, err

    v = []

    for i, j in enumerate(range(len(byte_groups))):
        if len(text[i]) != byte_groups[j]:
            return None, err
        v.append(binascii.a2b_hex(text[i]))
    return b''.join(v), None


ID_BYTES_LEN = 16


class ID(object):
    '''The ID of en entity, in the form of an UUID.'''

    def __init__(self, id):
        id_bytes, err = UUID_to_ID(id)
        self.string = None
        self.bytes = None
        self.cmd_key = None
        if err is not None:
            logger.error(err)
            return
        md5hash = md5()
        md5hash.update(id_bytes)
        md5hash.update('c48619fe-8f02-49e0-b9e9-edf763e17e21'.encode('utf-8'))
        self.cmd_key = md5hash.digest()
        self.string = id
        self.bytes = id_bytes
