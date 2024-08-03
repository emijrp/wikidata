#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2022 emijrp <emijrp@gmail.com>
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

import datetime
import json
import os
import re
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse
import pywikibot

def cronstop():
    return
    if datetime.datetime.now().isoweekday() in [1, 2, 3, 4, 5]: #1 Monday
        if datetime.datetime.now().hour > 4 and datetime.datetime.now().hour < 18:
            sys.exit()

def getClaims(site, mid):
    payload = {
      'action' : 'wbgetclaims',
      'format' : 'json',
      'entity' : mid,
    }
    request = site.simple_request(**payload)
    try:
        r = request.submit()
        #return json.loads(r)
        return r
    except pywikibot.exceptions.APIError as e:
        if e.code == 'no-such-entity':
            return { "claims": { } }
    return 

def removeAccents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def getURL(url='', retry=False, timeout=30):
    raw = ''
    version = 110
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/%d.0' % (version) })
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
    except:
        sleep = 10 # seconds
        maxsleep = 60
        while retry and sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            try:
                req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/%d.0' % (version) })
                raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
            except:
                version += 1
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

def getUserEditCount(user='', site=''):
    if user and site:
        editcounturl = 'https://%s/w/api.php?action=query&list=users&ususers=%s&usprop=editcount&format=json' % (site, urllib.parse.quote(user))
        raw = getURL(editcounturl)
        json1 = json.loads(raw)
        if 'query' in json1 and 'users' in json1['query'] and 'editcount' in json1['query']['users'][0]:
            return json1['query']['users'][0]['editcount']
    return 0

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

def getAllCountries():
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3FitemLabel%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ6256.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D%0AORDER%20BY%20ASC(%3FitemLabel)'
    url = '%s&format=json' % (url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)
    countries = []
    for result in json1['results']['bindings']:
        #print(result)
        q = result['item']['value'].split('/entity/')[1]
        label = result['itemLabel']['value']
        countries.append([label, q])
    return countries

