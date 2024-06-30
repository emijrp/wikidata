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

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    number2month = { 1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December" }
    
    for loop in range(100):
        time.sleep(10)
        #le tengo puesto en la query que sean solo personas vivas, pq a veces las fechas de las fotos en commons están mal y pone pointintimte 20XX para gente que murió hace décadas. Otra forma sería controlar q la fecha fallecimiento si la hay sea superior a la fecha de la foto
        #posteriormente añado que hayan nacido desde 1950 (antes empezaba en 1900), para quitar mas casos de fotos antiguas
        #https://www.wikidata.org/w/index.php?diff=2181498523
        #https://commons.wikimedia.org/w/index.php?title=&oldid=882216141
        querywd = """
        SELECT DISTINCT ?item
        WHERE {
          SERVICE bd:sample {
            ?item wdt:P31 wd:Q5 .
            bd:serviceParam bd:sample.limit 100000 .
            bd:serviceParam bd:sample.sampleType "RANDOM" .
          }
          ?item p:P18 ?p18.
          OPTIONAL { ?p18 pq:P585 ?pointintime. }
          FILTER(!BOUND(?pointintime))
          
          ?item wdt:P569 ?birthdate.
          FILTER (?birthdate >= "1950-01-01"^^xsd:dateTime && ?birthdate < "2000-01-01"^^xsd:dateTime).
          
          OPTIONAL { ?item wdt:P570 ?deathdate. }
          FILTER(!BOUND(?deathdate)).
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
            
            item = pywikibot.ItemPage(repo, q)
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
                        if p18claim.qualifiers and 'P585' in p18claim.qualifiers: #p585 point in time
                            print("Ya tiene point in time P585, saltamos")
                            continue
                        filename = p18claim.getTarget()
                        print(filename.title())
                        commonsfileurl = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(filename.title().replace(" ", "_"))
                        print(commonsfileurl)
                        raw = getURL(url=commonsfileurl)
                        #cuidado con los parametros generados para quickstatements, esta foto no tiene SDC inception pero tiene un P571 generado al vuelo, los excluyo parseando desde "P571":[{"mainsnak":  https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_183-1987-0411-019,_1._FC_Union_Berlin_-_FC_Karl-Marx-Stadt_4-2.jpg
                        m = re.findall(r'(?im)"P571":\[\{"mainsnak":[^Z]*?(\d\d\d\d-\d\d-\d\d)T', raw)
                        year = ""
                        month = ""
                        day = ""
                        if m and len(m) == 1:
                            pointintime = m[0]
                            if pointintime.endswith("-00") or pointintime.endswith("-01"):
                                print("Probable fecha redondeada, saltamos")
                                continue
                            
                            year = int(pointintime.split('-')[0])
                            month = int(pointintime.split('-')[1])
                            day = int(pointintime.split('-')[2])
                            
                            #comparar SDC inception con los metadatos de la foto, sino tiene metadatos o no coincide, saltamos
                            #ejemplo https://commons.wikimedia.org/wiki/File%3AGustavBergmann_berg1.jpg
                            metadata = r'(?im)<tr class="exif-datetimeoriginal"><th>Date and time of data generation</th><td>\d\d:\d\d, %d %s %d</td></tr>' % (day, number2month[month], year)
                            #print(raw)
                            #print(metadata)
                            if not re.search(metadata, raw):
                                print("No coincide con metadata, saltamos")
                                continue
                            
                            #no es una camara digital, (posible scan? analógica? saltamos)
                            if not re.search(r"(?im)<th>Camera manufacturer</th>", raw):
                                print("No es una camara digital")
                                continue
                            
                            #comparar con la fecha de la infobox, sino coincide saltamos
                            if not re.search(r"(?im)\|\s*date\s*=\s*%s" % (pointintime), filename.text):
                                print("No coincide con infobox date, saltamos")
                                continue
                        else:
                            print("Inception not found, skiping")
                            continue
                        
                        if year and month and day:
                            print("Adding pointintime", pointintime)
                            qualifierP585 = pywikibot.Claim(repo, "P585")
                            qualifierP585.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
                            p18claim.addQualifier(qualifierP585, summary="BOT - Adding 1 qualifier")
                            time.sleep(1)
                    
if __name__ == '__main__':
    main()
