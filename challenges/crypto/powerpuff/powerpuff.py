#!/usr/bin/env python3


import random
import time

random.seed(int(time.time()))

def generate_ordering():
    a_prominent_trio = ['Bubbles','Buttercup','Blossom']
    random.seed(random.random() * 123)
    random.shuffle(a_prominent_trio)
    return " ".join(a_prominent_trio)

def  get_input():
    the_input = input("The order?")
    while "".join(sorted(the_input)).replace(" ", "") != 'BBBbbceellmooprsssttuuu':
        print("Invalid input!")
        the_input = input("The order?")
    return the_input

def server():
    print("Welcome!")
    print("Pay close attention to the pattern...")
    for i in range(3):
        print(generate_ordering())
    failed = False
    for i in range(10):
        print("now guess what comes next")
        the_input = get_input()
        next = generate_ordering()
        if the_input == next:
            print("correct")
        else:
            failed = True
            print("nope, it was " + next)
    if failed:
        print("Try your luck next time")
    else:
        print("MINUTEMAN{B10550m_sh0uldnt_s33d_th3_rng}")
server()
