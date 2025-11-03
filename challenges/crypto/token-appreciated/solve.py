import json

from pwn import *
import itertools

p = process(['python3', 'chall.py'])
p.sendline(b'1')
password = '0000'
p.sendline(password.encode())
p.recvuntil(b'User ')
username = p.recvuntil(b' ').strip().decode()

unencrypted_token = json.dumps([username, password]).encode()
p.recvuntil(b'is: ')
valid = bytes.fromhex(p.recvline().strip().decode())
def xor(key, msg):
    result = []
    for k, m in zip(key, msg):
        result.append(k ^ m)
    return bytes(result)

key = xor(valid, unencrypted_token)
p.recvuntil(b'1. ')

for characters in itertools.product(string.digits, repeat=4):
    password = ''.join(characters)
    print(password)
    unencrypted_token = json.dumps(['admin', password]).encode()
    p.sendline(b'2')
    p.sendline(xor(key, unencrypted_token).hex().encode())
    p.recvuntil(b'1. ')
    if p.recvline() == b'Print flag\n':
        p.sendline(b'1')
        p.interactive()

