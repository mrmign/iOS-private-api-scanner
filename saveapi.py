#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
save apis into sqlite db
"""

import os
import sqlite3

from getmethods import extract
import iterheaders

cur_dir = os.getcwd()

#dbname = "new.db"
dbname = "new1.db"
db_path = os.path.join(cur_dir, dbname)

def create_table():
    """
    create tables
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = ("create table public_doc_api("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "framework varchar)")
    sql1 = ("create table public_all_api("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "framework varchar)")
    sql2 = ("create table public_include_api("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "framework varchar)")
    cur.execute(sql)
    cur.execute(sql1)
    cur.execute(sql2)
    con.commit()
    cur.close()
    con.close()

def insert(sql_list):
    """
    execute insert sqls.
    Args:
        list of sqls
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for sql in sql_list:
        try:
            cur.execute(sql)
        except Exception, e:
            print sql
    con.commit()
    cur.close()
    con.close()

def delete(sql_list):
    """
    execute delete sqls.
    Args:
        list of sqls
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for sql in sql_list:
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()
            
def query(sql):
    """
    execute query sql.
    Args:
        query sql
    Returns:
        result set of query
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(sql)
    result_set = cur.fetchall()
    cur.close()
    con.close()
    return result_set

def get_apis(filepath):
    """
    get the methods of file
    Args:
        header file path(absolute)
    Returns:
        methods list
    """
    with open(filepath) as f:
        text = f.read()
        apis = extract(text)
        return apis
    return []

def save_apis(api_list, header_file, framework, sql_fmt):
    """
    save apis into sqlite
    Args:
        api_list : all apis in header_file
        header_file : header file be processed
        framework : where header file belongs, To C-style apis, the framework
                    to be /usr/include/objc 
        sql_fmt : 
    Returns:
        None
    """
    pass

def main(call):
    #sql_fmt = ("insert into public_doc_api(api_name, class_name, type, header_file, framework)"
    #           "values('%s', '%s','%s','%s','%s')")
    #sql_fmt = ("insert into public_include_api(api_name, class_name, type, header_file, framework)"
               #"values('%s', '%s','%s','%s','%s')")
    sql_fmt = ("insert into public_all_api(api_name, class_name, type, header_file, framework)"
               "values('%s', '%s','%s','%s','%s')")
    sql_list = []
    #headers = iterheaders.public_framework_headers()
    headers = call()
    #print headers
    #return
    for h in headers:
        apis = get_apis(h[2])
        for api in apis:
            class_name = api["class"] if api["class"] != "ctype" else h[1]
            method_list = api["methods"]
            m_type = api["type"]
            for m in method_list:
                sql_list.append(sql_fmt % (m, class_name, m_type, h[1], h[0]))
    insert(sql_list)
        
def delete_document_api():
    """
    delete document apis from all dumped public apis
    """
    sql = "select api_name from document_api group by api_name"
    doc_api = query(sql)
    delete_sql = "delete from public_all_api where api_name ='%s'"
    sqllist = []
    for r in doc_api:
        sqllist.append(delete_sql % r[0])
    delete(sqllist)


if __name__ == "__main__":
    #create_table()
    #main(iterheaders.public_framework_headers)
    #main(iterheaders.public_include_headers)
    #main(iterheaders.public_dump_headers)
    delete_document_api()
