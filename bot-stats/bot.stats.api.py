#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021 emijrp <emijrp@gmail.com>
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

def calculateTopDay(days={}):
    dayslist = [[v, k] for k, v in days.items()]
    dayslist.sort(reverse=True)
    return [dayslist[0][1], dayslist[0][0]]

def main():
    path = '/data/project/emijrpbot/wikidata'
    nick = 'Emijrpbot'
    nick_ = re.sub(' ', '_', nick)
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
        data = json.loads(json_data.read().decode('utf-8'))
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
    statsbyday = { 'edits': {}, 'aliases': {}, 'claims': {}, 'descriptions': {}, 'labels': {}, 'references': {}, 'sitelinks': {}, 'items': {} }
    statsprev = { 'edits': 0, 'aliases': 0, 'claims': 0, 'descriptions': 0, 'labels': 0, 'references': 0, 'sitelinks': 0, 'items': 0 }
    site = pywikibot.Site('wikidata', 'wikidata')
    statspage = pywikibot.Page(site, 'User:Emijrpbot/stats')
    for statsprop in statsprev.keys():
        statsprev[statsprop] = int(re.findall(r"(?im)%s[^\n\{]+?{{formatnum:(\d+)}}" % (statsprop), statspage.text)[0])
    
    #848135050,2019-02-01T10:14:31Z,"/* wbeditentity-update:0| */ BOT - Adding descriptions (57 languages): ar, ast, bg, bn, ca, cs, da, de, el, eo, es, et, fa, fi, fr, gl, he, hu, hy, it, ja, ka, ko, lt, nan, nb, nn, oc, pl, pt, pt-br, ro, ru, sk, sq, sr, sr-ec, sr-el, sv, tg, tg-cyrl, th, tl, tr, ur, vi, wuu, yue, zh, zh-cn, zh-hans, zh-hant, zh-hk, zh-mo, zh-my, zh-sg, zh-tw"
    regexps = {
        'aliases': re.compile(r"(?i)BOT - Adding ([0-9]+) alias"), 
        'claims': re.compile(r"(?i)BOT - Adding ([0-9]+) claim"), 
        'descriptions': re.compile(r"(?i)BOT - Adding descriptions? \(([0-9]+) languages?\)"), 
        'labels': re.compile(r"(?i)BOT - Adding labels? \(([0-9]+) languages?\)"), 
        'references': re.compile(r"(?i)BOT - Adding ([0-9]+) reference"), 
        'sitelinks': re.compile(r"(?i)BOT - Adding ([0-9]+) sitelink"), 
        'items': re.compile(r"(?i)BOT - Creating item"), 
    }
    if os.path.exists('%s/%s-edits.csv' % (path, nick)):
        with open('%s/%s-edits.csv' % (path, nick), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                revid = row[0]
                timestamp = row[1]
                comment = row[2]
                
                day = timestamp.split('T')[0]
                for statsbydayprop in statsbyday.keys():
                    if not day in statsbyday[statsbydayprop]:
                        statsbyday[statsbydayprop][day] = 0
                
                for regexpname, regexp in regexps.items():
                    m = regexp.findall(comment)
                    if regexpname == 'items':
                        stats[regexpname] += m and 1 or 0
                        statsbyday[regexpname][day] += m and 1 or 0
                    else:
                        stats[regexpname] += m and int(m[0]) or 0
                        statsbyday[regexpname][day] += m and int(m[0]) or 0
                
                stats['edits'] += 1
                statsbyday['edits'][day] += 1
                if stats['edits'] % 1000 == 0:
                    print('%s edits analysed' % (stats['edits']))
    
    formatdict = {}
    for k, v in stats.items():
        formatdict[k] = v
        formatdict['diff'+k] = v - statsprev[k]
        topday = calculateTopDay(days=statsbyday[k])
        formatdict['topday'+k+'day'] = topday[0]
        formatdict['topday'+k+'value'] = topday[1]
    formatdict['nick'] = nick
    formatdict['nick_'] = nick_
    formatdict['lastupdate'] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    output = """{{| class="wikitable sortable plainlinks" style="text-align: center;"
! colspan=4 | Statistics for [[User:{nick}|{nick}]]
|-
! Data
! Total added
! Added today
! Top day
|-
| '''Edits''' || data-sort-value={edits} | [[Special:Contributions/Emijrpbot|{{{{formatnum:{edits}}}}}]]
| data-sort-value={diffedits} | +{{{{formatnum:{diffedits}}}}}
| data-sort-value={topdayeditsvalue} | +{{{{formatnum:{topdayeditsvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdayeditsday}&limit=100&title=Special:Contributions {topdayeditsday}])
|-
| '''[[Help:Label|Labels]]''' || data-sort-value={labels} | {{{{formatnum:{labels}}}}}
| data-sort-value={difflabels} | +{{{{formatnum:{difflabels}}}}}
| data-sort-value={topdaylabelsvalue} | +{{{{formatnum:{topdaylabelsvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdaylabelsday}&limit=100&title=Special:Contributions {topdaylabelsday}])
|-
| '''[[Help:Description|Descriptions]]''' || data-sort-value={descriptions} | {{{{formatnum:{descriptions}}}}}
| data-sort-value={diffdescriptions} | +{{{{formatnum:{diffdescriptions}}}}}
| data-sort-value={topdaydescriptionsvalue} | +{{{{formatnum:{topdaydescriptionsvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdaydescriptionsday}&limit=100&title=Special:Contributions {topdaydescriptionsday}])
|-
| '''[[Help:Aliases|Aliases]]''' || data-sort-value={aliases} | {{{{formatnum:{aliases}}}}}
| data-sort-value={diffaliases} | +{{{{formatnum:{diffaliases}}}}}
| data-sort-value={topdayaliasesvalue} | +{{{{formatnum:{topdayaliasesvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdayaliasesday}&limit=100&title=Special:Contributions {topdayaliasesday}])
|-
| '''[[Help:Statements|Claims]]''' || data-sort-value={claims} | {{{{formatnum:{claims}}}}}
| data-sort-value={diffclaims} | +{{{{formatnum:{diffclaims}}}}}
| data-sort-value={topdayclaimsvalue} | +{{{{formatnum:{topdayclaimsvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdayclaimsday}&limit=100&title=Special:Contributions {topdayclaimsday}])
|-
| '''[[Help:Sitelinks|Sitelinks]]''' || data-sort-value={sitelinks} | {{{{formatnum:{sitelinks}}}}}
| data-sort-value={diffsitelinks} | +{{{{formatnum:{diffsitelinks}}}}}
| data-sort-value={topdaysitelinksvalue} | +{{{{formatnum:{topdaysitelinksvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdaysitelinksday}&limit=100&title=Special:Contributions {topdaysitelinksday}])
|-
| '''[[Help:Items|Items]]''' || data-sort-value={items} | [https://www.wikidata.org/w/index.php?title=Special:NewPages&namespace=0&username={nick_} {{{{formatnum:{items}}}}}]
| data-sort-value={diffitems} | +{{{{formatnum:{diffitems}}}}}
| data-sort-value={topdayitemsvalue} | +{{{{formatnum:{topdayitemsvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdayitemsday}&limit=100&title=Special:Contributions {topdayitemsday}])
|-
| '''[[Help:Sources|References]]''' || data-sort-value={references} | {{{{formatnum:{references}}}}}
| data-sort-value={diffreferences} | +{{{{formatnum:{diffreferences}}}}}
| data-sort-value={topdayreferencesvalue} | +{{{{formatnum:{topdayreferencesvalue}}}}} ([https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdayreferencesday}&limit=100&title=Special:Contributions {topdayreferencesday}])
|-
! colspan=4 | <small>Last update: {lastupdate}</small>
|}}""".format(**formatdict)
    summary = "BOT - Updating stats: Edits ({diffedits}+), Labels ({difflabels}+), Descriptions ({diffdescriptions}+), Aliases ({diffaliases}+), Claims ({diffclaims}+), Sitelinks ({diffsitelinks}+), Items ({diffitems}+), References ({diffreferences}+)".format(**formatdict)
    print(output)
    statspage.text = output
    statspage.save(summary)

if __name__ == "__main__":
    main()
