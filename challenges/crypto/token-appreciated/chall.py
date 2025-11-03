import json
import os
import string
import random

from you_dont_have_this_file import flag

one_time_pad = os.urandom(256)
one_minute_in_ns = 60 * 1000 * 1000 * 1000


def xor(key, msg):
    result = []
    for k, m in zip(key, msg):
        result.append(k ^ m)
    return bytes(result)


class User:
    def __init__(self, username, password=None):
        """
            Create a new user, generate a random 4-digit password if one is not given
        """
        self.username = username
        if password is None:
            password = ''.join([random.choice(string.digits) for _ in range(4)])
        self.password = password

    def generate_token(self):
        """
            Generates the login token for this user
        """
        unencrypted_token = json.dumps([self.username, self.password]).encode()
        return xor(one_time_pad, unencrypted_token)

    def check_token(self, token):
        """
            Check if the login token is valid for this user
        """
        decrypted_token = xor(one_time_pad, token)
        username, password = json.loads(decrypted_token)
        return username == self.username and password == self.password


admin = User('admin')
users = [admin]

logged_in = None
while True:
    if logged_in is None:
        print('1. Register new account')
        print('2. Log in with token')
        choice = int(input('> '))
        if choice == 1:
            username = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(12)])
            new_user = User(username)
            users.append(new_user)
            password = input('Enter password (4 digits): ')
            if len(password) != 4 and not all(c in string.digits for c in password):
                print('Your password is invalid')
                continue
            print('User', username, 'registered')
            print('Your login token is:', new_user.generate_token().hex())
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
            print('Your login token is:', logged_in.generate_token().hex())
        elif choice == 3:
            logged_in = None
            print('Logged out')
        else:
            print('Invalid choice')
