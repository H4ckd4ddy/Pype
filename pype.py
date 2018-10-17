#!/usr/bin/env python3

###########################################
#                                         #
#                 "Pype"                  #
#       Simple file sharing server,       #
#       to upload and download file       #
#                from  CLI                #
#                                         #
#             Etienne  SELLAN             #
#               17/10/2018                #
#                                         #
###########################################

#SETTINGS BEGIN
url = "http://pype.sellan.fr/"
port = 80
directory = "/tmp"
deleteLimit = 24#hours
cleaningInterval = 1#hours
#SETTINGS END

import sys,time
import signal
import threading
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import shutil
import base64

class fileRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        filePath = directory+self.path
        if self.path != "/" and os.path.exists(filePath):
            with open(filePath, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-Type", 'application/octet-stream')
                self.send_header("Content-Disposition", 'attachment; filename="{}"'.format(os.path.basename(filePath)))
                fs = os.fstat(file.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(file, self.wfile)
        else:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            html = "PCFET0NUWVBFIGh0bWw+CjxodG1sPgoJPGhlYWQ+CgkJPG1ldGEgY2hhcnNldD0nVVRGLTgnPgoJCTx0aXRsZT5QeXBlPC90aXRsZT4KCQk8c3R5bGU+CgkJCWJvZHkgewoJCQkJZm9udC1mYW1pbHk6IGNvdXJpZXIsYXJpYWw7CgkJCQljb2xvcjogd2hpdGU7CgkJCX0KCQkJI21haW5fdGl0bGUgewoJCQkJcG9zaXRpb246IGFic29sdXRlOwoJCQkJdG9wOiAzMHB4OwoJCQkJbGVmdDogMzBweDsKCQkJCWNvbG9yOiAjMjk4MGNjOwoJCQkJZm9udC13ZWlnaHQ6IGJvbGQ7CgkJCQlmb250LXNpemU6IDMwcHg7CgkJCX0KCQkJI0NMSSB7CgkJCQloZWlnaHQ6IDI1MHB4OwoJCQkJd2lkdGg6IDYwMHB4OwoJCQkJcGFkZGluZzogMjVweDsKCQkJCXBvc2l0aW9uOiBhYnNvbHV0ZTsKCQkJCW1hcmdpbjogYXV0bzsKCQkJCXRvcDogMDsKCQkJCXJpZ2h0OiAwOwoJCQkJYm90dG9tOiAwOwoJCQkJbGVmdDogMDsKCQkJCWJhY2tncm91bmQ6IGJsYWNrOwoJCQkJYm9yZGVyLXJhZGl1czogMCAwIDdweCA3cHg7CgkJCX0KCQkJCgkJCSNDTEkgI2JhciB7CgkJCQlwb3NpdGlvbjogYWJzb2x1dGU7CgkJCQl0b3A6IC0yNXB4OwoJCQkJbGVmdDogMDsKCQkJCXJpZ2h0OiAwOwoJCQkJd2lkdGg6IDEwMCU7CgkJCQloZWlnaHQ6IDI1cHg7CgkJCQlib3JkZXItcmFkaXVzOiA3cHggN3B4IDAgMDsKCQkJCWJhY2tncm91bmQ6ICNlMGUwZTA7CgkJCQl0ZXh0LWFsaWduOiBjZW50ZXI7CgkJCX0KCQkJCgkJCSNDTEkgI2JhciAjdGl0bGUgewoJCQkJZm9udC1zaXplOiA4MCU7CgkJCQljb2xvcjogIzc1NzU3NTsKCQkJCW1hcmdpbi10b3A6IDVweDsKCQkJfQoJCQkKCQkJI0NMSSAjYmFyICNncmVlbiB7CgkJCQlwb3NpdGlvbjogYWJzb2x1dGU7CgkJCQl0b3A6IDVweDsKCQkJCXJpZ2h0OiAxMHB4OwoJCQkJaGVpZ2h0OiAxNXB4OwoJCQkJd2lkdGg6IDE1cHg7CgkJCQlib3JkZXItcmFkaXVzOiAyNXB4OwoJCQkJYmFja2dyb3VuZDogIzNjYmEzYzsKCQkJCWJvcmRlcjogc29saWQgMXB4IGdyZXk7CgkJCX0KCQkJCgkJCSNDTEkgI2JhciAjb3JhbmdlIHsKCQkJCXBvc2l0aW9uOiBhYnNvbHV0ZTsKCQkJCXRvcDogNXB4OwoJCQkJcmlnaHQ6IDMzcHg7CgkJCQloZWlnaHQ6IDE1cHg7CgkJCQl3aWR0aDogMTVweDsKCQkJCWJvcmRlci1yYWRpdXM6IDI1cHg7CgkJCQliYWNrZ3JvdW5kOiAjZmNiZDUxOwoJCQkJYm9yZGVyOiBzb2xpZCAxcHggZ3JleTsKCQkJfQoJCQkKCQkJI0NMSSAjYmFyICNyZWQgewoJCQkJcG9zaXRpb246IGFic29sdXRlOwoJCQkJdG9wOiA1cHg7CgkJCQlyaWdodDogNTZweDsKCQkJCWhlaWdodDogMTVweDsKCQkJCXdpZHRoOiAxNXB4OwoJCQkJYm9yZGVyLXJhZGl1czogMjVweDsKCQkJCWJhY2tncm91bmQ6ICNmZjU3NTc7CgkJCQlib3JkZXI6IHNvbGlkIDFweCBncmV5OwoJCQl9CgkJCQoJCQkjdGV4dGUgewoJCQkJbWFyZ2luLXRvcDogNTBweDsKCQkJCWZvbnQtc2l6ZTogMTVweDsKCQkJfQoJCTwvc3R5bGU+Cgk8L2hlYWQ+Cgk8Ym9keT4KCQk8ZGl2IGlkPSdtYWluX3RpdGxlJz5QeXBlPC9kaXY+CgkJPGRpdiBpZD0nQ0xJJz4KCQkJPGRpdiBpZD0nYmFyJz4KCQkJCTxkaXYgaWQ9J3RpdGxlJz5QeXBlIC0gW3VybF08L2Rpdj4KCQkJCTxkaXYgaWQ9J2dyZWVuJz48L2Rpdj4KCQkJCTxkaXYgaWQ9J29yYW5nZSc+PC9kaXY+CgkJCQk8ZGl2IGlkPSdyZWQnPjwvZGl2PgoJCQk8L2Rpdj4KCQkJPGRpdiBpZD0ndGV4dGUnPgoJCQkJU2ltcGxlIGZpbGUgc2hhcmluZyBzZXJ2ZXIsIHRvIHVwbG9hZCBhbmQgZG93bmxvYWQgZmlsZSBmcm9tIENMSQoJCQkJPGJyLz48YnIvPjxici8+CgkJCQlUbyB1cGxvYWQJOgljdXJsIC1UIGZpbGUudHh0IFt1cmxdPGJyLz4KCQkJCVRvIGRvd25sb2FkCToJY3VybCBbdXJsXS9baWRdL2ZpbGUudHh0ID4gZmlsZXMudHh0PGJyLz4KCQkJPC9kaXY+CgkJPC9kaXY+Cgk8L2JvZHk+CjwvaHRtbD4="
            html = base64.urlsafe_b64decode(html)
            self.wfile.write(str.encode(html.decode("utf-8").replace("[url]",url)))
        return
    def do_PUT(self):
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        while "Bad token":
            randomToken = binascii.hexlify(os.urandom(6)).decode()
            if not os.path.exists(directory+"/"+randomToken):
                break
        os.makedirs(directory+"/"+randomToken,666)
        fileName = self.path.split("/")[-1]
        filePath = directory+"/"+randomToken+"/"+fileName
        currentFile = open(filePath,"wb")
        currentFile.write(content)
        currentFile.close()
        self.wfile.write(str.encode(url+randomToken+"/"+fileName+"\n"))
        return

def run_on(port):
    print("\n")
    print("/--------------------------------\\")
    print("|  Starting a server on port {}  |".format(port))
    print("\\--------------------------------/")
    print("\n")
    print("Reminder : \n")
    print("To upload   :      curl -T file.txt {}".format(url))
    print("To download :      curl {}/[id]/file.txt > files.txt".format(url))
    print("\n\nLogs : \n")
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, fileRequestHandler)
    httpd.serve_forever()
    
def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()

def cleanFiles():
    now = time.time()
    limitDate = now - (deleteLimit * 3600)
    for file in os.listdir(directory):
        if os.path.exists(directory+"/"+file):
            stats = os.stat( directory + "/" + xfile )
            timestamp = stats.st_ctime
            if timestamp < limitDate:
                os.rmtree(directory+"/"+file)

if __name__ == "__main__":
    server = Thread(target=run_on, args=[port])
    server.daemon = True
    server.start()
    setInterval(cleanFiles,(cleaningInterval * 3600))
    signal.pause()