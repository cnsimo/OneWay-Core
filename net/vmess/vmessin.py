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
from net_io import vmess as vmessio
import net_io as owio
import core
import threading
import socket
from hashlib import md5
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('VMessIn')


class VMessRequestHandler(StreamRequestHandler):
    def handle(self):
        logger.info('VMess connection from %s' % ownet.Address(*self.client_address))
        client = self.connection
        try:
            reader = vmessio.VMessRequestReader(self.server.clients)
            request, err = reader.read(client)
            if err is not None:
                logger.error('Invalid request from %s: %s' % (ownet.Address(*self.client_address), err))
                self.server.close_request(client)
                return
            logger.debug('Received request for %s' % request.address)

            way = self.server.point.new_inbound_connection_accepted(request.address)
            ipt_queue = way.inbound_input()
            opt_queue = way.inbound_output()

            ipt_thread = threading.Thread(target=self.handle_input, args=(request, client, ipt_queue), name='VmessInHandleInputThread')
            ipt_thread.start()

            response_key = md5(request.key).digest()
            response_iv = md5(request.iv).digest()

            logger.debug('ResponseKey: %s  ResponseIV: %s' % (response_key.hex(), response_iv.hex()))

            auth_header = request.header
            encryptor = owio.CryptionWriter(response_key, response_iv, client)
            encryptor.sendall(auth_header)

            opt_thread = threading.Thread(target=self.handle_output, args=(encryptor, opt_queue), name='VmessInHandleOutputThread')
            opt_thread.start()

            ipt_thread.join()
            opt_thread.join()
        except socket.error:
            logger.error('Local socket error!!')
            self.server.close_request(client)
        except ConnectionAbortedError:
            logger.error('The connection is terminated!!')
            self.server.close_request(client)
        pass

    def handle_input(self, request, conn, ipt_q):
        request_reader = owio.CryptionReader(request.key, request.iv, conn)
        ownet.reader_to_queue(ipt_q, request_reader)

    def handle_output(self, conn, opt_q):
        ownet.queue_to_writer(opt_q, conn)

class VMessInboundHandler(ThreadingMixIn, TCPServer):
    def __init__(self, point, clients, server_address, request_handler=VMessRequestHandler):
        self.point = point
        self.clients = clients
        TCPServer.__init__(self, server_address, request_handler)
        pass


class VMessInboundHandlerFactory(core.InboundConnectionHandlerFactory):
    def create(self, point, config):
        cfg = load_inbound_config(config)
        allowed_clients = core.TimeUserSet()
        for client in cfg.allowed_clients:
            user = client.to_user()
            allowed_clients.add_user(user)
        return VMessInboundHandler(point, allowed_clients, ('', point.port))
