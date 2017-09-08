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

import re
import sys
import time
import urllib.parse

import pwb
import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    queries = [
        
        #Q8502 mountains
        """SELECT ?item
        WHERE {
          ?item wdt:P31 wd:Q8502.
          ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
          FILTER(STRSTARTS(?labelen, 'Cerro ')).
          FILTER(!STRSTARTS(?labelen, "Cerro d'")).
          FILTER(!STRSTARTS(?labelen, 'Cerro do ')).
          OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
          FILTER(!BOUND(?labeles)).
        }""", 
        """SELECT ?item
        WHERE {
          ?item wdt:P31 wd:Q8502.
          ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
          FILTER(STRSTARTS(?labelen, 'Pico ')).
          FILTER(!STRSTARTS(?labelen, "Pico d'")).
          FILTER(!STRSTARTS(?labelen, 'Pico do ')).
          OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
          FILTER(!BOUND(?labeles)).
        }
        """,
        
        #Q4022 rivers
        """SELECT ?item
        WHERE {
          ?item wdt:P31/wdt:P279* wd:Q355304.
          ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
          FILTER(STRSTARTS(?labelen, 'Arroyo ')).
          FILTER(!STRSTARTS(?labelen, "Arroyo d'")).
          FILTER(!STRSTARTS(?labelen, 'Arroyo do ')).
          OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
          FILTER(!BOUND(?labeles)).
        }""", 
        """SELECT ?item
        WHERE {
          ?item wdt:P31/wdt:P279* wd:Q355304.
          ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
          FILTER(STRSTARTS(?labelen, 'Río ')).
          FILTER(!STRSTARTS(?labelen, "Río d'")).
          FILTER(!STRSTARTS(?labelen, 'Río do ')).
          OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
          FILTER(!BOUND(?labeles)).
        }""",
        
        #Q39816 valley
        """SELECT ?item
        WHERE {
          ?item wdt:P31 wd:Q39816.
          ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
          FILTER(STRSTARTS(?labelen, 'Valle ')).
          FILTER(!STRSTARTS(?labelen, "Valle d'")).
          FILTER(!STRSTARTS(?labelen, 'Valle do ')).
          OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
          FILTER(!BOUND(?labeles)).
        }""",
    
    ]
    skip = ''
    for query in queries:
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
            if 'es' in labels:
                continue
            if not 'en' in labels:
                continue
            
            labels['es'] = labels['en']
            summary = 'BOT - Adding labels (1 languages): es'
            data = { 'labels': labels }
            print(summary)
            try:
                item.editEntity(data, summary=summary)
            except:
                print('Error while saving')
                continue
    
if __name__ == '__main__':
    main()
