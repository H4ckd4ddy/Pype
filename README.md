# Pype

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/sellan/Pype/blob/master/LICENSE)

Simple file sharing server, to upload and download file from cli

## Usage

#### Launch server
```
./pype.py
```

#### Upload a file
```
curl -T file.txt https://pype.sellan.fr
```

#### Download a file
```
curl https://pype.sellan.fr/id/file.txt > file.txt
```
or
```
wget https://pype.sellan.fr/id/file.txt
```

#### Delete file after download
```
curl https://pype.sellan.fr/id/file.txt?delete > file.txt
```
or
```
wget https://pype.sellan.fr/id/file.txt?delete
```

#### Get infos about a file
```
curl https://pype.sellan.fr/id/file.txt?info
```

## Functions

* Show homepage
* Easy upload and download with curl
* Show file infos
* Delete file after download
* Auto-cleaning files after expiration
* Store logs (split standard events and errors)
