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


from config import *
from net.address import Address
import net_io.socks as socksio
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import socket
import select
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

logger = logging.getLogger('Socks5Server')

PORT = 1088


class Socks5Server(ThreadingMixIn, TCPServer):

    def __init__(self, config, server_address, request_handler):
        self.config = config
        TCPServer.__init__(self, server_address, request_handler)


class Socks5RequestHandler(StreamRequestHandler):
    """A class for socks5 server"""

    def handle_tcp(self, local, remote):
        fdset = [local, remote]
        try:
            while fdset:
                r, w, e = select.select(fdset, [], [])
                if local in r:
                    if remote.send(local.recv(4096)) <= 0:
                        logger.debug('local -> remote completed.')
                        break
                if remote in r:
                    if local.send(remote.recv(4096)) <= 0:
                        logger.debug('remote -> local completed.')
                        break
        finally:
            remote.close()

    def handle(self):
        logger.info('Socks connection from %s' % Address(*self.client_address))
        try:
            client = self.connection


            auth_request, err = socksio.read_socks5_authentication_request(client)
            if err is not None:
                logger.error(err)
                self.server.close_request(client)
                return
            if(auth_request.version != socksio.SOCKS_V5):
                logger.waring('Only support socks version 5!!')
                self.server.close_request(client)
                return
            expected_auth_method = socksio.AUTH_NOT_REQUIRED
            if self.server.config.auth_method == JSON_AUTH_METHOD_USER_PASS:
                expected_auth_method = socksio.AUTH_USER_PASS
            if not auth_request.has_auth_method(expected_auth_method):
                auth_response = socksio.Socks5AuthenticationResponse(socksio.AUTH_NO_MATCHING_METHOD)
                socksio.write_socks5_authentication_response(client, auth_response)
                return
            auth_response = socksio.Socks5AuthenticationResponse(expected_auth_method)
            socksio.write_socks5_authentication_response(client, auth_response)
            if self.server.config.auth_method == JSON_AUTH_METHOD_USER_PASS:
                user_pass_request, err = socksio.read_user_pass_request(client)
                if err is not None:
                    logger.error(err)
                    self.server.close_request(client)
                    return
                user_pass_response = socksio.Socks5UserPassResponse(0x00)
                if not user_pass_request.is_valid(self.server.config.username, self.server.config.password):
                    user_pass_request = socksio.Socks5UserPassResponse(0xff)
                    logger.error('Account authentication failed!!')
                socksio.write_user_pass_response(client, user_pass_request)


            request, err = socksio.read_request(client)
            if err is not None:
                logger.error(err)
                self.server.close_request(client)
                return
            r_addr = Address(request.dst_addr, request.dst_port)
            response = socksio.Socks5Response()
            try:
                # TODO: Distinguish the domain is ipv6 or ipv4
                if request.command == socksio.CMD_CONNECT:
                    if request.addr_type != Address.ADDR_TYPE_IPv6:
                        address_familly = socket.AF_INET
                    else:
                        address_familly = socket.AF_INET6
                    remote = socket.socket(address_familly, socket.SOCK_STREAM)
                    remote.connect(r_addr.sock_address)
                    l_addr = Address(*remote.getsockname())
                    response.reply = socksio.REPLY_SUCCESS
                    response.bnd_addr = l_addr
                    response.addr_type = l_addr.addr_type
                    logger.info('Connected to %s' % r_addr)
                else:
                    response.reply = socksio.REPLY_COMMAND_NOT_SUPPORTED
                    logger.warning('No supported CMD.')
            except socket.error:
                response.reply = socksio.REPLY_CONNECTION_REFUSED
                logger.error('Remote connection refused')
            except TypeError:
                response.reply = socksio.REPLY_ADDRESS_TYPE_NOT_SUPPORTED
                logger.error('Some domain for ipv6 is not supported!')
            finally:
                socksio.write_response(client, response)

            if response.reply == socksio.REPLY_SUCCESS and request.command == socksio.CMD_CONNECT:
                logger.debug('Into handle_tcp function.')
                self.handle_tcp(client, remote)
        except socket.error:
            logger.error('Local socket error!!')
            self.server.close_request(client)
        except ConnectionAbortedError:
            logger.error('The connection is terminated!!')
            self.server.close_request(client)


def main():
    logger.info("Started the server from %s ..." % PORT)
    with open(r'../../config/in_socks.json', 'r') as f:
        config = load_config(f.read())
        with Socks5Server(config, ('', PORT), Socks5RequestHandler) as server:
            server.allow_reuse_address = True
            server.serve_forever()


if __name__ == '__main__':
    main()
