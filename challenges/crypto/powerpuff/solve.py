#!/usr/bin/env python3

from pwn import remote
import random, time

HOST, PORT = "127.0.0.1", 7000

def gen():
    a = ['Bubbles','Buttercup','Blossom']
    random.seed(random.random()*123)
    random.shuffle(a)
    return " ".join(a)

r = remote(HOST, PORT)
r.recvline(); r.recvline()
obs = [r.recvline(timeout=2).decode().strip() for _ in range(3)]

def reproduces(s):
    random.seed(s)
    first_outputs = [gen() for _ in range(3)]
    return first_outputs == obs

now = int(time.time())
found = None
for s in range(now, now+10):
    if reproduces(s):
        found = s; break

assert found is not None, "seed not found"
random.seed(found)
for _ in range(3): 
    gen()

for _ in range(10):
    r.recvuntil(b"now guess what comes next")
    p = gen()
    r.sendline(p.encode())
    print(r.recvline(timeout=2).decode().strip())

print(r.recvall(timeout=2).decode(errors="ignore"))
r.close()
