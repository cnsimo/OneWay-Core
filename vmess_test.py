from Crypto.Cipher import AES
import json

# def trans(s):
#         # return "b'%s'" % ''.join('\\x%.2x' % x for x in s)
#         return str([i for i in s])

BS = 16

padd = lambda s: s + (BS-len(s)%BS) * (0).to_bytes(1, 'big') if len(s)%BS else s


def main():
    key = b'\xf3\xcb\x15\x4e\x0e\x79\x55\x71\xcc\xd5\x81\xb0\x5e\x6a\x47\x3b'
    iv = b'\xe5\xc9\x2b\x6e\x74\x65\xe8\xb1\x9e\x81\x1c\xa8\xf6\xaa\xd0\xbc'
    text = b'\x4b\x22\x4e\xe2\xb5\xf5\xf2\x6e\x3f\x59\x75\x1b\x1d\x1c\x98\x64\x3e\x68\x19\xc9\x35\x0b\xda\xc1\x76\xb9\x42\xef\xd2\xb2\xd8'
    ciphertext = b'\x05\xd9\xce\x58\x0b\x4c\x1c\x4f\x01\xd6\xc0\xea\x1c\x9c\x07\x00\xff\xbf\xa6\xa7\x02\x35\x40\x1a\x67\xb3\xfa\x81\x91\xef\x2d'

    decryptor = AES.new(key, mode=AES.MODE_CFB, IV=iv, segment_size=128)
    plaintext = decryptor.decrypt(padd(ciphertext))

    # key :           aes中key
    # iv :            cfb中初始向量iv
    # ciphertext :    加密内容
    # plaintext  :    解密内容

    print('kev:\t\t', key.hex())
    print('iv:\t\t', iv.hex())
    print('ciphertext:\t', ciphertext.hex())
    print('plaintext:\t', plaintext[:len(ciphertext)].hex())

if __name__ == '__main__':
    main()
