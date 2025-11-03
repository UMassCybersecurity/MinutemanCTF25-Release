from pwn import *

p = process(['python3', 'chall.py'])
p.recvuntil(b'token: ')
admin = bytes.fromhex(p.recvline().strip().decode())

p.sendline(b'1')
p.sendline(b'admi')
p.sendline(b' ')
p.recvuntil(b'is: ')
valid = bytes.fromhex(p.recvline().strip().decode())
spliced_token = (admin[:9] + valid[9:-105] + admin[-105:]).hex()
p.sendline(b'2')
p.sendline(spliced_token.encode())
p.sendline(b'1')

p.interactive()
