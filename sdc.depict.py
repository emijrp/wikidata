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
from pywikibot import pagegenerators
from wikidatafun import *

def isPortrait(itemlabels="", filename=""):
    if not itemlabels or not filename:
        return False
    
    isportrait = False
    personnames = []
    for labellang in itemlabels:
        #cierta logintud, al menos un espacio (dos palabras) y solo los caracteres indicados
        if len(itemlabels[labellang]) >= 8 and ' ' in itemlabels[labellang] and not re.search(r"(?im)[^a-záéíóúàèìòùäëïöüçñ\,\.\- ]", itemlabels[labellang]):
            personnames.append(itemlabels[labellang])
    personnames = list(set(personnames))
    
    for personname in personnames:
        symbols = "[0-9\-\.\,\!\¡\"\$\&\(\)\*\?\¿\~\@\= ]*?"
        #primero convierto los puntos, comas, rayas, en espacios, pq hay puntos etc en symbols
        personnamex = personname.replace(".", " ").replace(",", " ").replace("-", " ")
        personnamex = personnamex.replace(" ", symbols)
        andregexp = "(.{5,} (?:and|y|et|und) %s|%s (?:and|y|et|und) .{5,}|.{5,} (?:and|y|et|und) %s|%s (?:and|y|et|und) .{5,})" % (personname, personname, personnamex, personnamex)
        commaregexp = "(.{5,} ?(?:,|-|&) ?%s|%s ?(?:,|-|&) ?.{5,}|.{5,} ?(?:,|-|&) ?%s|%s  ?(?:,|-|&) ?.{5,})" % (personname, personname, personnamex, personnamex)
        withregexp = "(.{5,} (?:with|con|avec|mit) %s|%s (?:with|con|avec|mit) .{5,}|.{5,} (?:with|con|avec|mit) %s|%s (?:with|con|avec|mit) .{5,})" % (personname, personname, personnamex, personnamex)
        byregexp = "(%s (?:by|por) .{5,}|%s (?:by|por) .{5,})" % (personname, personnamex)
        verbregexp = "(%s [a-z]{2,}ing .*|%s [a-z]{2,}ing .*|%s [a-z]{2,}ed .*|%s [a-z]{2,}ed .*|%s [a-z]{2,}s .*|%s [a-z]{2,}s .*)" % (personname, personnamex, personname, personnamex, personname, personnamex)
        portraitregexp = r"(?im)^File:%s(%s|%s|%s|%s|%s|%s|%s)%s\.(?:jpe?g|gif|png|tiff?)$" % (symbols, personname, personnamex, andregexp, commaregexp, withregexp, byregexp, verbregexp, symbols)
        regexpmonths = "(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|apr|jun|jul|aug|sept?|oct|nov|dec|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|ene|feb|mar|abr|may|jun|jul|ago|sept?|oct|nov|dic)"
        regexpdays = "(([012]?\d|3[01])(st|nd|rd|th))"
        filenameclean = re.sub(r"(?im)\b(cropp?e?d?|recortad[oa]|rotated?|rotad[oa]|portrait|retrato|before|antes|after|despu[eé]s|cut|sr|sir|prince|dr|in|on|at|en|circa|c|rev|img|imagen?|pics?|pictures?|photos?|photographs?|fotos?|fotograf[íi]as?|head[ -]shots?|b ?&? ?w|colou?r|the|[a-z]|[a-z]+\d+[a-z0-9]*|\d+[a-z]+[a-z0-9]*|%s|%s)\b" % (regexpdays, regexpmonths), "", filename)
        #print(portraitregexp)
        if re.search(portraitregexp, filename) or re.search(portraitregexp, filenameclean):
            isportrait = True
            return isportrait
    
    return isportrait

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
                        if re.search(r"(?im)(artwork|painting|statue|coin|numism)", filepage.text):
                            print("Obra de arte, saltamos")
                            continue
                        
                        #add depict to the Commons image used in the item's P18
                        if isPortrait(itemlabels=item.labels, filename=filename.title()):
                            summary = "BOT - Adding [[Commons:Structured data|structured data]] based on Wikidata item [[:d:%s|%s]]: depicts" % (q, q)
                            addP180Claim(site=sitecommons, mid=mid, q=q, rank="preferred", overwritecomment=summary) #prominent
                        else:
                            print("Puede que no sea retrato, saltamos")
                
                #explore commonscat for this person by year, if exists
                if 'P373' in item.claims: #commonscat
                    commonscat = item.claims['P373'][0].getTarget()
                    commonscatbyyear = pywikibot.Category(sitecommons, "%s by year" % (commonscat))
                    if not commonscatbyyear.exists():
                        print("No existe", commonscatbyyear.title())
                        continue
                    print("->", commonscatbyyear.title())
                    for subcat in commonscatbyyear.subcategories():
                        print(subcat.title())
                        for subcatfilename in subcat.articles(recurse=0, namespaces=[6]): #recursivo 0 subnivel, solo las PERSON_IN_YEAR, algunas subcats de ellas son interesantes pero otras provocan falsos positivos
                            if re.search(r"(?im)(artwork|painting|statue|coin|numism)", subcatfilename.text):
                                print("Obra de arte, saltamos")
                                continue
                            #es necesario filtrar las imagenes con isPortrait() pq hay documentos en jpg, pdfs, etc, q no son fotos de personas
                            #no se puede añadir el depict a todos los ficheros de la subcategoria a lo loco
                            if isPortrait(itemlabels=item.labels, filename=subcatfilename.title()):
                                print("-->", subcatfilename.title())
                                subcatfilemid = "M" + str(subcatfilename.pageid)
                                print(subcatfilemid)
                                summary = "BOT - Adding [[Commons:Structured data|structured data]] based on Wikidata item [[:d:%s|%s]] and Commons category [[%s]]: depicts" % (q, q, subcat.title())
                                addP180Claim(site=sitecommons, mid=subcatfilemid, q=q, rank="normal", overwritecomment=summary) #normal
                else:
                    print("No tiene commonscat")
                            
if __name__ == '__main__':
    main()

#si este script va bien, pedir autorizacion para hacer lo mismo con taxon, edificios, iglesias, etc, ver ideas en https://query.wikidata.org/#SELECT%20%3Fp31%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%20%20%20%20SERVICE%20bd%3Asample%20%7B%0A%20%20%20%20%20%20%3Fitem%20wdt%3AP18%20%3Fimage.%0A%20%20%20%20%20%20bd%3AserviceParam%20bd%3Asample.limit%20120000%20.%0A%20%20%20%20%20%20bd%3AserviceParam%20bd%3Asample.sampleType%20%22RANDOM%22%20.%0A%20%20%20%20%7D%0A%20%20%20%20%3Fitem%20wdt%3AP31%20%3Fp31.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Ces%22.%20%7D%0A%7D%0AGROUP%20BY%20%3Fp31%0AORDER%20BY%20DESC%28%3Fcount%29

#tb hacer este https://commons.wikimedia.org/wiki/Commons:Bots/Requests/Emijrpbot_12
#para las descs q sean simplemente un ^[[link]]\.?$, o sean ^The [[link]], o ^[[link]] viewed https://en.wikipedia.org/w/index.php?title=Murray_River&oldid=1231417560#Murray_mouth
