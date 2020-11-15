#!/usr/bin/env python3
import os
import re
import string
import random

random.seed(os.urandom(128))

path = '../btcxplr/__init__.py'
lines  = []
charset = string.ascii_letters + string.digits + '`~@#$%^&*()-_=+[]{};:,.<>/?'
generate_random_key = lambda length : ''.join(random.choice(charset) for i in range(length))

with open(path, 'r') as f:
    for line in f.readlines():
        line = line.strip()
        if 'app.secret_key' in line:
            line = 'app.secret_key = "{}"'.format(generate_random_key(32))
        lines.append(line)

with open(path, 'w') as f:
    f.write('\n'.join(lines))