#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2019 emijrp <emijrp@gmail.com>
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

import pwb
import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    method = 'all'
    if len(sys.argv) > 1:
        method = sys.argv[1]
    
    if method == 'all' or method == 'method1':
        #method 1
        skip = ''
        countryqq = [
            'Q414', #Argentina
            'Q750', #Bolivia
            'Q298', #Chile
            'Q739', #Colombia
            'Q800', #Costa Rica
            'Q241', #Cuba
            'Q786', #Dominican Republic
            'Q736', #Ecuador
            'Q792', #El Salvador
            'Q774', #Guatemala
            'Q783', #Honduras
            'Q96',  #Mexico
            'Q811', #Nicaragua
            'Q804', #Panama
            'Q733', #Paraguay
            'Q419', #Peru
            'Q29',  #Spain
            'Q77',  #Uruguay
            'Q717', #Venezuela
        ]
        for countryq in countryqq:
            query = """
            SELECT ?item
            WHERE {
                ?item wdt:P31 wd:Q5.
                ?item wdt:P27 wd:%s ;
                      wdt:P27 ?instance .
                ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
                OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
                FILTER(!BOUND(?labeles)).
            }
            GROUP BY ?item
            HAVING(COUNT(?instance) = 1)
            """ % (countryq)
            
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
    
    querylimit = 10000
    if method == 'all' or method == 'method2':
        #method 2
        queries = [
        """
        SELECT ?item
        WHERE {
            SERVICE bd:sample {
                ?item wdt:P31 wd:Q5 .
                bd:serviceParam bd:sample.limit %s .
                bd:serviceParam bd:sample.sampleType "RANDOM" .
            }
            ?item rdfs:label ?labelen .filter(lang(?labelen) = "en").
            OPTIONAL { ?item rdfs:label ?labeles filter(lang(?labeles) = "es") }.
            FILTER(!BOUND(?labeles)).
        }
        #random%s
        """ % (str(querylimit+i), random.randint(1,1000000)) for i in range(1, 10000)
        ]
        
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
                
                nameisok = True
                words = labels['en'].split(' ')
                if len(words) > 4:
                    print("Too long:")
                    print(labels['en'].encode('utf-8'))
                    continue
                if labels['en'].lower() != removeAccents(labels['en'].lower()):
                    print("Accents:")
                    print(labels['en'].encode('utf-8'))
                    continue
                for word in words:
                    word_ = word.lower().strip('.')
                    if len(word_) < 3:
                        nameisok = False
                    if word_ in ['of', 'the', 'mr', 'ms', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']:
                        nameisok = False
                    if '[' in word_ or ']' in word_ or '(' in word_ or ')' in word_:
                        nameisok = False
                
                if nameisok:
                    labels['es'] = labels['en']
                    print("OK!")
                    print(labels['en'].encode('utf-8'))
                    summary = 'BOT - Adding labels (1 languages): es'
                    data = { 'labels': labels }
                    print(summary)
                    try:
                        item.editEntity(data, summary=summary)
                    except:
                        print('Error while saving')
                        continue
                else:
                    print("Didnt pass:")
                    print(labels['en'].encode('utf-8'))

if __name__ == '__main__':
    main()
