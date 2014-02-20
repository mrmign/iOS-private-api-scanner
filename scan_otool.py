#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
get apis from otool -ov qzone
"""

import os
import re
import subprocess

def otool_ov(qzone):
    cmd = "/usr/bin/otool -ov %s" % qzone
    out = subprocess.check_output(cmd.split())
    return out

def get_section(text):
    section_pattern = re.compile("Contents\sof\s\(([^)]+)\)\ssection\s*^((?:(?!Contents\sof\s\([^)]+\)\ssection)[\s\S])+)", re.VERBOSE|re.MULTILINE)
    sections = []
    for sec in section_pattern.finditer(text):
        sections.append([sec.group(1),sec.group(2)])

    return sections

def get_classlist(text):
    pattern_str = """
        [0-9a-f]+\s0x[0-9a-f]+\s_OBJC_CLASS_\$_([\w]+)\s*^((?:(?![0-9a-f]+\s0x[0-9a-f]+\s_OBJC_CLASS_\$_[\w]+)[\s\S])+)
    """
    class_pattern = re.compile(pattern_str, re.VERBOSE|re.MULTILINE)
    class_list = []
    for c in class_pattern.finditer(text):
        class_name = c.group(1)
        m, v, p = get_class_values(c.group(2))
        #class_list.append({class_name:{"method":m, "var":v, "attr":p}})
        class_list.append([m, v,p])
    return class_list
    
def get_catlist(text):
    pattern_str = """
        #[0-9a-f]+\s0x[0-9a-f]+\s+^((?:(?![0-9a-f]+\s0x[0-9a-f]+)[\s\S])+)
        [0-9a-f]+\s0x[0-9a-f]+\s+^((?:(?!instancePorperties)[\s\S])+)
    """
    cat_pattern = re.compile(pattern_str, re.VERBOSE|re.MULTILINE)
    cat_list = []
    var_list = []
    pro_list = []
    for c in cat_pattern.finditer(text):
        m, v, p = get_class_values(c.group(1))
        #cat_list.append(m)
        cat_list += m
        var_list += v
        pro_list += p
    print "catlist", len(cat_list), len(var_list), len(pro_list)
    return cat_list, var_list+ pro_list

def get_class_name(text):
    patter = re.compile("_OBJC_CLASS_\$_([\w]+)")
    c_list = []
    for c in patter.finditer(text):
        c_list.append(c.group(1))
    return c_list

def get_class_values(text):
    method = re.compile("name\s0x[0-9a-f]+\s([\w:.]+)\s*types\s0x[0-9a-f]+", re.MULTILINE)
    variable = re.compile("name\s0x[0-9a-f]+\s([\w]+)\s*type\s0x[0-9a-f]+\s([@\"\w<>]+)", re.MULTILINE)
    #prop = re.compile("name\s0x[0-9a-f]+([\w]+)\s*attributes", re.MULTILINE)
    prop = re.compile("name\s0x[0-9a-f]+\s([\w]+)\s*attributes\sx[0-9a-f]+\s[@\"\w<>,&*]+", re.MULTILINE)
    m_list = []
    v_list = []
    p_list = []
    for m in method.finditer(text):
        m_list.append(m.group(1))
    for v in variable.finditer(text):
        #v_list.append((v.group(1), v.group(2)))
        v_list.append(v.group(1))
    for p in prop.finditer(text):
        p_list.append(p.group(1))
    return m_list, v_list, p_list

def get_text_type(s):
    a = s.split(",")[-1]
    return a.split("_")[-1]

def main(qzone):
    #text = otool_ov(qzone)
    text = qzone
    sections = get_section(text)
    classlist = []
    classrefs = []
    catlist = []
    for sec in sections:
        t = get_text_type(sec[0])
        if t == "classlist":
            classlist += get_classlist(sec[1])
        elif t == "classrefs" or t == "superrefs":
            classrefs += get_class_name(sec[1])
        elif t == "catlist":
            #catlist += get_catlist(sec[1])
            catlist, vp = get_catlist(sec[1])
    methods = []
    var = []
    pro = []
    for m in classlist:
        methods += m[0]
        var += m[1]
        pro += m[2]
    print len(methods), len(var), len(pro)
    return methods+catlist, var+pro + vp# classrefs


if __name__ == "__main__":
    with open("qzone.segment") as f:
        text = f.read()
    #sec = get_section(text)
    #print len(sec)
    a ,b = main(text)
    print len(a), len(b)


# 51273 13913 9383
