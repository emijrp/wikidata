#!/usr/bin/env python
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

import datetime
import os
import pickle
import random
import re
import sys
import time
import unicodedata
import urllib.request

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

lang2langname = {
    "ca": "catalan",
    "en": "english",
    "es": "spanish",
    "fr": "french", 
    "it": "italian", 
}
lang2q = {
    "ca": "Q7026", 
    "cat": "Q7026", 
    "en": "Q1860", 
    "es": "Q1321", 
    "fr": "Q150", 
    "it": "Q652", 
}
regexpsbylang = {
    "ca": r"(?im)\b(i|els|les)\b", 
    "es": r"(?im)\b(un|una|unos|unas|el|la|los|las|ante|con|para|por|de|del|muy|que|este|esta|nuestro|nuestra)\b",
    "fr": r"(?im)\b(et|le|vous|au|ou|pour|nos)\b",
    "it": r"(?im)\b(di|il|le|per)\b",
}

def getLocalizedVersions(html=""):
    #pending
    """
    <link hreflang="en" href="https://www.memory-of-mankind.com/en/" rel="alternate" />
    <link hreflang="de" href="https://www.memory-of-mankind.com/de/" rel="alternate" />
    <link hreflang="x-default" href="https://www.memory-of-mankind.com/" rel="alternate" />
    """
    localizedversions = re.findall(r"(?im)<link [^<>]*?hreflang=[\"\']([a-z]{2}(?:-[a-z]{2}))[\"\'][^<>]*? href=[\"\']([^<>]+?)[\"\'][^<>]*?>", html)
    print(localizedversions)
    return

def htmllangtags(html="", targetlang=""):
    if not html or not targetlang:
        return False
    
    if re.search(r"(?im)<html[^<>]*? lang\s*=\s*[\'\"]?(%s)[\'\"]?[^<>]*>" % (targetlang), html) or \
       re.search(r"(?im)<meta[^<>]*? name=[\'\"]language[\'\"][^<>]*? content=[\'\"](%s|%s|%s-)[\'\"]\s*/>" % (lang2langname[targetlang], targetlang, targetlang), html):
        return True
    return False

def detectLanguage(html=""):
    if not html:
        return
    langs = ["es", "ca", "fr", "it"] #priority
    detectedlang = ""
    for lang in langs:
        if htmllangtags(html=html, targetlang=lang) and len(re.findall(regexpsbylang[lang], html)) >= 10:
            detectedlang = lang
            break
    return detectedlang

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    skip = ""
    
    targetdomainsuffixes = ["it"]
    for targetdomainsuffix in targetdomainsuffixes:
        for i in range(100000):
            time.sleep(1)
            queries = [
            """
            SELECT DISTINCT ?item
            WHERE {
              SERVICE bd:sample {
                ?item wdt:P856 ?web.
                bd:serviceParam bd:sample.limit 10000 .
                bd:serviceParam bd:sample.sampleType "RANDOM" .
              }
              ?item wdt:P31/wdt:P279* wd:Q82794.
              MINUS { ?web pq:P407 ?weblang. } .
              FILTER(STRENDS(STR(?web), '.%s')) .
              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
            #random%s
            """ % (targetdomainsuffix, random.randint(1,1000000)),
            """
            SELECT DISTINCT ?item
            WHERE {
              SERVICE bd:sample {
                ?item wdt:P856 ?web.
                bd:serviceParam bd:sample.limit 10000 .
                bd:serviceParam bd:sample.sampleType "RANDOM" .
              }
              ?item wdt:P31/wdt:P279* wd:Q82794.
              MINUS { ?web pq:P407 ?weblang. } .
              FILTER(STRENDS(STR(?web), '.%s/')) .
              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
            #random%s
            """ % (targetdomainsuffix, random.randint(1,1000000))
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
                    if skip:
                        if q != skip:
                            print('Skiping...')
                            continue
                        else:
                            skip = ''
                    
                    print("https://www.wikidata.org/wiki/%s" % (q))
                    item = pywikibot.ItemPage(repo, q)
                    try: #to detect Redirect because .isRedirectPage fails
                        item.get()
                    except:
                        print('Error while .get()')
                        continue
                    
                    if item.claims:
                        if not 'P856' in item.claims:
                            print("P528 not found, skiping")
                            continue
                        if 'P856' in item.claims and len(item.claims["P856"]) != 1:
                            print("More than one website, skiping")
                            continue
                    else:
                        print("No claims found, skiping")
                        continue
                    
                    if len(item.claims["P856"][0].qualifiers) > 0:
                        print("Tiene qualifiers, skiping")
                        continue
                    
                    website = item.claims["P856"][0].getTarget()
                    print("Analizando", website)
                    html = getURL(url=website, retry=False, timeout=10)
                    weblang = detectLanguage(html=html)
                    if weblang:
                        if weblang in lang2q.keys() and weblang == targetdomainsuffix:
                            print("Detectado como idioma", weblang)
                            qualifierlang = pywikibot.Claim(repo, "P407")
                            targetlangitem = pywikibot.ItemPage(repo, lang2q[weblang])
                            qualifierlang.setTarget(targetlangitem)
                            item.claims["P856"][0].addQualifier(qualifierlang, summary="BOT - Adding 1 qualifier")
                            
                            #add other languages if available and different
                            #getLocalizedVersions(html=html)
                        else:
                            print("Idioma desconocido", weblang, "skiping")
                            continue
                    else:
                        print("No se pudo detectar idioma, skiping")
                        continue
            
if __name__ == "__main__":
    main()
