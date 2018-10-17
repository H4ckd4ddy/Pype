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
url = "http://127.0.0.1/"
port = 80
directory = "."
deleteLimit = 24#hours
cleaningInterval = 1#hours
#SETTINGS END

import sys,time
import signal
import threading
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import secrets
import os
import shutil

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
            self.wfile.write(str.encode("Hello World !"))
        return
    def do_PUT(self):
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        while "Bad token":
            randomToken = secrets.token_urlsafe(6)
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
    print("Starting a server on port {}".format(port))
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