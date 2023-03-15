#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file shell.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-13 17:16


import os
import errno
import subprocess


def utils_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def utils_syscall(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).strip().decode()
    except subprocess.CalledProcessError:
        return ''
