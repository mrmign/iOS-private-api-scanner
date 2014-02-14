#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
iterate header files in Frameworks
"""
import os
import subprocess

def public_framework_headers():
    """
    get all public frameworks' header files(documented)
    Args:
        
    Returns:
        [('UIKit.framework', 'UIWindow.h', 
        '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/UIKit.framework/Headers/UIWindow.h')]
    """
    def iterate_dir(framework, prefix, path):
        files = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                files.append((framework, prefix+f, os.path.join(path, f)))
            elif os.path.isdir(os.path.join(path, f)):
                files += iterate_dir(framework, prefix+f+"/", os.path.join(path, f))
        return files
            
    allpaths = []
    path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/"
    #import pdb
    #pdb.set_trace()
    for framework in os.listdir(path):
        if framework.endswith(".framework"):
            header_path = path + framework +"/Headers/"
            if os.path.exists(header_path):
                #for header in os.listdir(header_path):
                #    file_path = header_path + header
                #    allpaths.append((framework, header, file_path))
                allpaths += iterate_dir(framework, "", os.path.join(path, header_path))
    return allpaths
    #print len(allpaths)

def public_include_headers():
    """
    get all the header files in .../usr/include/objc/
    Args:
    Returns:
        [('/usr/include/objc', 'NSObject.h', 
        '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/usr/include/objc/NSObject.h')]
    """
    allpaths = []
    path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/usr/include/objc/"
    for header in os.listdir(path):
        allpaths.append(("/usr/include/objc", header, path + header))
    return allpaths

def class_dump_framework():
    """
    class-dump public framework
    Todo:
    iterate all the files and directories, to find the mach-o files. We can accomplish this with "file -b xxx"
    """
    cur_dir = os.getcwd()
    #path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/"
    path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/PrivateFrameworks/"
    dump_cmd = "/usr/local/bin/class-dump -H %s -o %s"
    for framework in os.listdir(path):
        if framework.endswith(".framework"):
            #cmd = dump_cmd%(os.path.join(path, framework), os.path.join(os.path.join(cur_dir, "pub-headers"), framework))
            cmd = dump_cmd%(os.path.join(path, framework), os.path.join(os.path.join(cur_dir, "pri-headers"), framework))
            ret = subprocess.call(cmd.split())
            if ret != 0:
                print framework


def public_dump_headers():
    """
    get all public frameworks' header files(documented)
    Args:
        
    Returns:
        [('UIKit.framework', 'UIWindow.h', 
        '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/UIKit.framework/Headers/UIWindow.h')]
    """
    def iterate_dir(framework, prefix, path):
        files = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                files.append((framework, prefix+f, os.path.join(path, f)))
            elif os.path.isdir(os.path.join(path, f)):
                files += iterate_dir(framework, prefix+f+"/", os.path.join(path, f))
        return files
            
    allpaths = []
    path = os.path.join(os.getcwd(), "pub-headers") 
    #import pdb
    #pdb.set_trace()
    for framework in os.listdir(path):
        if framework.endswith(".framework"):
            header_path = os.path.join(path, framework)
            if os.path.exists(header_path):
                #for header in os.listdir(header_path):
                #    file_path = header_path + header
                #    allpaths.append((framework, header, file_path))
                allpaths += iterate_dir(framework, "", header_path)
    return allpaths
    #print len(allpaths)

if __name__ == "__main__":
    #print public_framework_headers()
    #print public_include_headers()
    class_dump_framework()
    pass
