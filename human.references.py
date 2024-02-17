#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2024 emijrp <emijrp@gmail.com>
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

import datetime
import random
import re
import sys
import time
import urllib

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    queries = [
    """
    SELECT ?item
    WHERE {
      SERVICE bd:sample {
        ?item wdt:P950 ?id. #P950 BNE id
        bd:serviceParam bd:sample.limit 10000 .
        bd:serviceParam bd:sample.sampleType "RANDOM" .
      }
      ?item wdt:P31 wd:Q5.
    }
    #random%d
    """ % (random.randint(1000000, 9999999))
    ]
    for query in queries:
        time.sleep(1)
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
        url = '%s&format=json' % (url)
        print("Loading...", url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        itembne = pywikibot.ItemPage(repo, "Q50358336")
        itembnf = pywikibot.ItemPage(repo, "Q19938912")
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            #bneid = 'bneid' in result and result['item']['value'] or ''
            if not q:
                break
            print('\n== %s ==' % (q))
            item = pywikibot.ItemPage(repo, q)
            try: #to detect Redirect because .isRedirectPage fails
                item.get()
            except:
                print('Error while .get()')
                continue
            
            today = datetime.date.today()
            year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
            #human
            bneinref = False
            bnfinref = False
            if 'P31' in item.claims and len(item.claims['P31']) == 1:
                #print(item.claims['P31'][0].getTarget())
                sources = item.claims['P31'][0].getSources()
                for source in sources:
                    #print(source)
                    if ("P248" in source and source["P248"][0].getTarget() == itembne) or \
                       ("P950" in source) or \
                       ("P854" in source and "bne.es" in source["P854"][0].getTarget()):
                        bneinref = True
                    if ("P248" in source and source["P248"][0].getTarget() == itembnf) or \
                       ("P268" in source) or \
                       ("P854" in source and "bnf.fr" in source["P854"][0].getTarget()):
                        bnfinref = True
            else:
                print("Not a Q5")
                continue
            """
            if bnfinref:
                print("Ya tiene BNF en referencia")
            else:
                print("NO tiene BNF en referencia")
            """
            if bneinref:
                print("Ya tiene BNE en referencia, skiping")
                continue
            else:
                print("NO tiene BNE en referencia")
            
            bneid = ""
            if 'P950' in item.claims:
                if len(item.claims['P950']) == 1:
                    bneid = item.claims['P950'][0].getTarget()
                    print(bneid)
                else:
                    print("More than one ID, skiping")
                    continue
            else:
                print("No tiene BNE id, skiping")
                continue
            
            if not bneid:
                print("No BNE id, skiping")
                continue
            if not bneid.startswith("XX"):
                print("BNE ID not starts with XX, skiping")
                continue
            
            claim = item.claims['P31'][0]
            refstatedinclaim = pywikibot.Claim(repo, 'P248')
            refstatedinclaim.setTarget(itembne)
            refretrieveddateclaim = pywikibot.Claim(repo, 'P813')
            refretrieveddateclaim.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
            refbneidclaim = pywikibot.Claim(repo, 'P950')
            refbneidclaim.setTarget(bneid)
            claim.addSources([refstatedinclaim, refretrieveddateclaim, refbneidclaim], summary='BOT - Adding 1 reference')
            print("Adding reference to claim")

if __name__ == "__main__":
    main()
