#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import re
import sys
import _thread
import time
import urllib
import urllib.request
import urllib.parse

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        sleep = 10 # seconds
        maxsleep = 100
        while sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            try:
                raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
            except:
                pass
            sleep = sleep * 2
    return raw

def isScriptAliveCore(pidfilename=''):
    while 1:
        with open(pidfilename, 'w') as f:
            f.write('alive')
        time.sleep(10)

def isScriptAlive(filename=''):
    alivefilename = '%s.alive' % (filename)
    if os.path.exists(alivefilename):
        print('Script is working, we wont launch another copy. Exiting...')
        os.remove(alivefilename)
        sys.exit()
    else:
        print('Alive file not found. We continue this instance')
        try:
           _thread.start_new_thread(isScriptAliveCore, (alivefilename,) )
        except:
           print("Error: unable to start thread")

def loadSPARQL(sparql=''):
    json1 = ''
    if sparql:
        try:
            json1 = json.loads(sparql)
            return json1
        except:
            print('Error downloading SPARQL? Malformatted JSON? Skiping\n')
            return 
    else:
        print('Server return empty file')
        return 
    return

