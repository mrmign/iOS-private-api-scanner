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

import sys
import os
import sqlite3
import subprocess
import commands
import time
import re

cur_dir = os.getcwd()
curday = time.strftime("%Y-%m-%d", time.localtime())

"""
Todo:
rename ipa
unzip ipa
look for mach-o file, return it
"""
def unzip_app(app_name):
    cur_time = time.strftime("%Y-%m-%d#%H:%M:%S", time.localtime())

#APP_PATH = "/Users/sngTest/armingli/QZone.app"
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
    if app == None:
        #app = APP_PATH
        return -1
        
    #rename app
    #filename = app.split("/")[-1]
    #subprocess.call(["mv", app, cur_dir+"/upload/"+filename])
    #status, output = commands.getstatusoutput("/bin/sh %s %s"%(cur_dir + "/strings.sh", app))
    cur_time = time.strftime("%Y-%m-%d#%H:%M:%S", time.localtime())
    cmd = "strings %s" % app
    status, output = commands.getstatusoutput(cmd)
    outfile = os.path.join(cur_dir, "strings"+cur_time)
    with open(outfile, "w") as f:
        print >> f, output
    return outfile


def getStrings(string_file):
    "return all strings get from QZone.app"
    s = set()
    with open(string_file) as f:
        for line in f:
            s.add(line.strip())
    return s

#dbname = "/privateapi.db"
#dbname = "/api.db"
dbname = "/newapi.db"
def getApiList():
    con = sqlite3.connect(cur_dir + dbname)
    cur = con.cursor()
    #sql = "select api_name from private group by api_name"
    #sql = "select api_name from methods group by api_name"
    sql = "select api_name from public_all_api group by api_name"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    con.close()
    return res

def queryDB(sql):
    con = sqlite3.connect(cur_dir + dbname)
    cur = con.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    con.close()
    return res


def otool(app, outpath):
    status, output = commands.getstatusoutput("/bin/sh %s %s"%(cur_dir + "/otool.sh", app))
    r = re.compile("PrivateFrameworks\/(\w*)\.framework")
    out = output.split()
    with open(outpath, "a") as f:
        for line in out:
            if line.count("PrivateFrameworks") > 0:
                s = r.search(line)
                if s:
                    print >> f, s.groups()[0]

def get_qzone_variables(qzone=None):
    "get all private variables, properties, and interface name"
    class_dump = "/usr/local/bin/class-dump %s" % qzone
    dump_result= subprocess.check_output(class_dump.split())
    interface = re.compile("^@interface (\w*).*")
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
       r = prop.search(l)
       if r:
           m = r.groups()
           res.add(m[0])
           if m[1] != None:
               #res.add("V"+m[1])
               res.add(m[1])
    return res


def get_public_method_whit_():
    "get all public methods start with _"
    sql = "select api_name from public group by api_name"
    res = queryDB(sql)
    ret = set()
    #reg = re.compile("^_.*")
    import pdb
    for r in res:
        #s = reg.search(r[0])
        #if s:
            #pdb.set_trace()
        if r[0][0] == '_':
            ret.add(r[0])
    return ret


def scan(app_path, outpath):
    app = get_executable_file(app_path)
    
    strings = getStrings(stringsAPP(app))
    #apis = getApiList()
    api_set = get_public_method_whit_()
    #api_set = set()
    #for row in apis:
    #    api_set.add(row[0])
    print len(api_set)
    qzone_varibles = get_qzone_variables(app)
    left = strings - qzone_varibles
    print len(left)
    inter = left.intersection(api_set) 
    print len(inter)
    with open(outpath, "w") as of:
        for i in inter:
            print >> of, i
    #return inter
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "arguments error!"
    app_path = sys.argv[1]
    out_path = sys.argv[2]
    #ret = stringsAPP(app_path)
    #if ret != 0:
    #    print "strings app error"
    scan(app_path, out_path)
    #otool(app_path, out_path)
    #print get_executable_file(os.path.join(cur_dir, "QZone.app"))
    #print len(get_public_method_whit_())




