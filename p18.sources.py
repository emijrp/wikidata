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
import time

import pwb
import pywikibot
from wikidatafun import *

def main():
    sites = {
        'dewiki': pywikibot.Site('de', 'wikipedia'),
        'enwiki': pywikibot.Site('en', 'wikipedia'),
        'frwiki': pywikibot.Site('fr', 'wikipedia'),
        'itwiki': pywikibot.Site('it', 'wikipedia'),
        'jawiki': pywikibot.Site('ja', 'wikipedia'),
        'nlwiki': pywikibot.Site('nl', 'wikipedia'),
        'plwiki': pywikibot.Site('pl', 'wikipedia'),
        'ptwiki': pywikibot.Site('pt', 'wikipedia'),
        'ruwiki': pywikibot.Site('ru', 'wikipedia'),
        'svwiki': pywikibot.Site('sv', 'wikipedia'),
        'wikidata': pywikibot.Site('wikidata', 'wikidata'),
    }
    importedfroms = {
        'dewiki': 'Q48183', 
        'enwiki': 'Q328', 
        'frwiki': 'Q8447', 
        'itwiki': 'Q11920', 
        'jawiki': 'Q177837', 
        'nlwiki': 'Q10000', 
        'plwiki': 'Q1551807', 
        'ptwiki': 'Q11921', 
        'ruwiki': 'Q206855', 
        'svwiki': 'Q169514', 
    }
    wikisites = ['enwiki', 'dewiki', 'frwiki', 'itwiki', 'plwiki', 'ptwiki', 'nlwiki', 'svwiki', 'ruwiki', 'jawiki', ] #prefered order for importedfrom
    repo = sites['wikidata'].data_repository()
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP18%20%3Fimage.%0A%7D%0ALIMIT%20100%0AOFFSET%200'
    url = '%s&format=json' % (url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)
    skip = ''
    for result in json1['results']['bindings']:
        q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
        print('==', q, '==')
        if skip:
            if skip != q:
                print('Skiping until', skip)
                continue
            else:
                skip = ''
        
        item = pywikibot.ItemPage(repo, q)
        try: #to detect Redirect because .isRedirectPage fails
            item.get()
        except:
            print('Error while .get()')
            continue
        
        if 'P18' in item.claims:
            for itemimage in item.claims['P18']:
                imagefilename = itemimage.getTarget().title().split('File:')[1]
                imagefilename_r = '(?i)%s' % (imagefilename.replace(' ', '[_ ]'))
                sources = itemimage.getSources()
                if sources:
                    print('Item has sources for P18. Skiping...')
                    continue
                else:
                    print('Item doesnt have sources for P18')
                    #print(item.sitelinks)
                    for wikisite in wikisites:
                        if wikisite in item.sitelinks:
                            page = pywikibot.Page(sites[wikisite], item.sitelinks[wikisite])
                            if page.exists() and not page.isRedirectPage() and \
                               re.search(imagefilename_r, page.text):
                                print('Image "%s" found in %s "%s"' % (imagefilename.encode('utf-8'), wikisite, page.title().encode('utf-8')))
                                importedfrom = pywikibot.Claim(repo, 'P143')
                                importedwp = pywikibot.ItemPage(repo, importedfroms[wikisite])
                                importedfrom.setTarget(importedwp)
                                itemimage.addSource(importedfrom, summary='BOT - Adding 1 reference: [[Property:P143]]: [[%s]]' % (importedfroms[wikisite]))
                                break
                
    print("Finished successfully")

if __name__ == "__main__":
    main()
