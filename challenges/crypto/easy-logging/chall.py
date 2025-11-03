import random
import hashlib
from you_dont_have_this_file import flag


def identity_permutation(size):
    """
    Returns a list of the form [0,1,2,...,size-1]
    """
    return list(range(size))

def apply_permutation(perm, target):
    """
    This code uses a permutation to shuffle the target array. For example:
    apply_permutation([0,3,1,2], ['a', 'b', 'c', 'd']) == ['a', 'd', 'b', 'c']
    apply_permutation([3,2,1,0], [1,2,3,0]) == [0, 3, 2, 1]
    """
    result = identity_permutation(len(perm))
    for i, j in enumerate(perm):
        result[i] = target[j]
    return result


def binary_exponentiate(perm, power):
    """
    This code does the same as the following (but much more efficiently):
    result = identity_permutation(len(perm))
    for _ in range(power):
        result = apply_permutation(perm, result)
    return result
    """
    result = identity_permutation(len(perm))
    perm_to_the_2_i = perm
    while power > 0:
        if power % 2 == 1:
            result = apply_permutation(perm_to_the_2_i, result)
        perm_to_the_2_i = apply_permutation(perm_to_the_2_i, perm_to_the_2_i)
        power >>= 1
    return result


g = identity_permutation(1009)
i = random.randint(1, 1009)
g = g[i:] + g[:i]
print('g =', g)

a = random.randint(1, 1 << 64)
ga = binary_exponentiate(g, a)
print('ga =', ga)

b = random.randint(1, 1 << 64)
gb = binary_exponentiate(g, b)
print('gb =', gb)

assert binary_exponentiate(gb, a) == binary_exponentiate(ga, b) == binary_exponentiate(g, a * b)
shared_private_key = binary_exponentiate(g, a * b)
one_time_pad = hashlib.sha512(str(shared_private_key).encode()).digest()


def xor(key, msg):
    result = []
    for k, m in zip(key, msg):
        result.append(k ^ m)
    return bytes(result)

print(f'ciphertext = bytes.fromhex("{xor(one_time_pad, flag).hex()}")')
