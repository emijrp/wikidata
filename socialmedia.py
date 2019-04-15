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

import os
import re
import sys
import urllib.parse

import pwb
import pywikibot
from wikidatafun import *

def youtubeIsDuplicate(canonical=''):
    query = """
    SELECT (COUNT(?item) AS ?count)
    WHERE {
        ?item wdt:P2397 ?youtube.
        BIND("%s" AS ?youtube).
    }
    """ % (canonical)
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
    url = '%s&format=json' % (url)
    #print("Loading...", url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)    
    for result in json1['results']['bindings']:
        count = int(result['count']['value'])
        print("Youtube usage count:", count)
        if count > 0:
            return True
    return False
    
def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    skip = ''
    queries = [
    """
    SELECT ?item ?website
    WHERE {
        ?item wdt:P31 wd:Q5.
        ?item wdt:P106 wd:Q177220.
        ?item wdt:P856 ?website.
        OPTIONAL { ?item wdt:P2397 ?youtube. }
        FILTER(!BOUND(?youtube)).
    }
    """
    ]
    for query in queries:
        time.sleep(1)
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
        url = '%s&format=json' % (url)
        print("Loading...", url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            website = result['website']['value']
            if not q or not website:
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
            
            html = getURL(url=website, retry=False)
            
            #youtube
            if not 'P2397' in item.claims:
                m = re.findall(r"(?im)https?://www\.youtube\.com/(?:user|channel)/[^/\'\"\.<>\?\n\r ]+", html)
                m = list(set(m))
                if m and len(m) == 1:
                    print(m)
                    youtube = m[0]
                    html2 = getURL(url=youtube, retry=False)
                    youtubecanonical = re.findall(r'<meta property="og:url" content="https://www.youtube.com/channel/([^/\'\"\.<>\?\n\r ]+)">', html2)[0]
                    print(youtubecanonical)
                    if not youtubeIsDuplicate(canonical=youtubecanonical):
                        youtubetitle = re.findall(r'<meta property="og:title" content="([^<>\n\r]+?)">', html2)[0]
                        youtubeclaim = pywikibot.Claim(repo, 'P2397')
                        youtubeclaim.setTarget(youtubecanonical)
                        item.addClaim(youtubeclaim, summary='BOT - Adding 1 claim: %s https://www.youtube.com/channel/%s' % (youtubetitle, youtubecanonical))
                        youtuberefclaim = pywikibot.Claim(repo, 'P854') # dirección web de la referencia (P854) 
                        youtuberefclaim.setTarget(website)
                        youtubeclaim.addSource(youtuberefclaim, summary='BOT - Adding 1 reference')

if __name__ == '__main__':
    main()
