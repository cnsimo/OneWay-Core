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

import socket
import queue
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('NetTransport')

BUFFER_SIZE = 32 * 1024


def get_byte_from(data):
    yield from data


def reader_to_queue(q, reader):
    try:
        while True:
            data = reader.recv(BUFFER_SIZE)
            logger.debug(data.hex())
            if len(data) > 0:
                for byte_data in get_byte_from(data):
                    q.put(byte_data)
            else:
                # q.put('Done!')
                logger.debug(reader.__class__.__name__ + '-->' + q.__class__.__name__ + ' [Done!]')
                return
    except socket.error:
        # q.put('Done!')
        logger.debug(reader.__class__.__name__ + '-->' + q.__class__.__name__ + ' [error!]')
        return


def queue_to_writer(q, writer):
    try:
        while True:
            data = q.get(timeout=10)
            logger.debug(bytes([data]).hex())
            # if isinstance(data, str):
            #     return
            if len(str(data)) <= 0: return
            writer.sendall(bytes([data]))
            # n = writer.sendall(bytes([data]))
            # if n <= 0: return
    except queue.Empty:
        logger.debug(q.__class__.__name__ + '-->' + writer.__class__.__name__ + ' [Done!]')
        return
    except socket.error:
        logger.debug(q.__class__.__name__ + '-->' + writer.__class__.__name__ + ' [error!]')
        return
