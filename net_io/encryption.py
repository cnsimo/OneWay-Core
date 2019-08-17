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

from Crypto.Cipher import AES

BS = 1
# padding的意思是如果数据长度不是BS的整数倍则对其填充0
padding = lambda s: s + (BS-len(s)%BS) * (0).to_bytes(1, 'big') if len(s)%BS else s


class CryptionReader(object):
    def __init__(self, key, iv, reader):
        self.decryptor = AES.new(key, mode=AES.MODE_CFB, IV=iv, segment_size=8)
        self.reader = reader

    def recv(self, size):
        buf = self.reader.recv(size)
        return (self.decryptor.decrypt(padding(buf)))[:len(buf)]


class CryptionWriter(object):
    def __init__(self, key, iv, writer):
        self.encryptor = AES.new(key, mode=AES.MODE_CFB, IV=iv, segment_size=8)
        self.writer = writer

    def crypt(self, data):
        return (self.encryptor.encrypt(padding(data)))[:len(data)]

    def sendall(self, data):
        buf = self.crypt(data)
        return self.writer.sendall(buf)
