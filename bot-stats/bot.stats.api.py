#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 emijrp <emijrp@gmail.com>
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

import csv
import datetime
import json
import os
import re
import sys
import time
import urllib
import urllib.request

import pywikibot

def loadLastEditId(nick='', path=''):
    lasteditid = 0
    if nick and path and os.path.exists('%s/%s-edits.csv' % (path, nick)):
        with open('%s/%s-edits.csv' % (path, nick), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                #print(', '.join(row))
                if int(row[0]) > lasteditid:
                    lasteditid = int(row[0])
    return lasteditid

def saveEdits(nick='', path='', edits=''):
    if nick and path and edits:
        with open('%s/%s-edits.csv' % (path, nick), 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar ='"')
            csvwriter.writerows(edits)

def main():
    path = '/data/project/emijrpbot/bots'
    nick = 'Emijrpbot'
    #load saved edits
    lasteditid = loadLastEditId(nick=nick, path=path)
    print('%d last edit id' % (lasteditid))
    
    #load new edits
    api = 'https://www.wikidata.org/w/api.php'
    apiquery = '?action=query&list=usercontribs&ucuser=%s&uclimit=500&ucprop=timestamp|title|comment|ids&format=json' % (nick)
    uccontinue = True
    uccontinue_name = 'uccontinue'
    total = 0
    edits = []
    while uccontinue:
        if len(edits) >= 10000:
            saveEdits(nick=nick, path=path, edits=edits)
            edits = []
        if uccontinue == True:
            json_data = urllib.request.urlopen(api+apiquery)
        else:
            try:
                json_data = urllib.request.urlopen(api+apiquery+'&'+uccontinue_name+'='+uccontinue)
            except:
                time.sleep(10)
                try:
                    json_data = urllib.request.urlopen(api+apiquery+'&'+uccontinue_name+'='+uccontinue)
                except:
                    uccontinue = ''
                    break
        data = json.loads(json_data.readall().decode('utf-8'))
        for edit in data['query']['usercontribs']:
            if edit['revid'] == lasteditid:
                uccontinue = ''
                break
            d = datetime.datetime.strptime(edit['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
            #d = datetime.datetime.strptime(edit['timestamp'].split('T')[0], "%Y-%m-%d")
            unixtime = d.strftime('%s')
            edits.append([edit['revid'], edit['timestamp'], edit['comment'].encode('utf-8')])
            total += 1
        json_data.close()
        if uccontinue:
            if 'query-continue' in data:
                if not uccontinue_name in data['query-continue']['usercontribs']:
                    uccontinue_name = 'ucstart'
                uccontinue = data['query-continue']['usercontribs'][uccontinue_name]
            elif 'continue' in data:
                uccontinue = data['continue'][uccontinue_name]
            else:
                uccontinue = ''
        print('%s edits' % (total))
    print('%s edits. Finished' % (total))
    if edits:
        saveEdits(nick=nick, path=path, edits=edits)
    edits = []
    
    stats = { 'edits': 0, 'aliases': 0, 'claims': 0, 'descriptions': 0, 'labels': 0, 'references': 0, 'sitelinks': 0, 'items': 0 }
    if os.path.exists('%s/%s-edits.csv' % (path, nick)):
        with open('%s/%s-edits.csv' % (path, nick), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                comment = row[2]
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) alias", comment)
                stats['aliases'] += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) claim", comment)
                stats['claims'] += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding descriptions? \(([0-9]+) languages?\)", comment)
                stats['descriptions'] += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding labels? \(([0-9]+) languages?\)", comment)
                stats['labels'] += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) reference", comment)
                stats['references'] += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) sitelink", comment)
                stats['sitelinks'] += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Creating item", comment)
                stats['items'] += m and 1 or 0
                stats['edits'] += 1
                if stats['edits'] % 1000 == 0:
                    print('%s edits analysed' % (stats['edits']))
    output = """{| class="wikitable sortable plainlinks" style="text-align: center;"
|-
| '''Edits''' || [[Special:Contributions/Emijrpbot|{{formatnum:%s}}]]
|-
| '''[[Help:Label|Labels]]''' || {{formatnum:%s}}
|-
| '''[[Help:Description|Descriptions]]''' || {{formatnum:%s}}
|-
| '''[[Help:Aliases|Aliases]]''' || {{formatnum:%s}}
|-
| '''[[Help:Statements|Claims]]''' || {{formatnum:%s}}
|-
| '''[[Help:Sitelinks|Sitelinks]]''' || {{formatnum:%s}}
|-
| '''[[Help:Items|Items]]''' || [https://www.wikidata.org/w/index.php?title=Special:NewPages&namespace=0&username=Emijrpbot {{formatnum:%s}}]
|-
| '''[[Help:Sources|References]]''' || {{formatnum:%s}}
|-
| colspan=2 | <small>Last update: %s</small>
|}""" % (stats['edits'], stats['labels'], stats['descriptions'], stats['aliases'], stats['claims'], stats['sitelinks'], stats['items'], stats['references'], datetime.datetime.now().strftime('%Y-%m-%d'))
    
    print(output)
    site = pywikibot.Site('wikidata', 'wikidata')
    page = pywikibot.Page(site, 'User:Emijrpbot/stats')
    page.text = output
    page.save('BOT - Updating stats')

if __name__ == "__main__":
    main()
