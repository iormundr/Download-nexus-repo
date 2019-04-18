#!/usr/bin/env python3

import sys
import requests
import json
import os
import argparse

args_options = argparse.ArgumentParser()

args_options.add_argument("-r", "--repository", dest="repository", help="Nexus repository name", default="snapshots")
args_options.add_argument("-u", "--user", dest="user", help="user")
args_options.add_argument("-p", "--password", dest="password", help="password" )
args_options.add_argument("-n", "--url", dest="url", help="nexus url")

options = args_options.parse_args()
if not options.repository:
    print("No repository specified !!")
    sys.exit(1)

headers = {'content-type': 'application/json'}

req = requests.get(options.url + '/service/rest/v1/repositories',headers=headers)
data = req.json()

repos = []        
for item in data:
    repos.append(item['name'])
if options.repository not in repos:
    print("Repo does not exist, please check the name")
    sys.exit(1)
files_downloaded = 0

urlRepo = options.url + "/service/rest/v1/assets?repository=" + options.repository
req = requests.get(urlRepo,headers=headers)
data = req.json()

while True:
    for x in range(len(data['items'])):
        path=data['items'][x]['path'].split('/',100)
        path = path[:-1]
        path = [x for x in path if x!='-']
        fp=os.path.join(str(options.repository) ,* path )
        if not os.path.isdir(fp):
            os.makedirs(fp)
        dir="".join([x+'/' for x in path])
        dir=options.repository +  '/' + dir
        print(dir + " Downloading " +  data['items'][x]['downloadUrl'])
        cwd=os.getcwd()
        os.chdir(str(dir))
        os.system('wget --user ' + str(options.user)+ ' --password ' + str(options.password)+' ' + data['items'][x]['downloadUrl'] + ' &> /tmp/' + options.repository + '.log')
        files_downloaded+=1
        os.chdir(cwd)
        token_mem = data['continuationToken']
    if data['continuationToken'] is None:
        break
    urlRepo = options.url + "/service/rest/v1/assets?continuationToken=" + data['continuationToken'] + "&repository=" + options.repository
    req = requests.get(urlRepo,headers=headers)
    try:
        data = req.json()
    except Exception as Error:
        print("Empty json input")
        print(Error)
    if token_mem == data['continuationToken'] or data['continuationToken'] is None:
        print("Breaking now..")
        break
print("REPO: " + options.repository  + " DOWNLOADED")
print("Number of files downloaded:  " , files_downloaded)
