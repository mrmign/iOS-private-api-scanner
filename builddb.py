#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
This file is used to build private api database
"""

import re
import sys
import os
import subprocess
import sqlite3
import time

cur_dir = os.getcwd()
dump_cmd = cur_dir + "/class-dump %s"
lib_path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/"
def class_dump_public():
    path = lib_path + "Frameworks/"
    with open("pub") as f:
        for line in f:
            name = line.split(".")[0]
            cmd = dump_cmd %(path+line)
            fn = cur_dir + "/public/"+name
            with open(fn, "w") as ff:
                out = os.popen(cmd)
                print >> ff, out.read()

def class_dump_private():
    path = lib_path + "PrivateFrameworks/"
    with open("pri") as f:
        for line in f:
            name = line.split(".")[0]
            cmd = dump_cmd %(path+line)
            fn = cur_dir + "/private/"+name
            with open(fn, "w") as ff:
                out = os.popen(cmd)
                print >> ff, out.read()
            
dump_header_cmd = cur_dir + "/class-dump -H  %s -o %s"
def class_dump_private_header():
    path = lib_path + "PrivateFrameworks/"
    with open("pri") as f:
        for line in f:
            name = line.split(".")[0]
            cmd = dump_header_cmd %(path+line, cur_dir+"/private-headers/"+name)
            subprocess.call(cmd.split())
            #out = os.popen(cmd)
            #import pdb
            #pdb.set_trace()
            #print cmd


def process_dump_file(frame_type):
    """
    frame_type: 
    public : Frameworks, public
    private: PrivateFrameworks, private
    """
    directory = "%s/%s/"%(cur_dir, frame_type)
    sql_tmp = "insert into %s(api_name, framework) values('%s', '%s')"
    for filename in os.listdir(directory):
        res = extract(directory + filename)
        sql_set = set()
        for api in res:
            sql_set.add(sql_tmp%(frame_type, api, filename))
        insertIntoDB(sql_set)

def methods():
    """
    get all methods in private frameworks
    """
    directory = "%s/%s/"%(cur_dir, "private")
    sql_tmp = "insert into methods(api_name, framework) values('%s', '%s')"
    for filename in os.listdir(directory):
        res = extract(directory + filename)
        sql_set = set()
        for api in res:
            sql_set.add(sql_tmp%(api, filename))
        insertIntoDB(sql_set)


def extract(filename):
    # normal struct **** {
    struct = re.compile("^struct (\w*).*")
    # typedef struct { **
    # } struct_name; 
    typedef = re.compile("^} (\w*);")
    method = re.compile("^[+-] \([ *\w]*\)\w+[;:].*")
    method_args = re.compile("(\w+:)\([\w *]*\)\w+ ?")
    method_no_args = re.compile("^[+-] \( *\w*\)(\w*);")
    interface = re.compile("^@interface (\w*).*")
    result = set()
    f = open(filename)
    #try:
        #f = open(filename)
    #except:
        #print"open file failure"
    for line in f:
        # find struct 1
        #s = struct.search(line)
        #if s:
            #result.add(s.groups()[0])
            #continue
        ## find struct 2
        #t = typedef.search(line)
        #if t:
            #result.add(t.groups()[0])
            #continue
        #i = interface.search(line)
        #if i:
            #result.add(i.groups()[0])
            #continue
        m = method.search(line)
        if m:
            args = re.findall(method_args, line)
            if len(args) > 0:
                result.add("".join(args))
            else:
                no_args = method_no_args.search(line)
                if no_args:
                    result.add(no_args.groups()[0])
            continue
    f.close()
    return result
            
def pub_pri_intersection():
    pri_sql = "select api_name from private group by api_name"
    pub_sql = "select api_name from public group by api_name"
    pri_res = set([r[0] for r in queryDB(pri_sql)])
    pub_res = set([r[0] for r in queryDB(pub_sql)])
    #print type(pri_res) 
    intersection_res = pri_res.intersection(pub_res)
    return intersection_res
    

def remove_public_methods():
    "remove public methods from private tables"
    inter = pub_pri_intersection()
    #print len(inter)
    sql = "delete from private where api_name='%s'"
    sqls = set()
    for i in inter:
        sqls.add(sql % i)
    delete(sqls)


def filter_public_with_():
    "merge apis start with _ in public frameworks into private tables"
    r = re.compile("^_\w*")
    sql = "select * from public"
    res = queryDB(sql)
    insert_sql = "insert into api(api_name, framework, from_public) values('%s', '%s', %d)"
    sql_set = set()
    for row in res:
        if r.search(row[0]):
            sql_set.add(insert_sql%(row[0], row[1], 1))
    insertIntoDB(sql_set)

def transfer_private():
    sql = "select * from private"
    res = queryDB(sql)
    insert_sql = "insert into api(api_name, framework, from_public) values('%s', '%s', %d)"
    sql_set = set()
    for row in res:
        sql_set.add(insert_sql%(row[0], row[1], 0))
    insertIntoDB(sql_set)

def delete_api_with_level():
    sql = "select ZSIGNATURE from ZPWEEP where ZLEVEL<=30"
    res = queryFromPweep(sql)
    #delete_sql = "delete from api where api_name ='%s'"
    delete_sql = "delete from methods where api_name ='%s'"
    sql_set = set()
    for row in res:
        sql_set.add(delete_sql%(row[0]))
    delete(sql_set)


def get_variables(qzone_classes=None):
    "get all private variables, properties, and interface name"
    qzone_classes = cur_dir+"/qzone.txt"
    interface = re.compile("^@interface (\w*).*")
    private = re.compile("^\s*[\w <>]* [*]?(\w*)[\[\]\d]*;")
    prop = re.compile("@property\([\w, ]*\) (?:\w+ )*[*]?(\w+); // @synthesize \w*(?:=([\w]*))?;")
    wait_end = False 
    res = set()
    with open(qzone_classes) as f:
        for line in f:
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
    reg = re.compile("^_.*")
    import pdb
    for r in res:
        s = reg.search(r[0])
        if s:
            #pdb.set_trace()

            ret.add(r[0])
    return ret

curday = time.strftime("%Y-%m-%d", time.localtime())
def match_result():
    pubs = get_public_method_whit_()
    strings = set()
    with open(cur_dir+"/out"+curday) as f:
        for line in f:
            strings.add(line.strip())
    variables = get_variables()
    #with open(cur_dir+"/variable.txt","w") as ff:
    #    print >>ff, variables
    left = strings - variables
    #comm = strings.intersection(variables)
    #with open(cur_dir+"/common.txt", "w") as f:
        #print >> f, comm
    inter = left.intersection(pubs)
    return inter

def get_private_framework():
    res = match_result()
    sql = "select * from public where api_name='%s'"
    ret = []
    for r in res:
        d = queryDB(sql % r)
        for dd in d:
            ret.append([dd[0], dd[1]])
            print "%s ----> %s"%(dd[0], dd[1])
    return ret

#dbname = "/privateapi.db"
#dbname = "/api.db"
dbname = "/newapi.db"
def create_table():
    con = sqlite3.connect(cur_dir + dbname)
    cur = con.cursor()
    sql = "create table private(api_name varchar, framework varchar)"
    sql1 = "create table public(api_name varchar, framework varchar)"
    sql2 = "create table methods(api_name varchar, framework varchar)"
    cur.execute(sql)
    cur.execute(sql1)
    cur.execute(sql2)
    con.commit()
    cur.close()
    con.close()

def insertIntoDB(sql_set):
    con = sqlite3.connect(cur_dir + dbname)
    cur = con.cursor()
    for sql in sql_set:
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

def delete(sql_set):
    con = sqlite3.connect(cur_dir + dbname)
    cur = con.cursor()
    for sql in sql_set:
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

def queryDB(sql):
    con = sqlite3.connect(cur_dir + dbname)
    cur = con.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    con.close()
    return res

def queryFromPweep(sql):
    con = sqlite3.connect(cur_dir+"/Pweep.sqlite")
    cur = con.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    con.close()
    return res


if __name__ == "__main__":
    #f = "/Users/sngTest/Desktop/uifoundation.txt"
    #res = extract(f)
    #for l in res:
        #print l
    #class_dump_public()
    #class_dump_private()
    #pass
    #inter = pub_pri_intersection()
    #for i in inter:
        #print i
    #pri_sql = "select api_name from private group by api_name"
    #pri_sql = "select api_name from public group by api_name"
    #res = queryDB(pri_sql)
    #count = 0
    ##print len(res)
    #for r in res:
        #if r[0] and r[0][0] == '_':
            #count += 1
    #print count
    #class_dump_private_header()
    
    #create_table()
    #process_dump_file("private")
    #process_dump_file("public")
    #remove_public_methods()
    #filter_public_with_()
    #transfer_private()
    #delete_api_with_level()
    #methods()
    #res = get_public_method_whit_()
    #res = match_result()
    #res = get_variables()
    res = get_private_framework()
    #for r in res:
    #    print r
