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
import select
import socket
import threading
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('Freedom')


class FreedomConnection(object):

    def __init__(self, dest):
        self.dest = dest

    # def start(self, way):
    #     if not self.dest.is_ipv6():
    #         address_familly = socket.AF_INET
    #     else:
    #         address_familly = socket.AF_INET6
    #     remote = socket.socket(address_familly, socket.SOCK_STREAM)
    #     remote.connect(self.dest.sock_address)
    #     way.out_way = remote
    #     fdset = [way.in_way, way.out_way]
    #     try:
    #         while fdset:
    #             r, w, e = select.select(fdset, [], [])
    #             if way.in_way in r:
    #                 if way.out_way.send(way.in_way.recv(4096)) <= 0:
    #                     break
    #             if way.out_way in r:
    #                 if way.in_way.send(way.out_way.recv(4096)) <= 0:
    #                     break
    #     finally:
    #         way.out_way.close()

    def start(self, way):
        ipt_queue = way.outbound_input()
        opt_queue = way.outbound_output()
        if not self.dest.is_ipv6():
            address_familly = socket.AF_INET
        else:
            address_familly = socket.AF_INET6
        conn = socket.socket(address_familly, socket.SOCK_STREAM)
        conn.connect(self.dest.sock_address)

        logger.info("Sending outbound tcp: %s" % str(self.dest))

        ipt_thread = threading.Thread(target=self.dump_input, args=(conn, ipt_queue), name="FreedomDumpInputThread")
        opt_thread = threading.Thread(target=self.dump_output, args=(conn, opt_queue), name="FreedomDumpOutputThread")
        ipt_thread.start()
        opt_thread.start()

        return

    def dump_input(self, conn, ipt_q):
        ownet.queue_to_writer(ipt_q, conn)
        return

    def dump_output(self, conn, opt_q):
        ownet.reader_to_queue(opt_q, conn)
        return
