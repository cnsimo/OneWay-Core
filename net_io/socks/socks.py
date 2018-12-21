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

from net.address import Address
import struct
import socket

SOCKS_V5 = 0x05

AUTH_NOT_REQUIRED = 0x00
AUTH_GSS_API = 0x01
AUTH_USER_PASS = 0x02
AUTH_NO_MATCHING_METHOD = 0xff


class Socks5AuthenticationRequest(object):

    def __init__(self, version=SOCKS_V5):
        self.version = version
        self.n_method = 0
        self.auth_methods = []

    def has_auth_method(self, method):
        if not self.n_method and self.n_method == 0: return False
        for i in range(self.n_method):
            if self.auth_methods[i] == method:
                return True
        return False


class Socks5AuthenticationResponse(object):

    def __init__(self, method=0x00, version=SOCKS_V5):
        self.version = version
        self.auth_method = method

    def to_bytes(self):
        return struct.pack('!BB', self.version, self.auth_method)


def read_socks5_authentication_request(sock):
    err = None
    data = sock.recv(2)
    if len(data) < 2:
        err = 'Expected 2 bytes read, but actaully %d bytes read' % len(data)
        return None, err
    auth5_request = Socks5AuthenticationRequest()
    auth5_request.version, auth5_request.n_method = struct.unpack('!BB', data)
    for i in range(auth5_request.n_method):
        auth5_request.auth_methods.append(ord(sock.recv(1)))

    return auth5_request, err
    pass


def write_socks5_authentication_response(sock, r):
    return sock.sendall(r.to_bytes())


AUTH_USER_PASS_V1 = 0x01


class Socks5UserPassRequest(object):

    def __init__(self, username='', password='', version=AUTH_USER_PASS_V1):
        self.version = version
        self.username = username.decode() if isinstance(username, bytes) else username
        self.password = password.decode() if isinstance(password, bytes) else password

    def is_valid(self, username, password):
        return self.username == username and self.password == password


class Socks5UserPassResponse(object):

    def __init__(self, status, version=AUTH_USER_PASS_V1):
        self.version = version
        self.status = status

    def to_bytes(self):
        return struct.pack('!BB', self.version, self.status)


def read_user_pass_request(sock):
    err = None
    req = Socks5UserPassRequest()
    data = sock.recv(2)
    if len(data) < 2:
        err = 'Expected 2 bytes read, but actaully %d bytes read' % len(data)
        return None, err
    req.version, n_username = struct.unpack('!BB', data)
    req.username = sock.recv(n_username).decode()
    n_password = ord(sock.recv(1))
    req.password = sock.recv(n_password).decode()
    return req, err


def write_user_pass_response(sock, r):
    return sock.sendall(r.to_bytes())


CMD_CONNECT = 0x01
CMD_BIND = 0x02
CMD_UDP_ASSOCIATE = 0x03


class Socks5Request(object):

    def __init__(self, command=CMD_CONNECT, addr_type=Address.ADDR_TYPE_IPv4, dst_addr=None, dst_port=None, version=SOCKS_V5):
        self.version = version
        self.command = command
        self.addr_type = addr_type
        self.dst_addr = dst_addr
        self.dst_port = dst_port

    def destination(self):
        return Address(self.addr_type, self.dst_addr, self.dst_port)


REPLY_SUCCESS = 0x00
REPLY_GENERAL_FAILURE = 0x01
REPLY_CONNECTION_NOT_ALLOWED = 0x02
REPLY_NETWORK_UNREACHABLE = 0x03
REPLY_HOST_UNREACHABLE = 0x04
REPLY_CONNECTION_REFUSED = 0x05
REPLY_TTL_EXPIRED = 0x06
REPLY_COMMAND_NOT_SUPPORTED = 0x07
REPLY_ADDRESS_TYPE_NOT_SUPPORTED = 0x08


class Socks5Response(object):

    def __init__(self, reply=REPLY_SUCCESS, addr_type=Address.ADDR_TYPE_IPv4, bnd_addr=None, version=SOCKS_V5):
        self.version = version
        self.reply = reply
        self.addr_type = addr_type
        self.bnd_addr = bnd_addr

    # def set_field(self, version, reply, addr_type, addr):
    #     self.version = version
    #     self.reply = reply
    #     self.addr_type = addr_type
    #     self.bnd_addr = addr

    def to_bytes(self):
        if self.reply != REPLY_SUCCESS:
            self.bnd_addr = Address('0.0.0.0', 0)
        reply = struct.pack('>BBBB', self.version, self.reply, 0x00, self.addr_type)
        reply += self.bnd_addr.packed
        return reply


def read_request(sock):
    err = None
    req = Socks5Request()
    data = sock.recv(4)
    if len(data) < 4:
        err = 'Expected 4 bytes read, but actaully %d bytes read' % len(data)
        return None, err
    req.version, req.command, _, req.addr_type = struct.unpack('>BBBB', data)
    if req.addr_type == Address.ADDR_TYPE_IPv4:
        data = sock.recv(4)
        if len(data) < 4:
            err = 'Unabled to read IPv4 address.'
            return None, err
        req.dst_addr = socket.inet_ntoa(data)
    elif req.addr_type == Address.ADDR_TYPE_IPv6:
        data = sock.recv(6)
        if len(data) < 6:
            err = 'Unabled to read IPv6 address'
            return None, err
        req.dst_addr = socket.inet_ntoa(data)
    elif req.addr_type == Address.ADDR_TYPE_DOMAIN:
        n_domain = ord(sock.recv(1))
        req.dst_addr = sock.recv(n_domain).decode()
        if len(req.dst_addr) < n_domain:
            err = 'Unable to read domain with %d bytes, expecting %d bytes' % (len(req.dst_addr), n_domain)
            return None, err
    else:
        err = 'Unexpected address type %d' % req.addr_type
        return None, err
    data = sock.recv(2)
    if len(data) < 2:
        err = 'Unabled to read port.'
        return None, err
    req.dst_port = struct.unpack('!H', data)[0]
    return req, err


def write_response(sock, r):
    return sock.sendall(r.to_bytes())


__all__ = ['SOCKS_V5', 'AUTH_NOT_REQUIRED', 'AUTH_USER_PASS', 'AUTH_GSS_API', 'AUTH_NO_MATCHING_METHOD', 'Socks5AuthenticationRequest', 'Socks5AuthenticationResponse', 'read_socks5_authentication_request', 'write_socks5_authentication_response', 'AUTH_USER_PASS_V1', 'Socks5UserPassRequest', 'Socks5UserPassResponse', 'read_user_pass_request', 'write_user_pass_response', 'CMD_CONNECT', 'CMD_BIND', 'CMD_UDP_ASSOCIATE', 'Socks5Request', 'REPLY_SUCCESS', 'REPLY_GENERAL_FAILURE', 'REPLY_CONNECTION_NOT_ALLOWED', 'REPLY_NETWORK_UNREACHABLE', 'REPLY_HOST_UNREACHABLE', 'REPLY_CONNECTION_REFUSED', 'REPLY_TTL_EXPIRED', 'REPLY_COMMAND_NOT_SUPPORTED', 'REPLY_ADDRESS_TYPE_NOT_SUPPORTED', 'Socks5Response', 'read_request', 'write_response']
