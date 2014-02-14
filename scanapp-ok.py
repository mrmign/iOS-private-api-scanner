#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
This file is used to scan private iOS methods and variables
in app.
"""

import os
import sqlite3
import subprocess
import time
import re
from getmethods import extract

cur_dir = os.getcwd()
curday = time.strftime("%Y-%m-%d", time.localtime())

# APP_PATH = "/Users/sngTest/armingli/QZone.app"
def get_executable_file(path):
    regex = re.compile(".*?Mach-O.*")
    for f in os.listdir(path):
        cmd = "file -b %s" % os.path.join(path, f)
        out = subprocess.check_output(cmd.split())
        if regex.search(out):
            return os.path.join(path, f)

    
def stringsAPP(app=None):
    """
    Args:
        app : the full path of the Mach-O file in app
    Returns:
        outfile : the result file of the strings app
    """

    cmd = "strings %s" % app
    output = subprocess.check_output(cmd.split())
    strings = open("strings.txt", "w")
    print >>strings, output
    return set(output.split())


# def getStrings(string_file):
#     "return all strings get from QZone.app"
#     s = set()
#     with open(string_file) as f:
#         for line in f:
#             s.add(line.strip())
#     return s

# dbname = "/privateapi.db"
# dbname = "/api.db"
dbname = os.path.join(os.path.dirname(__file__), "new1.db")
def getApiList(public_framework):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    #sql = "select api_name from private group by api_name"
    # sql = "select api_name from methods group by api_name"
    framework = ""
    for f in public_framework:
        framework += '"%s",'%f
    #sql = 'select api_name from public_all_api where framework in(%s) group by api_name' % framework[:-1]
    sql = 'select api_name from public_all_api group by api_name'
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    con.close()
    ret = set()
    for r in res:
        ret.add(r[0])
    return ret

def queryDB(sql):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    con.close()
    return res


def otool(app_path):
    """
    Get framework included in app
    Args:
        Mach-o path
    Returns:
        two sets, one is public framework, one is private framework
    """
    cmd = "/usr/bin/otool -L %s" % app_path
    out = subprocess.check_output(cmd.split())
    pattern = re.compile("PrivateFrameworks\/(\w*)\.framework")
    pub_pattern = re.compile("Frameworks\/([\.\w]*)")
    private = set()
    public = set()
    for r in re.finditer(pattern, out):
        private.add(r.group(1))
    for r in re.finditer(pub_pattern, out):
        public.add(r.group(1))
    return private, public

def get_public_method_whit_():
    "get all public methods start with _"
    sql = "select api_name from public group by api_name"
    res = queryDB(sql)
    ret = set()
    # reg = re.compile("^_.*")
#     import pdb
    for r in res:
        # s = reg.search(r[0])
        # if s:
            # pdb.set_trace()
        if r[0][0] == '_':
            ret.add(r[0])
    return ret


def get_qzone_variables(qzone=None):
    "get all private variables, properties, and interface name"
    class_dump = "/usr/local/bin/class-dump %s" % qzone
    dump_result = subprocess.check_output(class_dump.split())
    interface = re.compile("^@interface (\w*).*")
    protocol = re.compile("@protocoli (\w*)")
    private = re.compile("^\s*[\w <>]* [*]?(\w*)[\[\]\d]*;")
    prop = re.compile("@property\([\w, ]*\) (?:\w+ )*[*]?(\w+); // @synthesize \w*(?:=([\w]*))?;")
    res = set()
    lines = dump_result.split("\n")
    wait_end = False 
    for line in lines:
        l = line.strip()
        if l.startswith("}"):
            wait_end = False
            continue
        if wait_end:
            r = private.search(l)
            if r:
                res.add(r.groups()[0])
            continue
        r = interface.search(l)
        if r:
            res.add(r.groups()[0])
            wait_end = True
            continue
        r = protocol.search(l)
        if r:
            res.add(r.groups()[0])
            wait_end = True
            continue
        r = prop.search(l)
        if r:
            m = r.groups()
            res.add(m[0])
            res.add("set" + m[0].title() + ":")
            print "set" + m[0].title() + ":"
            if m[1] != None:
                # res.add("V"+m[1])
                res.add(m[1])
    return res

def get_qzone_methods(app):
    class_dump = "/usr/local/bin/class-dump %s" % app
    dump_result = subprocess.check_output(class_dump.split())
    ret_methods = set()
    methods = extract(dump_result)
    for m in methods:
        ret_methods = ret_methods.union(set(m["methods"]))
    return ret_methods


def scan(app_path):
    if not os.path.exists(app_path):
        return [], []
    app = get_executable_file(app_path)
    
    strings = stringsAPP(app)
    #api_set = get_public_method_whit_()
    private, public = otool(app)
    api_set = getApiList(public)
    qzone_varibles = get_qzone_variables(app)
    left = strings - qzone_varibles
    inter = left.intersection(api_set) 
#     inter = []
    #return inter, otool_res
    qz_methods = get_qzone_methods(app)
    methods_in_qzone = inter.intersection(qz_methods)
    methods_not_in_qzone = inter - methods_in_qzone
    return methods_in_qzone, methods_not_in_qzone, private

if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print "arguments error!"
#     app_path = sys.argv[1]
#     out_path = sys.argv[2]
    # ret = stringsAPP(app_path)
    # if ret != 0:
    #    print "strings app error"
#     scan(app_path, out_path)
    # otool(app_path, out_path)
    # print get_executable_file(os.path.join(cur_dir, "QZone.app"))
    # print len(get_public_method_whit_())
    #path = "/Users/maxiao/Documents/WorkSpace/DailyBuild/build/53079/Payload/QZone.app"
    #path = "/Users/sngTest/armingli/QZone.app"
    path = "/Users/sngTest/Documents/EclipseWorkSpace/DailyBuild/build/53467/Payload/QZone.app"
    #print scan(path)
    a, b, c = scan(path)
    print "="*50
    print len(a), "Methods in QZone:"
    print "*"*50
    for aa in a:
        print aa
    print "="*50
    print len(b), "Methods not in QZone:"
    print "*"*50
    for bb in b:
        print bb

