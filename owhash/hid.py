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

import binascii
import hmac
from abc import ABCMeta, abstractmethod


def int64_to_bytes(value):
    simple_byte_nums = []
    for offset in range(56, -1, -8):
        simple_byte_nums.append(value >> offset & 0xff)
    return bytes(simple_byte_nums)


class IdHash(metaclass=ABCMeta):
    @abstractmethod
    def hash(self, key, data):
        pass


class HMACHash(IdHash):
    def hash(self, key, data):
        return hmac.new(key, data, digestmod="MD5").digest()


class TimeHash(IdHash):
    def hash(self, key, counter):
        counter_bytes = int64_to_bytes(counter)
        base_hash = HMACHash()
        return base_hash.hash(key, counter_bytes)


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


__all__ = ['TimeHash', 'HMACHash', 'int64_to_bytes']

if __name__ == '__main__':
    def trans(s):
        return "b'%s'" % ''.join('\\x%.2x' % x for x in s)
    # print(trans(int64_to_bytes(1547024940)))

    id_bytes = UUID_to_ID('ad937d9d-6e23-4a5a-ba23-bce5092a7c51')[0]
    id_hase = TimeHash()
    hash = id_hase.hash(id_bytes, 1547024940)
    print(hash)
