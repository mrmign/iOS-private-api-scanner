#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
This file is used for getting iOS documented api from its document database.
"""
import os
import sqlite3

cur_dir = os.getcwd()
dbname = "new1.db"
dbpath = os.path.join(cur_dir, dbname)

def create_table():
    con = sqlite3.connect(dbpath)
    cur = con.cursor()
    sql = ("create table document_api("
           "id integer,"
           "api_name varchar,"
           "api_type interger,"
           "container_name varchar,"
           "framework_name varchar,"
           "header_path varchar)")
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

doc_db = "docSet.dsidx"
doc_db_path = os.path.join(cur_dir, doc_db)
def query(sql):
    """
    execute query sql in doc_db.
    Args:
        query sql
    Returns:
        result set of query
    """
    con = sqlite3.connect(doc_db_path)
    cur = con.cursor()
    cur.execute(sql)
    result_set = cur.fetchall()
    cur.close()
    con.close()
    return result_set

def insert(sql_list):
    """
    execute insert sqls.
    Args:
        list of sqls
    """
    con = sqlite3.connect(dbpath)
    cur = con.cursor()
    for sql in sql_list:
        try:
            cur.execute(sql)
        except Exception, e:
            print sql
    con.commit()
    cur.close()
    con.close()


def filter_doc_api():
    """
    get all methods in documented api
    """
    # ZTOKENTYPE = 3, 9, 12, 13, 16 all of them are methods
    sql = "SELECT T.Z_PK, T.ZTOKENNAME, T.ZTOKENTYPE, T.ZCONTAINER, M.ZDECLAREDIN FROM ZTOKEN AS T, ZTOKENMETAINFORMATION AS M WHERE ZTOKENTYPE IN (3,9,12,13,16) AND T.Z_PK = M.ZTOKEN"
    #sql = "SELECT T.Z_PK, T.ZTOKENNAME, T.ZTOKENTYPE, T.ZCONTAINER, M.ZDECLAREDIN FROM ZTOKEN AS T, ZTOKENMETAINFORMATION AS M WHERE ZTOKENTYPE IN (3,9,12,13,16) AND T.Z_PK = M.ZTOKEN AND T.ZCONTAINER IS NULL"
    apiset = query(sql)
    #print apiset[0]
    con = sqlite3.connect(doc_db_path)
    cur = con.cursor()
    container_sql = "SELECT ZCONTAINERNAME FROM ZCONTAINER WHERE Z_PK=%d"
    header_sql = "SELECT ZFRAMEWORKNAME, ZHEADERPATH FROM ZHEADER WHERE Z_PK=%d"
    sql_fmt = "insert into document_api(id, api_name, api_type, container_name, framework_name, header_path) values(%d, '%s', %d, '%s', '%s', '%s')"
    sql_list = []
    for r in apiset:
        # get containername from ZCONTAINER table
        container_name = ""
        if r[3]:
            cur.execute(container_sql % r[3])
            container_name = cur.fetchone()[0]
        # get frameworkname and headerpath from ZHEADER table
        framework_name = ""
        header_path = ""
        if r[4]:        
            cur.execute(header_sql % r[4])
            row = cur.fetchone()
            framework_name = row[0] if row[0] else ""
            header_path = row[1] if row[1] else ""
        sql_list.append(sql_fmt %(r[0], r[1], r[2], container_name, framework_name, header_path))
    cur.close()
    con.close()
    print len(sql_list)
    insert(sql_list)


if __name__ == "__main__":
    #create_table()
    filter_doc_api()
