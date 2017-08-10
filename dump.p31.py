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

import bz2
import json
import time

import pywikibot

def main():
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    p31 = {}
    c = 0
    t1 = time.time()
    dumpdate = '20170807'
    f = bz2.open('/public/dumps/public/wikidatawiki/entities/%s/wikidata-%s-all.json.bz2' % (dumpdate, dumpdate), 'r')
    for line in f:
        line = line.decode('utf-8')
        line = line.strip('\n').strip(',')
        if line.startswith('{') and line.endswith('}'):
            json1 = json.loads(line)
            q = json1['id']
            if 'claims' in json1:
                if 'P31' in json1['claims']:
                    for x in json1['claims']['P31']:
                        p31x = ''
                        if 'mainsnak' in x and \
                           'datavalue' in x['mainsnak'] and \
                           'value' in x['mainsnak']['datavalue'] and \
                           'id' in x['mainsnak']['datavalue']['value']:
                            p31x = x['mainsnak']['datavalue']['value']['id']
                        else:
                            continue
                        if p31x:
                            #print(q, 'P31', p31x)
                            if p31x in p31:
                                p31[p31x] += 1
                            else:
                                p31[p31x] = 1
        c += 1
        if c % 1000 == 0:
            print(c, time.time()-t1)
            t1 = time.time()
    
    p31list = [[y, x] for x, y in p31.items()]
    p31list.sort(reverse=True)
    rows = []
    c = 1
    for x, y in p31list[:1000]:
        rows.append('| %s || {{Q|%s}} || %s ' % (c, y, x))
        c += 1
    rows = '\n|-\n'.join(rows)
    table = """
{| class="wikitable sortable"
! # !! {{P|P31}} !! Frequency  
|-
%s
|}""" % (rows)
    page = pywikibot.Page(wdsite, 'User:Emijrp/sandbox2')
    page.text = table
    page.save('BOT - Updating table')
    #with open('dump.p31.txt', 'w') as f:
    #    f.write(output)

if __name__ == '__main__':
    main()
