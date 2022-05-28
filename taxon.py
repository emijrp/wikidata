#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021 emijrp <emijrp@gmail.com>
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

import random
import re
import sys
import time
import urllib.parse

import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    method = 'all'
    if len(sys.argv) > 1:
        method = sys.argv[1]
    
    targetlangs = ["es", "ast", "ca", "gl", "ext", "eu", "oc", "an", ]
    targetlangs += ["fr", "de", "it", "pt", "pt-br", "nl", "ga", "pl", ]
    targetlangs += ["eo", "io", "ia", "ie", "vo", ]
    targetlangs += ["la", ]
    targetlangs = list(set(targetlangs))
    targetlangs.sort()
    if method == 'all' or method == 'method1':
        #method 1
        for i in range(1000):
            skip = ''
            query = """
            SELECT DISTINCT ?item
            WHERE {
                SERVICE bd:sample {
                    ?item wdt:P31 wd:Q16521 .
                    bd:serviceParam bd:sample.limit 1000 .
                    bd:serviceParam bd:sample.sampleType "RANDOM" .
                }
                ?item wdt:P225 ?taxonname.
                OPTIONAL { ?item rdfs:label ?label filter(lang(?label) = "ext") }
                FILTER(!BOUND(?label))
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
            """
            
            url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
            url = '%s&format=json' % (url)
            print("Loading...", url)
            sparql = getURL(url=url)
            json1 = loadSPARQL(sparql=sparql)
            
            for result in json1['results']['bindings']:
                q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                if not q:
                    break
                print('\n== %s ==' % (q))
                if skip:
                    if q != skip:
                        print('Skiping...')
                        continue
                    else:
                        skip = ''
                
                item = pywikibot.ItemPage(repo, q)
                try: #to detect Redirect because .isRedirectPage fails
                    item.get()
                except:
                    print('Error while .get()')
                    continue
                
                labels = item.labels
                if not 'en' in labels:
                    continue
                if item.claims:
                    if not 'P225' in item.claims:
                        print("P225 not found")
                        continue
                    if 'P225' in item.claims:
                        if not labels['en'] in [claim.getTarget() for claim in item.claims['P225']]:
                            print("Label (en) not found in claim P225")
                            continue
                
                addedlangs = []
                for targetlang in targetlangs:
                    if not targetlang in labels:
                        labels[targetlang] = labels['en']
                        addedlangs.append(targetlang)
                
                if len(addedlangs) < 1:
                    continue
                addedlangs.sort()
                
                summary = 'BOT - Adding labels (%d languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                data = { 'labels': labels }
                print(summary)
                
                time.sleep(0.01)
                cronstop()
                try:
                    item.editEntity(data, summary=summary)
                except:
                    print('Error while saving')
                    continue

if __name__ == '__main__':
    main()
