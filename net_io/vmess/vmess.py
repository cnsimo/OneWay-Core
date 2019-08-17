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


from owmath import mint
from owmath import mrand
import net as ownet
import net_io as owio
import core
import owhash
import socket
import time
import struct
import random
from Crypto import Random
from Crypto.Cipher import AES
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('VMessIO')


VERSION = 0x01
BLOCK_SIZE = 16

ADDR_TYPE_IPV4 = 0x01
ADDR_TYPE_DOMAIN = 0x02
ADDR_TYPE_IPV6 = 0x03


class VMessRequest(object):
    '''
    VMessRequest implements the request message of VMess protocol. It only contains
    the header of a request message. The data part will be handled by conection
    handler directly, in favor of data streaming.
    '''
    def __init__(self, user_id=None, version=None):
        self.version = version
        self.user_id = user_id

    def to_bytes(self, id_hash, random_range_int64):
        buffer = b''
        err = None
        counter = random_range_int64(int(time.time()), 30)
        user_hash = id_hash.hash(self.user_id.bytes, counter)

        logger.debug('Writing userhash: %s' % user_hash.hex())
        buffer += user_hash

        encrypto_begin = len(buffer)
        random_length = random.SystemRandom().randint(1, 32)
        random_content = Random.get_random_bytes(random_length)
        random_length, err = mint.to_bytes(random_length, 'big')
        if err is not None:
            return None, err
        logger.debug('RandomLength: %s, RandomContent: %s' % (random_length.hex(), random_content.hex()))
        buffer += random_length
        buffer += random_content

        ver, err = mint.to_bytes(self.version, 'big')
        if err is not None:
            return None, err
        logger.debug('ver: %s' % ver.hex())
        buffer += ver
        buffer += self.iv
        buffer += self.key
        buffer += self.header
        buffer += self.command
        buffer += self.address.vmess_packed

        padding_length = random.SystemRandom().randint(1, 32)
        padding_buffer = Random.get_random_bytes(padding_length)
        padding_length, err = mint.to_bytes(padding_length, 'big')
        if err is not None:
            return None, err
        buffer += padding_length
        buffer += padding_buffer
        encrypto_end = len(buffer)

        logger.debug('ID: %s  KEY: %s  IV: %s' % (self.user_id.string, self.user_id.cmd_key.hex(), owhash.Int64Hash(counter).hex()))
        # BS = AES.block_size
        BS = 1
        padding = lambda s: s + (BS-len(s)%BS) * (0).to_bytes(1, 'big') if len(s)%BS else s
        aes_cipher = AES.new(self.user_id.cmd_key, mode=AES.MODE_CFB, IV=owhash.Int64Hash(counter), segment_size=8)
        buffer_encrypted = aes_cipher.encrypt(padding(buffer[encrypto_begin:encrypto_end]))
        return buffer[:encrypto_begin]+buffer_encrypted[:(encrypto_end-encrypto_begin)], err


ERROR_INVALIED_USER = "Invalid User"
ERROR_INVALIED_VERSION = "Invalid Version"


class VMessRequestReader(object):
    def __init__(self, user_set):
        self.user_set = user_set

    def read(self, conn):
        user_hash = conn.recv(core.ID_BYTES_LEN)
        logger.debug('Read user hash: %s' % user_hash.hex())

        user_id, time_sec = self.user_set.get_user(user_hash)
        if not user_id or not time_sec:
            return None, ERROR_INVALIED_USER

        decryptor = owio.CryptionReader(user_id.cmd_key, owhash.Int64Hash(time_sec), conn)
        logger.debug('ID: %s  KEY: %s  IV: %s' % (user_id.string, user_id.cmd_key.hex(), owhash.Int64Hash(time_sec).hex()))

        random_length = struct.unpack('>B', decryptor.recv(1))[0]
        if random_length <= 0 or random_length > 32:
            return None, "Unexpected random length %s" % random_length
        random_content = decryptor.recv(random_length)
        logger.debug('RandomLength: %s, RandomContent: %s' % (random_length, random_content.hex()))
        version = struct.unpack('>B', decryptor.recv(1))[0]
        print(version)
        request = VMessRequest(user_id, version)
        if request.version != VERSION:
            return None, ERROR_INVALIED_VERSION

        request.iv = decryptor.recv(16)
        request.key = decryptor.recv(16)
        request.header = decryptor.recv(4)
        request.command = struct.unpack('>B', decryptor.recv(1))[0]
        port = struct.unpack('>H', decryptor.recv(2))[0]
        addr_type = struct.unpack('>B', decryptor.recv(1))[0]
        if addr_type == ADDR_TYPE_IPV4:
            buf = decryptor.recv(4)
            dst_addr = socket.inet_ntop(socket.AF_INET, buf)
        elif addr_type == ADDR_TYPE_IPV6:
            buf = decryptor.recv(16)
            dst_addr = socket.inet_ntop(socket.AF_INET6, buf)
        elif ADDR_TYPE_DOMAIN:
            domain_len = struct.unpack('>B', decryptor.recv(1))[0]
            dst_addr = decryptor.recv(domain_len).decode()
        else:
            return None, "Unknown VMess address type: %s" % addr_type
        request.address = ownet.Address(dst_addr, port)

        padding_length = struct.unpack('>B', decryptor.recv(1))[0]
        if padding_length <= 0 or padding_length > 32:
            return None, "Unexpected padding length %s" % padding_length
        decryptor.recv(padding_length)
        return request, None


def main():
    r = VMessRequest()
    r.version = VERSION
    r.user_id = core.ID('ad937d9d-6e23-4a5a-ba23-bce5092a7c51')
    r.command = (0x01).to_bytes(1, 'big')
    r.address = ownet.Address('1.1.1.1', 9090)
    r.iv = Random.get_random_bytes(16)
    r.key = Random.get_random_bytes(16)
    r.header = Random.get_random_bytes(4)
    buf, err = r.to_bytes(owhash.TimeHash(), mrand.generate_random_int64_in_range)
    if err is not None:
        print(err)
        return
    print(buf)
