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
idLength = 2#bytes
maxNameLength = 64#chars
maxFileSize = 52428800#bytes
#SETTINGS END

import sys,time
import signal
import threading
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import binascii
import shutil
import base64

class requestHandler(BaseHTTPRequestHandler):
    def do_GET(self):#For home page and download
        filePath = directory+"/pype"+self.path
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
            html = "PCFET0NUWVBFIGh0bWw+CjxodG1sPgoJPGhlYWQ+CgkJPG1ldGEgY2hhcnNldD0nVVRGLTgnPgoJCTx0aXRsZT5QeXBlPC90aXRsZT4KCQk8c3R5bGU+CgkJCWJvZHkgewoJCQkJZm9udC1mYW1pbHk6IGNvdXJpZXIsYXJpYWw7CgkJCQljb2xvcjogd2hpdGU7CgkJCX0KCQkJI21haW5fdGl0bGUgewoJCQkJcG9zaXRpb246IGFic29sdXRlOwoJCQkJdG9wOiAzMHB4OwoJCQkJbGVmdDogMzBweDsKCQkJCWNvbG9yOiAjMjk4MGNjOwoJCQkJZm9udC13ZWlnaHQ6IGJvbGQ7CgkJCQlmb250LXNpemU6IDMwcHg7CgkJCX0KCQkJI0NMSSB7CgkJCQloZWlnaHQ6IDMwMHB4OwoJCQkJd2lkdGg6IDY1MHB4OwoJCQkJcGFkZGluZzogMjVweDsKCQkJCXBvc2l0aW9uOiBhYnNvbHV0ZTsKCQkJCW1hcmdpbjogYXV0bzsKCQkJCXRvcDogMDsKCQkJCXJpZ2h0OiAwOwoJCQkJYm90dG9tOiAwOwoJCQkJbGVmdDogMDsKCQkJCWJhY2tncm91bmQ6IGJsYWNrOwoJCQkJYm9yZGVyLXJhZGl1czogMCAwIDdweCA3cHg7CgkJCX0KCQkJCgkJCSNDTEkgI2JhciB7CgkJCQlwb3NpdGlvbjogYWJzb2x1dGU7CgkJCQl0b3A6IC0yNXB4OwoJCQkJbGVmdDogMDsKCQkJCXJpZ2h0OiAwOwoJCQkJd2lkdGg6IDEwMCU7CgkJCQloZWlnaHQ6IDI1cHg7CgkJCQlib3JkZXItcmFkaXVzOiA3cHggN3B4IDAgMDsKCQkJCWJhY2tncm91bmQ6ICNlMGUwZTA7CgkJCQl0ZXh0LWFsaWduOiBjZW50ZXI7CgkJCX0KCQkJCgkJCSNDTEkgI2JhciAjdGl0bGUgewoJCQkJZm9udC1zaXplOiA4MCU7CgkJCQljb2xvcjogIzc1NzU3NTsKCQkJCW1hcmdpbi10b3A6IDVweDsKCQkJfQoJCQkjQ0xJICNiYXIgI2dyZWVuIHsKCQkJCXBvc2l0aW9uOiBhYnNvbHV0ZTsKCQkJCXRvcDogNXB4OwoJCQkJcmlnaHQ6IDEwcHg7CgkJCQloZWlnaHQ6IDE1cHg7CgkJCQl3aWR0aDogMTVweDsKCQkJCWJvcmRlci1yYWRpdXM6IDI1cHg7CgkJCQliYWNrZ3JvdW5kOiAjM2NiYTNjOwoJCQkJYm9yZGVyOiBzb2xpZCAxcHggZ3JleTsKCQkJfQoJCQkjQ0xJICNiYXIgI29yYW5nZSB7CgkJCQlwb3NpdGlvbjogYWJzb2x1dGU7CgkJCQl0b3A6IDVweDsKCQkJCXJpZ2h0OiAzM3B4OwoJCQkJaGVpZ2h0OiAxNXB4OwoJCQkJd2lkdGg6IDE1cHg7CgkJCQlib3JkZXItcmFkaXVzOiAyNXB4OwoJCQkJYmFja2dyb3VuZDogI2ZjYmQ1MTsKCQkJCWJvcmRlcjogc29saWQgMXB4IGdyZXk7CgkJCX0KCQkJI0NMSSAjYmFyICNyZWQgewoJCQkJcG9zaXRpb246IGFic29sdXRlOwoJCQkJdG9wOiA1cHg7CgkJCQlyaWdodDogNTZweDsKCQkJCWhlaWdodDogMTVweDsKCQkJCXdpZHRoOiAxNXB4OwoJCQkJYm9yZGVyLXJhZGl1czogMjVweDsKCQkJCWJhY2tncm91bmQ6ICNmZjU3NTc7CgkJCQlib3JkZXI6IHNvbGlkIDFweCBncmV5OwoJCQl9CgkJCSN0ZXh0ZSB7CgkJCQltYXJnaW4tdG9wOiA1MHB4OwoJCQkJZm9udC1zaXplOiAxNXB4OwoJCQl9CgkJCSNhdXRob3IgewoJCQkJcG9zaXRpb246IGFic29sdXRlOwoJCQkJYm90dG9tOiAxMHB4OwoJCQkJbGVmdDogMTBweDsKCQkJCWNvbG9yOiAjODA4MDgwOwoJCQl9CgkJPC9zdHlsZT4KCTwvaGVhZD4KCTxib2R5PgoJCTxkaXYgaWQ9J21haW5fdGl0bGUnPlB5cGU8L2Rpdj4KCQk8YSBocmVmPSJodHRwczovL2dpdGh1Yi5jb20vc2VsbGFuL1B5cGUiIHRhcmdldD0iX2JsYW5rIj48aW1nIHN0eWxlPSJwb3NpdGlvbjogYWJzb2x1dGU7IHRvcDogMDsgcmlnaHQ6IDA7IGJvcmRlcjogMDsiIHNyYz0iaHR0cHM6Ly9zMy5hbWF6b25hd3MuY29tL2dpdGh1Yi9yaWJib25zL2ZvcmttZV9yaWdodF9yZWRfYWEwMDAwLnBuZyIgYWx0PSJGb3JrIG1lIG9uIEdpdEh1YiI+PC9hPgoJCTxkaXYgaWQ9J0NMSSc+CgkJCTxkaXYgaWQ9J2Jhcic+CgkJCQk8ZGl2IGlkPSd0aXRsZSc+UHlwZSAtIFt1cmxdPC9kaXY+CgkJCQk8ZGl2IGlkPSdncmVlbic+PC9kaXY+CgkJCQk8ZGl2IGlkPSdvcmFuZ2UnPjwvZGl2PgoJCQkJPGRpdiBpZD0ncmVkJz48L2Rpdj4KCQkJPC9kaXY+CgkJCTxkaXYgaWQ9J3RleHRlJz4KCQkJCVNpbXBsZSBmaWxlIHNoYXJpbmcgc2VydmVyLCB0byB1cGxvYWQgYW5kIGRvd25sb2FkIGZpbGUgZnJvbSBDTEkKCQkJCTxici8+PGJyLz48YnIvPgoJCQkJVG8gdXBsb2FkCToJY3VybCAtVCBmaWxlLnR4dCBbdXJsXTxici8+CgkJCQlUbyBkb3dubG9hZAk6CWN1cmwgW3VybF0vW2lkXS9maWxlLnR4dCA+IGZpbGVzLnR4dDxici8+CgkJCTwvZGl2PgoJCTwvZGl2PgoJCTxhIGhyZWY9Imh0dHBzOi8vY29udGFjdC5zZWxsYW4uZnIiPjxkaXYgaWQ9ImF1dGhvciI+RXRpZW5uZSBTRUxMQU48L2Rpdj48L2E+Cgk8L2JvZHk+CjwvaHRtbD4="
            html = base64.urlsafe_b64decode(html)
            self.wfile.write(str.encode(html.decode("utf-8").replace("[url]",url)))
        return
    def do_PUT(self):#For upload
        length = int(self.headers['Content-Length'])#Get the request size in header
        self.send_response(200)#Send success header
        self.send_header('Content-type','text/html')#Send mime
        self.end_headers()#Close header
        fileName = self.path.split("/")[-1]#Only take the file name
        if len(fileName) > maxNameLength:#Check file name length
            self.wfile.write(str.encode("Error: Too long file name (max {} chars)\n".format(maxNameLength)))#Return error
            return
        if length > maxFileSize:#Check file size
            self.wfile.write(str.encode("Error: Too big file (max {})\n".format(humanReadable(maxFileSize))))#Return error
            return
        content = self.rfile.read(length)#Read content from request
        if not os.path.exists(directory+"/pype/"):#Create directory for Pype if not exist
            os.makedirs(directory+"/pype/",666)
        while "Bad token":#Loop for generating uniq token
            randomToken = binascii.hexlify(os.urandom(idLength)).decode()#Get random token from urandom
            if not os.path.exists(directory+"/pype/"+randomToken):#If direcory not exist -> token free
                break
        os.makedirs(directory+"/pype/"+randomToken,666)#Create the token directory
        filePath = directory+"/pype/"+randomToken+"/"+fileName#Concat the new file full path
        currentFile = open(filePath,"wb")#Open new file to write binary data
        currentFile.write(content)#Write content of request
        currentFile.close()
        self.wfile.write(str.encode(url+randomToken+"/"+fileName+"\n"))#Return new file url to user
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
    httpd = HTTPServer(server_address, requestHandler)
    httpd.serve_forever()

def humanReadable(bytes):#Convert bytes to human readable string fomat
    units = ['o','Ko','Mo','Go','To','Po']
    cursor = 0
    while bytes > 1024:
        bytes /= 1024
        cursor += 1
    value = str(bytes).split('.')
    value[1] = value[1][:2]
    value = '.'.join(value)
    return value+' '+units[cursor]

def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()

def cleanFiles():
    removed = []
    now = time.time()
    limitDate = now - (deleteLimit * 3600)
    for file in os.listdir(directory+"/pype/"):
        if os.path.exists(directory+"/pype/"+file):
            stats = os.stat( directory + "/pype/" + file )
            timestamp = stats.st_ctime
            if timestamp < limitDate:
                removed.append(file)
                shutil.rmtree(directory+"/pype/"+file)
    if len(removed) > 0:
        print("Files removed : {}".format(', '.join(removed)))

if __name__ == "__main__":
    server = Thread(target=run_on, args=[port])
    server.daemon = True
    server.start()
    setInterval(cleanFiles,(cleaningInterval * 3600))
    signal.pause()