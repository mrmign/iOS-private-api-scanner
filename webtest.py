#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Site for scanning private api.
"""

import web

urls = (
        "/(.*)", "hello"
    )

app = web.application(urls, globals())

class hello:
    def GET(self, name):
        if not name:
            name = "world"
        return "Hello, " + name

if __name__ == "__main__":
    app.run()
