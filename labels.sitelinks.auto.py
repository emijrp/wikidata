#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2022-2023 emijrp <emijrp@gmail.com>
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

import os
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
    langs = ["de", "en", "es", "fr", "pt", "it"]
    random.shuffle(langs)
    for i in range(10000):
        for lang in langs:
            query1 = """
        SELECT DISTINCT ?item
        WHERE {
            SERVICE bd:sample {
               ?item wdt:P31 ?p31 .
               bd:serviceParam bd:sample.limit 100000 .
               bd:serviceParam bd:sample.sampleType "RANDOM" .
            }
            FILTER EXISTS {
               ?article schema:about ?item .
               ?article schema:inLanguage "%s" .
               ?article schema:isPartOf <https://%s.wikipedia.org/> .
            }
            OPTIONAL { ?item rdfs:label ?label filter(lang(?label) = "%s"). }
            FILTER(!BOUND(?label)) .
        }
        #%s""" % (lang, lang, lang, random.randint(1000000, 9999999))
            url1 = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query1))
            url1 = '%s&format=json' % (url1)
            #print("Loading...", url1)
            sparql1 = getURL(url=url1)
            json1 = loadSPARQL(sparql=sparql1)
            for result1 in json1['results']['bindings']:
                time.sleep(0.5)
                q = 'item' in result1 and result1['item']['value'].split('/entity/')[1] or ''
                if not q:
                    continue
                item = pywikibot.ItemPage(repo, q)
                try: #to detect Redirect because .isRedirectPage fails
                    item.get()
                except:
                    print('Error while .get()')
                    continue
                
                langwiki = "%swiki" % (lang)
                if not langwiki in item.sitelinks:
                    print("No tiene sitelink %s:" % (langwiki))
                    continue
                labelcandidate = str(item.sitelinks[langwiki])
                labelcandidate = re.sub(r'(?im)[\[\]]', '', labelcandidate)
                print(labelcandidate)
                if re.search(r"(?im)[\,\.\-\/\(\)]", labelcandidate):
                    print("Sitelink contains weird chars, skiping...")
                    continue
                
                itemlabels = item.labels
                if not lang in itemlabels.keys():
                    itemlabels[lang] = labelcandidate
                    data = { 'labels': itemlabels }
                    summary = 'BOT - Adding labels (1 languages): %s' % (lang)
                    print(q, summary)
                    try:
                        print(summary)
                        item.editEntity(data, summary=summary)
                        #break
                    except:
                        print('Error while saving')
                        continue
    print("Finished successfully") 

if __name__ == "__main__":
    main()
