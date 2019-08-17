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

from .config import *
import net_io as owio
from net_io import vmess as vmessio
from owmath import mrand
import owhash
import core
from Crypto import Random
from hashlib import md5
import threading
import socket
import random
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('VMessOut')


class VMessOutboundHandler(object):
    def __init__(self, point, dest, vnext_list):
        self.point = point
        self.dest = dest
        self.vnext_list = vnext_list

    def pick_vnext(self):
        try:
            vnext = random.choice(self.vnext_list)
            vnextuser = random.choice(vnext.users)
            return vnext.address, vnextuser
        except IndexError:
            logger.error('The vnext or users is null!')
            return None, None

    def start(self, way):
        vnext_addr, vnext_user = self.pick_vnext()
        if not vnext_addr or not vnext_user:
            return

        r = vmessio.VMessRequest()
        r.version = vmessio.VERSION
        # r.user_id = core.ID('ad937d9d-6e23-4a5a-ba23-bce5092a7c51')
        r.user_id = vnext_user.id
        r.command = (0x01).to_bytes(1, 'big')
        r.address = self.dest
        r.iv = Random.get_random_bytes(16)
        r.key = Random.get_random_bytes(16)
        r.header = Random.get_random_bytes(4)

        # t = threading.Thread(target=self.start_communicate, args=(r, way, vnext_addr), name='VMessIOThread')
        # t.start()
        # t.join()
        #
        self.start_communicate(r, way, vnext_addr)
        logger.debug('VMessIOThread closed!')

    def start_communicate(self, request, way, dest):
        if not dest.is_ipv6():
            address_familly = socket.AF_INET
        else:
            address_familly = socket.AF_INET6
        conn = socket.socket(address_familly, socket.SOCK_STREAM)
        conn.connect(dest.sock_address)
        ipt_queue = way.outbound_input()
        opt_queue = way.outbound_output()

        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # tasks = [self.handle_request(request, way), self.handle_response(request, way)]
        # loop.run_until_complete(asyncio.wait(tasks))
        # logger.debug('loop_finish!!')
        # loop.close()
        #

        t1 = threading.Thread(target=self.handle_request, args=(conn, request, ipt_queue), name='VMessOutHandleRequestThread')
        t2 = threading.Thread(target=self.handle_response, args=(conn, request, opt_queue), name='VMessOutHandleResponseThread')
        t1.start()
        t2.start()
        # t1.join()
        # t2.join()

        return

    def handle_request(self, conn, request, ipt_q):
        encryptor = owio.CryptionWriter(request.key, request.iv, conn)

        buf, err = request.to_bytes(owhash.TimeHash(), mrand.generate_random_int64_in_range)
        if err is not None:
            logger.error(err)
            return

        try:
            conn.sendall(buf)
            logger.debug('Request Done!')
            ownet.queue_to_writer(ipt_q, encryptor)
        except socket.error as e:
            # logger.error('The socket may be hanpend error during handling request!')
            logger.error('Handle response: %s' % e)

    def handle_response(self, conn, request, opt_q):
        response_key = md5(request.key).digest()
        response_iv = md5(request.iv).digest()
        logger.debug('ResponseKey: %s  ResponseIV: %s' % (response_key.hex(), response_iv.hex()))
        decryptor = owio.CryptionReader(response_key, response_iv, conn)

        auth_header = decryptor.recv(4)
        logger.debug(auth_header.hex())
        if auth_header != request.header:
            logger.warning('Unexepcted response header. The connection is probably hijacked.')
            return
        ownet.reader_to_queue(opt_q, decryptor)


class VMessOutBoundHandlerFactory(core.OutboundConnectionHandlerFactory):
    def create(self, point, config, dest):
        cfg = load_outbound_config(config)
        servers = []
        for server in cfg.vnext_list:
            servers.append(server.to_vnext_server())
        return VMessOutboundHandler(point, dest, servers)
