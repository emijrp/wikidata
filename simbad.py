#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 emijrp <emijrp@gmail.com>
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

constellations = [
    "Q6940204", 
    "Q8667", 
    "Q8675", 
    "Q8860", 
    "Q10441", 
    "Q10457", 
    "Q10435", 
    "Q10481", 
    "Q10574", 
    "Q10571", 
    "Q10473", 
    "Q10563", 
    "Q10578", 
    "Q8921", 
    "Q8842", 
    "Q10580", 
    "Q8679", 
    "Q10517", 
    "Q10448", 
    "Q8837", 
    "Q8853", 
    "Q10576", 
    "Q10535", 
    "Q10584", 
    "Q8923", 
    "Q8913", 
    "Q10511", 
    "Q10546", 
    "Q10464", 
    "Q9256", 
    "Q10484", 
    "Q10416", 
    "Q9289", 
    "Q10513", 
    "Q10428", 
    "Q10586", 
    "Q8839", 
    "Q8844", 
    "Q8849", 
    "Q9285", 
    "Q10470", 
    "Q10538", 
    "Q10486", 
    "Q10542", 
    "Q10503", 
    "Q10521", 
    "Q10446", 
    "Q9302", 
    "Q9286", 
    "Q10529", 
    "Q8864", 
    "Q8906", 
    "Q10476", 
    "Q10443", 
    "Q10437", 
    "Q9253", 
    "Q8865", 
    "Q10406", 
    "Q10425", 
    "Q8866", 
    "Q10403", 
    "Q10433", 
    "Q10468", 
    "Q10508", 
    "Q10498", 
    "Q10515", 
    "Q10506", 
    "Q10582", 
    "Q10488", 
    "Q9282", 
    "Q10430", 
    "Q8910", 
    "Q10413", 
    "Q10452", 
    "Q10422", 
    "Q10492", 
    "Q10570", 
    "Q8918", 
    "Q9251", 
    "Q10409", 
    "Q9305", 
    "Q10450", 
    "Q10478", 
    "Q10519", 
    "Q10565", 
    "Q8832", 
    "Q10438", 
    "Q10567", 
    "Q10525", 
]

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
        random.shuffle(constellations)
        for constellation in constellations:
            skip = ''
            query = """
            SELECT DISTINCT ?item
            WHERE {
                #?item wdt:P31 wd:Q523.
                ?item wdt:P3083 ?simbadid.
                ?item wdt:P59 wd:%s.
                OPTIONAL { ?item rdfs:label ?label filter(lang(?label) = "ext") }
                FILTER(!BOUND(?label))
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
            """ % (constellation)
            
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
                    if not 'P528' in item.claims:
                        print("P528 not found")
                        continue
                    if 'P528' in item.claims:
                        if not labels['en'] in [claim.getTarget() for claim in item.claims['P528']]:
                            print("Label (en) not found in claim P528")
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
