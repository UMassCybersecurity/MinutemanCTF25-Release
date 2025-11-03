import hashlib
import json
import os
import string
import time
import random

from you_dont_have_this_file import flag, timestamp

one_time_pad = os.urandom(256)
one_minute_in_ns = 60 * 1000 * 1000 * 1000


def xor(key, msg):
    result = []
    for k, m in zip(key, msg):
        result.append(k ^ m)
    return bytes(result)


class User:
    def __init__(self, username, password):
        """
            Creates a new user
        """
        self.username = username
        self.password = password

    def generate_token(self, time_generated=None):
        """
            Generates the login token for this user
        """
        if time_generated is None:
            time_generated = time.time_ns()
        salt = os.urandom(16)
        unencrypted_token = json.dumps(
            [self.username,
             time_generated,
             hashlib.sha256(self.password.encode() + salt).hexdigest(),
             salt.hex()]
        ).encode()
        return xor(one_time_pad, unencrypted_token)

    def check_token(self, token):
        """
            Check if token is valid for this user, token must also not be expired
        """
        decrypted_token = xor(one_time_pad, token)
        username, time_generated, hashed_password, salt = json.loads(decrypted_token)
        return (username == self.username and
                hashlib.sha256(self.password.encode() + bytes.fromhex(salt)).hexdigest() == hashed_password and
                time_generated > time.time_ns() - 10 * one_minute_in_ns)


admin_password = ''.join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12)])
admin = User('admin', admin_password)
users = [admin]
old_token = admin.generate_token(time_generated=timestamp)
print('Intercepted admin token:', old_token.hex())

logged_in = None
while True:
    if logged_in is None:
        print('1. Register new account')
        print('2. Log in with token')
        choice = int(input('> '))
        if choice == 1:
            username = input('Enter username: ')
            if len(username) > 64:
                print('Username too long')
                continue
            if username in [user.username for user in users]:
                print('Account already registered')
                continue
            password = input('Enter password: ')
            new_user = User(username, password)
            users.append(new_user)
            print('User', username, 'registered')
            print('Your temporary (10 minutes) login token is:', new_user.generate_token().hex())
        elif choice == 2:
            token = bytes.fromhex(input('Enter login token: '))
            for user in users:
                if user.check_token(token):
                    logged_in = user
                    print('Logged in as user', logged_in.username)
                    break
            else:
                print('Token is not valid for any users - make sure your token has not expired!')
        else:
            print('Invalid choice')
    else:
        print('1. Print flag')
        print('2. Get new login token')
        print('3. Log out')
        choice = int(input('> '))
        if choice == 1:
            if logged_in == admin:
                print(flag)
            else:
                print('You can only print the flag as the admin!')
        elif choice == 2:
            print('Your temporary (10 minutes) login token is:', logged_in.generate_token().hex())
        elif choice == 3:
            logged_in = None
            print('Logged out')
        else:
            print('Invalid choice')
