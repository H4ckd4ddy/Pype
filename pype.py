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
delete_limit = 24  # hours
cleaning_interval = 1  # hours
id_length = 2  # bytes
max_name_length = 64  # chars
max_file_size = 52428800  # bytes
# SETTINGS END


def path_to_array(path):
    # Split path
    path_array = path.split('/')
    # Remove empty elements
    path_array = [element for element in path_array if element]
    return path_array


def array_to_path(path_array):
    # Join array
    path = '/' + '/'.join(path_array)
    return path


def path_initialisation():
    global directory
    directory = path_to_array(directory)
    directory.append("pype")
    # Create directory for Pype if not exist
    if not os.path.exists(array_to_path(directory)):
        os.makedirs(array_to_path(directory), 666)


def initialisation():
    path_initialisation()


class request_handler(BaseHTTPRequestHandler):
    def do_GET(self):  # For home page and download
        # Check for options
        if '?' in self.path:
            # Split options of request
            self.option = self.path.split('?')[1]
            self.request_path = self.path.split('?')[0]
        else:
            # No options
            self.option = None
            self.request_path = self.path
        # Convert path of request to array for easy manipulation
        self.request_path = path_to_array(self.request_path)
        # Construct full path of the file
        self.file_path = directory + self.request_path
        if len(self.request_path) > 0 and os.path.exists(array_to_path(self.file_path)):
            with open(array_to_path(self.file_path), 'rb') as self.file:
                # Load file stats
                self.file.stat = os.fstat(self.file.fileno())
                if self.option == "info":
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.response = "Name: {}\nSize: {}\nCountdown: {} minute(s)\n"
                    self.file.countdown = round((((delete_limit * 3600) + self.file.stat.st_ctime) - time.time())/60)
                    # Place data in response
                    self.response = self.response.format(path_to_array(self.file.name)[-1], self.file.stat.st_size, self.file.countdown)
                    # Send response
                    self.wfile.write(str.encode(self.response))
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", 'application/octet-stream')
                    contentDisposition = 'attachment; filename="{}"'
                    contentDisposition = contentDisposition.format(self.file.name)
                    self.send_header("Content-Disposition", contentDisposition)
                    self.send_header("Content-Length", str(self.file.stat.st_size))
                    self.end_headers()
                    shutil.copyfileobj(self.file, self.wfile)
                    # If user want deleted file after download
                    if self.option == "delete":
                        # Remove file name from path to delete the directory
                        self.file_path.pop()
                        shutil.rmtree(array_to_path(self.file_path))
                        # Show deletion in server logs
                        print("{} deleted !\n".format(array_to_path(self.file_path)))
        else:
            # Open HTML homepage file
            with open('index.html', 'r') as homepage:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # Send HTML page with replaced data
                self.wfile.write(str.encode(homepage.read().replace("[url]", url)))
        return

    def do_PUT(self):  # For upload
        # Get the request size in header
        self.file_size = int(self.headers['Content-Length'])
        self.send_response(200)  # Send success header
        self.send_header('Content-type', 'text/html')  # Send mime
        self.end_headers()  # Close header
        self.file_name = self.path.split("/")[-1]  # Only take the file name
        if len(self.file_name) > max_name_length:  # Check file name length
            HTML_error = "Error: Too long file name (max {} chars)\n"
            HTML_error = HTML_error.format(max_name_length)
            self.wfile.write(str.encode(HTML_error))  # Return error
            return
        if self.file_size > max_file_size:  # Check file size
            HTML_error = "Error: Too big file (max {})\n"
            HTML_error = HTML_error.format(human_readable(max_file_size))
            self.wfile.write(str.encode(HTML_error))  # Return error
            return
        # Read content from request
        content = self.rfile.read(self.file_size)
        # Loop for generating uniq token
        while "Bad token":
            # Get random token from urandom
            random_token = binascii.hexlify(os.urandom(id_length)).decode()
            # If directory not exist -> token free
            if not os.path.exists(array_to_path(directory+[random_token])):
                break
        # Create the token directory
        os.makedirs(array_to_path(directory+[random_token]), 666)
        # Concat the new file full path
        self.file_path = directory+[random_token, self.file_name]
        # Open new file to write binary data
        current_file = open(array_to_path(self.file_path), "wb")
        # Write content of request
        current_file.write(content)
        current_file.close()
        # Return new file url to user
        self.wfile.write(str.encode(url+random_token+"/"+self.file_name+"\n"))
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
    # Create list of deleted files
    removed = []
    now = time.time()
    # Compute the limit_date from setings
    limit_date = now - (delete_limit * 3600)
    for file in os.listdir(array_to_path(directory)):
        if os.path.exists(array_to_path(directory+[file])):
            # Get informations about this file
            stats = os.stat(array_to_path(directory+[file]))
            timestamp = stats.st_ctime
            if timestamp < limit_date:
                removed.append(file)
                shutil.rmtree(array_to_path(directory+[file]))
    if len(removed) > 0:
        print("Files removed : {}".format(', '.join(removed)))


if __name__ == "__main__":
    server = Thread(target=run_on, args=[port])
    server.daemon = True
    server.start()
    initialisation()
    # Launch auto cleaning interval
    set_interval(clean_files, (cleaning_interval * 3600))
    signal.pause()
