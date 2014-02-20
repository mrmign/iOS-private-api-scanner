#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
scan qzone source code to get all strings defined, like @"xxx".
"""

import os
import re
from removecomment import remove_comments
source_dir = "/Users/sngTest/Documents/EclipseWorkSpace/code/test/src"
def iter_directory(path):
    files = []
    for f in os.listdir(path):
        p = os.path.join(path, f)
        if os.path.isfile(p):
            files.append(p)
        elif os.path.isdir(p):
            files += iter_directory(p)
    return files


pattern = re.compile("@\"([^\"]*)\"", re.VERBOSE|re.MULTILINE)
def scanfile(filepath):
    strings = set()
    with open(filepath) as f:
        text = f.read()
        clean_text = remove_comments(text)
        for m in pattern.finditer(clean_text):
            strings.add(m(1))
    return strings


def main():
    files = iter_directory(source_dir)
    strs = set()
    for f in files:
        strs |= scanfile(f)

    f = open("strings_in_qzone", "w")
    for s in strs:
        print s>>f
    f.close()

if __name__ == "__main__":
    main()

