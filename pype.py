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
            html = "test"
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
