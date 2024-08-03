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
    
    for loop in range(10):
        time.sleep(5)
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
                        if filepage.isRedirectPage():
                            filepage = filepage.getRedirectTarget()
                        print(filepage.full_url())
                        mid = "M" + str(filepage.pageid)
                        print(mid)
                        
                        #exclude images probably not portraits
                        personnames = []
                        for labellang in item.labels:
                            #cierta logintud, al menos un espacio (dos palabras) y solo los caracteres indicados
                            if len(item.labels[labellang]) >= 8 and ' ' in item.labels[labellang] and not re.search(r"(?im)[^a-záéíóúàèìòùäëïöüçñ\,\.\- ]", item.labels[labellang]):
                                personnames.append(item.labels[labellang])
                        personnames = list(set(personnames))
                        isportrait = False
                        for personname in personnames:
                            symbols = "[0-9\-\.\,\!\¡\"\$\&\(\)\*\?\¿\~\@\= ]*?"
                            #primero convierto los puntos, comas, rayas, en espacios, pq hay puntos etc en symbols
                            personnamex = personname.replace(".", " ").replace(",", " ").replace("-", " ")
                            personnamex = personnamex.replace(" ", symbols)
                            portraitregexp = r"(?im)^File:%s(%s|%s)%s\.(?:jpe?g|gif|png|tiff?)$" % (symbols, personname, personnamex, symbols)
                            regexpmonths = "(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|apr|jun|jul|aug|sept?|oct|nov|dec)"
                            regexpdays = "(([012]?\d|3[01])(st|nd|rd|th))"
                            filenameclean = re.sub(r"(?im)\b(cropp?e?d?|rotated?|portrait|before|after|cut|sir|prince|dr|in|on|at|en|circa|c|rev|img|image|pic|picture|photo|photography|the|[a-z]+\d+|\d+[a-z]+|%s|%s)\b" % (regexpdays, regexpmonths), "", filename.title())
                            #print(portraitregexp)
                            if re.search(portraitregexp, filenameclean):
                                isportrait = True
                                break
                        if not isportrait:
                            print("Puede que no sea retrato, saltamos")
                            continue
                        
                        claims = getClaims(site=sitecommons, mid=mid)
                        if not claims:
                            print("Error al recuperar claims, saltamos")
                            continue
                        elif claims and "claims" in claims and claims["claims"] == { }:
                            print("No tiene claims, no inicializado, inicializamos")
                        
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

#si este script va bien, pedir autorizacion para hacer lo mismo con taxon, edificios, iglesias, etc, ver ideas en https://query.wikidata.org/#SELECT%20%3Fp31%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%20%20%20%20SERVICE%20bd%3Asample%20%7B%0A%20%20%20%20%20%20%3Fitem%20wdt%3AP18%20%3Fimage.%0A%20%20%20%20%20%20bd%3AserviceParam%20bd%3Asample.limit%20120000%20.%0A%20%20%20%20%20%20bd%3AserviceParam%20bd%3Asample.sampleType%20%22RANDOM%22%20.%0A%20%20%20%20%7D%0A%20%20%20%20%3Fitem%20wdt%3AP31%20%3Fp31.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Ces%22.%20%7D%0A%7D%0AGROUP%20BY%20%3Fp31%0AORDER%20BY%20DESC%28%3Fcount%29

#tb hacer este https://commons.wikimedia.org/wiki/Commons:Bots/Requests/Emijrpbot_12
#para las descs q sean simplemente un ^[[link]]\.?$, o sean ^The [[link]], o ^[[link]] viewed https://en.wikipedia.org/w/index.php?title=Murray_River&oldid=1231417560#Murray_mouth

#despues otro para las imagenes en categorias de commons con el nombre PERSONA in YEAR, cuidado con este q no tiene pq ser prominent, puede haber mas de una persona en la foto
