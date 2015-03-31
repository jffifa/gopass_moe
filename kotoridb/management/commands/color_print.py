#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

def warn_print(s):
    sys.stderr.write ('\033[93m%s\033[0m\n' % (s,))

def fail_print(s):
    sys.stderr.write ('\033[91m%s\033[0m\n' % (s,))

def info_print(s):
    sys.stdout.write ('\033[92m%s\033[0m\n' % (s,))

