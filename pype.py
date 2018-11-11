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
from http.server import HTTPServer, baseHTTPRequestHandler
import os
import binascii
import shutil
import base64

# SETTINGS BEGIN
url = "http://pype.sellan.fr/"
port = 80
directory = "/tmp"
delete_limit = 24  # hours
cleaning_interval = 1  # hours
id_length = 2  # bytes
max_name_length = 64  # chars
max_file_size = 52428800  # bytes
# SETTINGS END


def path_to_array(path):
    path_array = path.split('/')
    path_array = [element for element in path_array if element]
    return path_array


def array_to_path(path_array):
    return '/'.join(path_array)


def path_initialisation():
    directory = path_to_array(directory)
    directory.append("pype")
    # Create directory for Pype if not exist
    if not os.path.exists(array_to_path(directory)):
        os.makedirs(array_to_path(directory), 666)



class request_handler(baseHTTPRequestHandler):
    def do_GET(self):  # For home page and download
        if '?' in self.path:
            option = self.path.split('?')[1]
            request_path = self.path.split('?')[0]
        else:
            option = None
            request_path = self.path
        file_path = directory+"/pype"+request_path
        if request_path != "/" and os.path.exists(file_path):
            if option == "info":
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(str.encode("About this file...\n"))
            else:
                file = open(file_path, 'rb')
                self.send_response(200)
                self.send_header("Content-Type", 'application/octet-stream')
                contentDisposition = 'attachment; filename="{}"'
                tmpPath = os.path.basename(file_path)
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
        file_name = self.path.split("/")[-1]  # Only take the file name
        if len(file_name) > max_name_length:  # Check file name length
            HTML_error = "Error: Too long file name (max {} chars)\n"
            HTML_error = HTML_error.format(max_name_length)
            self.wfile.write(str.encode(HTML_error))  # Return error
            return
        if length > max_file_size:  # Check file size
            HTML_error = "Error: Too big file (max {})\n"
            HTML_error = HTML_error.format(human_readable(max_file_size))
            self.wfile.write(str.encode(HTML_error))  # Return error
            return
        # Read content from request
        content = self.rfile.read(length)
        # Loop for generating uniq token
        while "Bad token":
            # Get random token from urandom
            random_token = binascii.hexlify(os.urandom(id_length)).decode()
            # If directory not exist -> token free
            if not os.path.exists(directory+"/pype/"+random_token):
                break
        # Create the token directory
        os.makedirs(directory+"/pype/"+random_token, 666)
        # Concat the new file full path
        file_path = directory+"/pype/"+random_token+"/"+file_name
        # Open new file to write binary data
        current_file = open(file_path, "wb")
        # Write content of request
        current_file.write(content)
        current_file.close()
        # Return new file url to user
        self.wfile.write(str.encode(url+random_token+"/"+file_name+"\n"))
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
    httpd = HTTPServer(server_address, request_handler)
    httpd.serve_forever()


def human_readable(bytes):  # Convert bytes to human readable string format
    units = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']
    cursor = 0
    while bytes > 1024:
        bytes /= 1024
        cursor += 1
    value = str(bytes).split('.')
    value[1] = value[1][:2]
    value = '.'.join(value)
    return value+' '+units[cursor]


def set_interval(func, time):
    e = threading.Event()
    while not e.wait(time):
        func()


def clean_files():
    removed = []
    now = time.time()
    limit_date = now - (delete_limit * 3600)
    for file in os.listdir(directory+"/pype/"):
        if os.path.exists(directory+"/pype/"+file):
            stats = os.stat(directory+"/pype/"+file)
            timestamp = stats.st_ctime
            if timestamp < limit_date:
                removed.append(file)
                shutil.rmtree(directory+"/pype/"+file)
    if len(removed) > 0:
        print("Files removed : {}".format(', '.join(removed)))


if __name__ == "__main__":
    server = Thread(target=run_on, args=[port])
    server.daemon = True
    server.start()
    set_interval(clean_files, (cleaning_interval * 3600))
    signal.pause()
