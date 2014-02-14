#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""
import os
import getmethods    
def iterate_dir(framework, prefix, path):                                                                      
    files = []  
    for f in os.listdir(path):                                                                                 
        if os.path.isfile(os.path.join(path, f)):
           files.append((framework, prefix+f, os.path.join(path, f)))                                         
        elif os.path.isdir(os.path.join(path, f)):                                                                                 
           files += iterate_dir(framework, prefix+f+"/", os.path.join(path, f))                               
    return files 

if __name__ == "__main__":
    #print iterate_dir("framework", "", "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/OpenGLES.framework/Headers")
    with open("./UIColor.h") as f:
        text = f.read()
        #nocomments = getmethods.remove_comments(text)
        #noclass = getmethods.remove_objc(nocomments)
        print getmethods.remove_objc(text)
        print noclass
        #print getmethods.extract(text)
