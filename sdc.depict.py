#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 emijrp <emijrp@gmail.com>
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

def getClaims(site, mid):
    payload = {
      'action' : 'wbgetclaims',
      'format' : 'json',
      'entity' : mid,
    }
    request = site.simple_request(**payload)
    try:
        r = request.submit()
        #return json.loads(r)
        return r
    except:
        print("ERROR wbgetclaims")
    return {}

def addClaims(site, mid, claims, comments, q):
    #https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim
    csrf_token = site.tokens['csrf']
    data = '{"claims":[%s]}' % (",".join(claims))
    comments.sort()
    payload = {
      'action' : 'wbeditentity',
      'format' : 'json',
      'id' : mid,
      'data' : data,
      'token' : csrf_token,
      'bot' : True, 
      'summary': "BOT - Adding [[Commons:Structured data|structured data]] based on Wikidata item [[:d:%s|%s]]: %s" % (q, q, ", ".join(comments)),
      'tags': 'BotSDC',
    }
    request = site.simple_request(**payload)
    try:
      r = request.submit()
    except:
      print("ERROR while saving")

def main():
    sitewd = pywikibot.Site('wikidata', 'wikidata')
    sitecommons = pywikibot.Site('commons', 'commons')
    repowd = sitewd.data_repository()
    querywd = """
    SELECT DISTINCT ?item
    WHERE {
      SERVICE bd:sample {
        ?item wdt:P31 wd:Q5 .
        bd:serviceParam bd:sample.limit 100000 .
        bd:serviceParam bd:sample.sampleType "RANDOM" .
      }
      ?item p:P18 ?p18.
    }
    LIMIT 10000
    #random%s
    """ % (random.randint(1,1000000))
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(querywd))
    url = '%s&format=json' % (url)
    print("Loading...", url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)
    
    for result in json1['results']['bindings']:
        q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
        if not q:
            break
        print('\n== %s ==' % (q))
        
        item = pywikibot.ItemPage(repowd, q)
        try: #to detect Redirect because .isRedirectPage fails
            item.get()
        except:
            print('Error while .get()')
            continue
        
        if item.claims:
            if not 'P18' in item.claims:
                print("P18 not found")
                continue
            if 'P18' in item.claims:
                for p18claim in item.claims['P18']: #p18 image
                    filename = p18claim.getTarget()
                    print(filename.title())
                    filepage = pywikibot.Page(sitecommons, filename.title())
                    print(filepage.full_url())
                    mid = "M" + str(filepage.pageid)
                    print(mid)
                    
                    #exclude images porbably not portraits
                    personnames = []
                    for labellang in item.labels:
                        if len(item.labels[labellang]) >= 10 and ' ' in item.labels[labellang] and not re.search(r"(?im)[^a-z ]", item.labels[labellang]):
                            personnames.append(item.labels[labellang])
                    personnames = list(set(personnames))
                    isportrait = False
                    for personname in personnames:
                        symbols = "[0-9\-\.\,\!\"\$\&\(\) ]*?"
                        personnamex = personname.replace(".", " ") #primero convierto los puntos en espacios, pq hay puntos en symbols
                        personnamex = personnamex.replace(" ", symbols)
                        portraitregexp = r"(?im)^File:%s(%s|%s)%s(in|en|at|on)?%s\.jpe?g$" % (symbols, personname, personnamex, symbols, symbols)
                        #print(portraitregexp)
                        if re.search(portraitregexp, filename.title()):
                            isportrait = True
                            break
                    if not isportrait:
                        print("Puede que no sea retrato, saltamos")
                        continue
                    
                    claims = getClaims(site=sitecommons, mid=mid)
                    if not claims:
                        print("No tiene claims, no inicializado, saltamos")
                        continue
                    
                    if "claims" in claims:
                        if "P180" in claims["claims"]: #p180 depicts
                            print("Ya tiene claim depicts, saltamos")
                            continue
                        else:
                            claimstoadd = []
                            comments = []
                            depictsclaim = """{ "mainsnak": { "snaktype": "value", "property": "P180", "datavalue": {"value": {"entity-type": "item", "numeric-id": "%s", "id": "%s"}, "type":"wikibase-entityid"} }, "type": "statement", "rank": "preferred" }""" % (q[1:], q)
                            claimstoadd.append(depictsclaim)
                            comments.append("depicts")
                            
                            if claimstoadd and comments and len(claimstoadd) == len(comments):
                                addClaims(site=sitecommons, mid=mid, claims=claimstoadd, comments=comments, q=q)

if __name__ == '__main__':
    main()
