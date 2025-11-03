from pwn import *

p = process(['python3', 'chall.py'])
p.recvuntil(b'n = ')
n = int(p.recvline())
e = 65537
print('n = ', n)
rotated = []
for i in range(512):
    p.sendline(str(i))
    p.recvuntil(b'>')
    rotated.append(int(p.recvline()))

plaintext = 0
for c1, c2 in zip(rotated, rotated[1:] + rotated[:1]):
    plaintext <<= 1
    if (pow(2, e, n) * c1) % n != c2:
        plaintext += 1


msg_int = int.to_bytes(plaintext,  64)
print(msg_int)