#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Arming lee <cloudniw1@gmail.com>
#
# Distributed under terms of the MIT license.
import web
import scanapp

urls = ('/upload', 'Upload',
        '/suc', 'Success',
    )

class Upload:
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        return """<html><head></head><body>
<form method="POST" enctype="multipart/form-data" action="">
<input type="file" name="myfile" />
<br/>
<input type="submit" />
</form>
</body></html>"""

    def POST(self):
        x = web.input(myfile={})
        filedir = '/Users/sngTest/armingli/upload/' # change this to the directory you want to store the file in.
        if 'myfile' in x: # to check if the file-object is created
            filepath=x.myfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
        #scanapp.stringsAPP(filename)
        raise web.seeother('/suc')

class Success:
    def GET(self):
        res = scanapp.scan()
        web.header("Content-Type","text/html; charset=utf-8")
        html = """
        <html><head>扫描结果</head><body><table>%s</table></body></html>
        """
        table = ""
        tr = "<tr>%s</tr>"
        td = "<td>%s</td>"
        count = 6
        tmp = ""
        for r in res:
            if count > 0:
                tmp += td % r
                count -= 1
            elif count == 0:
                count = 6
                table += tr % tmp
                tmp = ""
        return html % table


if __name__ == "__main__":
   app = web.application(urls, globals()) 
   app.run()
