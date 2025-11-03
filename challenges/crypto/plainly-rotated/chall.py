#!/usr/bin/python3
import os
import random

from Crypto.Util.number import getPrime
from you_dont_have_this_file import flag

pad_length = random.randint(0, 64 - len(flag))
flag = os.urandom(pad_length) + flag + os.urandom(64 - len(flag) - pad_length)
mask = ~(-1 << 512)

def bitwise_rotated(msg, iterations):
    """
         1 rotation moves the 511th bit to 0 and shift everything left
         so 2^511 + 2^510 + 2^1 = 0b1100....0010 would become 2^0 + 2^511 + 2^2 = 0b100...0101
    """
    msg_int = int.from_bytes(msg, 'big')
    msg_int = ((msg_int >> (512 - iterations)) | (msg_int << iterations)) & mask
    return msg_int

def encrypt(m, e, n):
    """
        Typical RSA encryption
    """
    return pow(m, e, n)


p, q = getPrime(512), getPrime(512)
e = 65537
n = p * q
print('n =', n)
print('e =', e)
while True:
    print('Rotate the plaintext as much as you want!')
    iterations = int(input('> '))
    unencrypted = bitwise_rotated(flag, iterations)
    encrypted = encrypt(unencrypted, e, n)
    print(encrypted)
