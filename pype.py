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

import sys
import time
import signal
import threading
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import binascii
import shutil
import base64

# SETTINGS BEGIN
url = "http://pype.sellan.fr/"
port = 80
directory = "/tmp"
deleteLimit = 24  # hours
cleaningInterval = 1  # hours
idLength = 2  # bytes
maxNameLength = 64  # chars
maxFileSize = 52428800  # bytes
# SETTINGS END


def path2Array(path):
    pathArray = path.split('/')
    pathArray = [element for element in pathArray if element]
    return pathArray


def array2Path(pathArray):
    return '/'.join(pathArray)


def pathInitialisation():
    directory = path2Array(directory)
    directory.append("pype")
    # Create directory for Pype if not exist
    if not os.path.exists(array2Path(directory)):
        os.makedirs(array2Path(directory), 666)


class requestHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # For home page and download
        if '?' in self.path:
            option = self.path.split('?')[1]
            requestPath = self.path.split('?')[0]
        else:
            option = None
            requestPath = self.path
        filePath = directory+"/pype"+requestPath
        if requestPath != "/" and os.path.exists(filePath):
            if option == "info":
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(str.encode("About this file...\n"))
            else:
                file = open(filePath, 'rb')
                self.send_response(200)
                self.send_header("Content-Type", 'application/octet-stream')
                contentDisposition = 'attachment; filename="{}"'
                tmpPath = os.path.basename(filePath)
                contentDisposition = contentDisposition.format(tmpPath)
                self.send_header("Content-Disposition", )
                fs = os.fstat(file.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(file, self.wfile)
                if option == "delete":
                    print("Delete this file")
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = "PCFET0NUWVBFIGh0bWw+CjxodG1sPgoJPGhlYWQ+CgkJPG1ldGEgY2hhcn\
                   NldD0nVVRGLTgnPgoJCTx0aXRsZT5QeXBlPC90aXRsZT4KCQk8c3R5bGU+C\
                   gkJCWJvZHkgewoJCQkJZm9udC1mYW1pbHk6IGNvdXJpZXIsYXJpYWw7CgkJ\
                   CQljb2xvcjogd2hpdGU7CgkJCX0KCQkJI21haW5fdGl0bGUgewoJCQkJcG9\
                   zaXRpb246IGFic29sdXRlOwoJCQkJdG9wOiAzMHB4OwoJCQkJbGVmdDogMz\
                   BweDsKCQkJCWNvbG9yOiAjMjk4MGNjOwoJCQkJZm9udC13ZWlnaHQ6IGJvb\
                   GQ7CgkJCQlmb250LXNpemU6IDMwcHg7CgkJCX0KCQkJI0NMSSB7CgkJCQlo\
                   ZWlnaHQ6IDMwMHB4OwoJCQkJd2lkdGg6IDY1MHB4OwoJCQkJcGFkZGluZzo\
                   gMjVweDsKCQkJCXBvc2l0aW9uOiBhYnNvbHV0ZTsKCQkJCW1hcmdpbjogYX\
                   V0bzsKCQkJCXRvcDogMDsKCQkJCXJpZ2h0OiAwOwoJCQkJYm90dG9tOiAwO\
                   woJCQkJbGVmdDogMDsKCQkJCWJhY2tncm91bmQ6IGJsYWNrOwoJCQkJYm9y\
                   ZGVyLXJhZGl1czogMCAwIDdweCA3cHg7CgkJCX0KCQkJCgkJCSNDTEkgI2J\
                   hciB7CgkJCQlwb3NpdGlvbjogYWJzb2x1dGU7CgkJCQl0b3A6IC0yNXB4Ow\
                   oJCQkJbGVmdDogMDsKCQkJCXJpZ2h0OiAwOwoJCQkJd2lkdGg6IDEwMCU7C\
                   gkJCQloZWlnaHQ6IDI1cHg7CgkJCQlib3JkZXItcmFkaXVzOiA3cHggN3B4\
                   IDAgMDsKCQkJCWJhY2tncm91bmQ6ICNlMGUwZTA7CgkJCQl0ZXh0LWFsaWd\
                   uOiBjZW50ZXI7CgkJCX0KCQkJCgkJCSNDTEkgI2JhciAjdGl0bGUgewoJCQ\
                   kJZm9udC1zaXplOiA4MCU7CgkJCQljb2xvcjogIzc1NzU3NTsKCQkJCW1hc\
                   mdpbi10b3A6IDVweDsKCQkJfQoJCQkjQ0xJICNiYXIgI2dyZWVuIHsKCQkJ\
                   CXBvc2l0aW9uOiBhYnNvbHV0ZTsKCQkJCXRvcDogNXB4OwoJCQkJcmlnaHQ\
                   6IDEwcHg7CgkJCQloZWlnaHQ6IDE1cHg7CgkJCQl3aWR0aDogMTVweDsKCQ\
                   kJCWJvcmRlci1yYWRpdXM6IDI1cHg7CgkJCQliYWNrZ3JvdW5kOiAjM2NiY\
                   TNjOwoJCQkJYm9yZGVyOiBzb2xpZCAxcHggZ3JleTsKCQkJfQoJCQkjQ0xJ\
                   ICNiYXIgI29yYW5nZSB7CgkJCQlwb3NpdGlvbjogYWJzb2x1dGU7CgkJCQl\
                   0b3A6IDVweDsKCQkJCXJpZ2h0OiAzM3B4OwoJCQkJaGVpZ2h0OiAxNXB4Ow\
                   oJCQkJd2lkdGg6IDE1cHg7CgkJCQlib3JkZXItcmFkaXVzOiAyNXB4OwoJC\
                   QkJYmFja2dyb3VuZDogI2ZjYmQ1MTsKCQkJCWJvcmRlcjogc29saWQgMXB4\
                   IGdyZXk7CgkJCX0KCQkJI0NMSSAjYmFyICNyZWQgewoJCQkJcG9zaXRpb24\
                   6IGFic29sdXRlOwoJCQkJdG9wOiA1cHg7CgkJCQlyaWdodDogNTZweDsKCQ\
                   kJCWhlaWdodDogMTVweDsKCQkJCXdpZHRoOiAxNXB4OwoJCQkJYm9yZGVyL\
                   XJhZGl1czogMjVweDsKCQkJCWJhY2tncm91bmQ6ICNmZjU3NTc7CgkJCQli\
                   b3JkZXI6IHNvbGlkIDFweCBncmV5OwoJCQl9CgkJCSN0ZXh0ZSB7CgkJCQl\
                   tYXJnaW4tdG9wOiA1MHB4OwoJCQkJZm9udC1zaXplOiAxNXB4OwoJCQl9Cg\
                   kJCSNhdXRob3IgewoJCQkJcG9zaXRpb246IGFic29sdXRlOwoJCQkJYm90d\
                   G9tOiAxMHB4OwoJCQkJbGVmdDogMTBweDsKCQkJCWNvbG9yOiAjODA4MDgw\
                   OwoJCQl9CgkJPC9zdHlsZT4KCTwvaGVhZD4KCTxib2R5PgoJCTxkaXYgaWQ\
                   9J21haW5fdGl0bGUnPlB5cGU8L2Rpdj4KCQk8YSBocmVmPSJodHRwczovL2\
                   dpdGh1Yi5jb20vc2VsbGFuL1B5cGUiIHRhcmdldD0iX2JsYW5rIj48aW1nI\
                   HN0eWxlPSJwb3NpdGlvbjogYWJzb2x1dGU7IHRvcDogMDsgcmlnaHQ6IDA7\
                   IGJvcmRlcjogMDsiIHNyYz0iaHR0cHM6Ly9zMy5hbWF6b25hd3MuY29tL2d\
                   pdGh1Yi9yaWJib25zL2ZvcmttZV9yaWdodF9yZWRfYWEwMDAwLnBuZyIgYW\
                   x0PSJGb3JrIG1lIG9uIEdpdEh1YiI+PC9hPgoJCTxkaXYgaWQ9J0NMSSc+C\
                   gkJCTxkaXYgaWQ9J2Jhcic+CgkJCQk8ZGl2IGlkPSd0aXRsZSc+UHlwZSAt\
                   IFt1cmxdPC9kaXY+CgkJCQk8ZGl2IGlkPSdncmVlbic+PC9kaXY+CgkJCQk\
                   8ZGl2IGlkPSdvcmFuZ2UnPjwvZGl2PgoJCQkJPGRpdiBpZD0ncmVkJz48L2\
                   Rpdj4KCQkJPC9kaXY+CgkJCTxkaXYgaWQ9J3RleHRlJz4KCQkJCVNpbXBsZ\
                   SBmaWxlIHNoYXJpbmcgc2VydmVyLCB0byB1cGxvYWQgYW5kIGRvd25sb2Fk\
                   IGZpbGUgZnJvbSBDTEkKCQkJCTxici8+PGJyLz48YnIvPgoJCQkJVG8gdXB\
                   sb2FkCToJY3VybCAtVCBmaWxlLnR4dCBbdXJsXTxici8+CgkJCQlUbyBkb3\
                   dubG9hZAk6CWN1cmwgW3VybF0vW2lkXS9maWxlLnR4dCA+IGZpbGVzLnR4d\
                   Dxici8+CgkJCTwvZGl2PgoJCTwvZGl2PgoJCTxhIGhyZWY9Imh0dHBzOi8v\
                   Y29udGFjdC5zZWxsYW4uZnIiPjxkaXYgaWQ9ImF1dGhvciI+RXRpZW5uZSB\
                   TRUxMQU48L2Rpdj48L2E+Cgk8L2JvZHk+CjwvaHRtbD4="
            html = base64.urlsafe_b64decode(html).decode("utf-8")
            self.wfile.write(str.encode(html.replace("[url]", url)))
        return

    def do_PUT(self):  # For upload
        # Get the request size in header
        length = int(self.headers['Content-Length'])
        self.send_response(200)  # Send success header
        self.send_header('Content-type', 'text/html')  # Send mime
        self.end_headers()  # Close header
        fileName = self.path.split("/")[-1]  # Only take the file name
        if len(fileName) > maxNameLength:  # Check file name length
            htmlError = "Error: Too long file name (max {} chars)\n"
            htmlError = htmlError.format(maxNameLength)
            self.wfile.write(str.encode(htmlError))  # Return error
            return
        if length > maxFileSize:  # Check file size
            htmlError = "Error: Too big file (max {})\n"
            htmlError = htmlError.format(humanReadable(maxFileSize))
            self.wfile.write(str.encode(htmlError))  # Return error
            return
        # Read content from request
        content = self.rfile.read(length)
        # Loop for generating uniq token
        while "Bad token":
            # Get random token from urandom
            randomToken = binascii.hexlify(os.urandom(idLength)).decode()
            # If directory not exist -> token free
            if not os.path.exists(directory+"/pype/"+randomToken):
                break
        # Create the token directory
        os.makedirs(directory+"/pype/"+randomToken, 666)
        # Concat the new file full path
        filePath = directory+"/pype/"+randomToken+"/"+fileName
        # Open new file to write binary data
        currentFile = open(filePath, "wb")
        # Write content of request
        currentFile.write(content)
        currentFile.close()
        # Return new file url to user
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
    httpd = HTTPServer(server_address, requestHandler)
    httpd.serve_forever()


def humanReadable(bytes):  # Convert bytes to human readable string format
    units = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']
    cursor = 0
    while bytes > 1024:
        bytes /= 1024
        cursor += 1
    value = str(bytes).split('.')
    value[1] = value[1][:2]
    value = '.'.join(value)
    return value+' '+units[cursor]


def setInterval(func, time):
    e = threading.Event()
    while not e.wait(time):
        func()


def cleanFiles():
    removed = []
    now = time.time()
    limitDate = now - (deleteLimit * 3600)
    for file in os.listdir(directory+"/pype/"):
        if os.path.exists(directory+"/pype/"+file):
            stats = os.stat(directory+"/pype/"+file)
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
    setInterval(cleanFiles, (cleaningInterval * 3600))
    signal.pause()
