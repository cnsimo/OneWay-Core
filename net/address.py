import ipaddress
import struct


class Address(object):
    ADDR_TYPE_IPv4 = 0x01
    ADDR_TYPE_IPv6 = 0x04
    ADDR_TYPE_DOMAIN = 0x03

    def __init__(self, addr, port):
        # TODO: 检查域名port的合法性
        try:
            self.addr = ipaddress.ip_address(addr)
            self.addr_type = self.ADDR_TYPE_IPv4 if self.addr.version == 4 else self.ADDR_TYPE_IPv6
        except ValueError:
            self.addr = addr
            self.addr_type = self.ADDR_TYPE_DOMAIN
        finally:
            self.port = int(port)
    # TODO: packed mode, em 1,2,3 for type,addr,port
    @property
    def socks_packed(self):
        if isinstance(self.addr, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return self.addr_type.to_bytes(1, 'big') + self.addr.packed + struct.pack('>H', self.port)
        else:
            return self.addr_type.to_bytes(1, 'big') + struct.pack('>B', len(self.addr)) + (self.addr if isinstance(self.addr, bytes) else self.addr.encode()) + struct.pack('>H', self.port)

    @property
    def vmess_packed(self):
        if isinstance(self.addr, ipaddress.IPv4Address):
            return struct.pack('>H', self.port) + 0x01.to_bytes(1, 'big') + self.addr.packed
        elif isinstance(self.addr, ipaddress.IPv6Address):
            return struct.pack('>H', self.port) + 0x03.to_bytes(1, 'big') + self.addr.packed
        else:
            return struct.pack('>H', self.port) + 0x02.to_bytes(1, 'big') + struct.pack('>B', len(self.addr)) + (self.addr if isinstance(self.addr, bytes) else self.addr.encode())

    @property
    def sock_address(self):
        return str(self.addr), self.port

    def is_ipv4(self):
        return self.addr_type == Address.ADDR_TYPE_IPv4

    def is_ipv6(self):
        return self.addr_type == Address.ADDR_TYPE_IPv6

    def is_domain(self):
        return self.addr_type == Address.ADDR_TYPE_DOMAIN

    def __str__(self):
        return '[' + str(self.addr) + ']:' + str(self.port) if self.is_ipv6() else str(self.addr) + ':' + str(self.port)


if __name__ == '__main__':
    baidu = Address(Address.ADDR_TYPE_DOMAIN, 'www.baidu.com', 80)
    myip = Address(Address.ADDR_TYPE_IPv4, '192.168.123.1', 22)
    myipv6 = Address(Address.ADDR_TYPE_IPv6, '::1', 23)

    print(baidu.is_domain())
    print(baidu.is_ipv4())
    print(myip.is_ipv4())
    print(myip.is_ipv6())
    print(myip)
    print(baidu)
    print(myipv6.is_ipv4())
    print(myipv6.is_ipv6())
    print(myipv6)
