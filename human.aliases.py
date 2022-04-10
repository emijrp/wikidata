#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021 emijrp <emijrp@gmail.com>
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
import time

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

def qIsHuman(item=""):
    try:
        item.get()
        if 'P31' in item.claims:
            for p31 in item.claims['P31']:
                if p31.getTarget().title() == "Q5":
                    return True
    except:
        print('Error while retrieving item, skiping...')
        return False
    return False

def main():
    #recorrer categorías de nacimientos por año, y buscar el texto bold del nombre, y compararlo con el label y aliases de wikidata, sino están, añadirlo
    #tirar de interwikis y repetir para es, it, fr, ..., alfabeto latino
    
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    repo = wdsite.data_repository()
    ignore = [
        'Q983416', #meh, just in case, https://www.wikidata.org/w/index.php?title=User_talk:Emijrp&oldid=1498162619#Inappropriate_alias(es)_by_your_bot
    ]
    
    years = list(range(1000, 2000))
    categories = {
        #añadido hasta el ido: segun la tabla al 31 de diciembre de 2021
        #'als': ['Category:%s' % (x) for x in ["Dütsche", "Schwiizer"]], el idioma gsw: recae en este? aclarar antes de lanzarlo
        'af': ['Category:Geboortes in %s' % (year) for year in years], 
        'an': ['Category:%s (naixencias)' % (year) for year in years], 
        'ast': ['Category:Persones nacíes en %s' % (year) for year in years], 
        'bar': ['Category:Geboren %s' % (year) for year in years], 
        'br': ['Category:Ganedigezhioù %s' % (year) for year in years], 
        'bs': ['Category:Rođeni %s.' % (year) for year in years], 
        'ca': ['Category:Persones vives'], 
        'cs': ['Category:Narození %s' % (year) for year in years], 
        'cy': ['Category:Genedigaethau %s' % (year) for year in years], 
        'da': ['Category:Født i %s' % (year) for year in years], 
        'de': ['Category:Geboren %s' % (year) for year in years], 
        'en': ['Category:%s births' % (year) for year in years], 
        'es': ['Category:Nacidos en %s' % (year) for year in years], 
        'et': ['Category:Sündinud %s' % (year) for year in years], 
        'eu': ['Category:Gizabanako biziak'], 
        'ext': ['Category:%s' % (x) for x in ["Científicus", "Escrebioris"]], 
        'fi': ['Category:Vuonna %s syntyneet' % (year) for year in years], 
        'fo': ['Category:Føðingar í %s' % (year) for year in years], 
        'fr': ['Category:Naissance en %s' % (year) for year in years], 
        'fy': ['Category:Persoan berne yn %s' % (year) for year in years], 
        'ga': ['Category:Daoine a rugadh i %s' % (year) for year in years], 
        'gl': ['Category:Nados en %s' % (year) for year in years], 
        'hsb': ['Category:Rodź. %s' % (year) for year in years], 
        'hu': ['Category:%s-ben született személyek' % (year) for year in years], 
        'ia': ['Category:%s' % (x) for x in ["Actores de film", "Philosophos", "Physicos", "Pictores", "Politicos", "Scriptores", "Scientistas"]], 
        'id': ['Category:Kelahiran %s' % (year) for year in years], 
        'it': ['Category:Nati nel %s' % (year) for year in years], 
        'jv': ['Category:Lair %s' % (year) for year in years], 
        'ku': ['Category:Jidayikbûn %s' % (year) for year in years], 
        'kw': ['Category:Mernansow %s' % (year) for year in years], 
        'la': ['Category:Nati %s' % (year) for year in years], 
        'ms': ['Category:Kelahiran %s' % (year) for year in years], 
        'nds': ['Category:Boren %s' % (year) for year in years], 
        #nl: no useful cats, deberia hacer esto con sparql sobre Q5 y sacar los iws y filtrar los idiomas interesen...
        'nn': ['Category:Fødde i %s' % (year) for year in years], 
        'no': ['Category:Fødsler i %s' % (year) for year in years], 
        'oc': ['Category:Naissença en %s' % (year) for year in years], 
        'pl': ['Category:Urodzeni w %s' % (year) for year in years], 
        'pt': ['Category:Nascidos em %s' % (year) for year in years], 
        'ro': ['Category:Nașteri în %s' % (year) for year in years], 
        'sh': ['Category:Rođeni %s.' % (year) for year in years], 
        'sk': ['Category:Narodenia v %s' % (year) for year in years], 
        'sq': ['Category:Lindje %s' % (year) for year in years], 
        'su': ['Category:Nu babar taun %s' % (year) for year in years], 
        'sv': ['Category:Födda %s' % (year) for year in years], 
        'tl': ['Category:Ipinanganak noong %s' % (year) for year in years], 
        'tr': ['Category:%s doğumlular' % (year) for year in years], 
        'vi': ['Category:Sinh năm %s' % (year) for year in years], 
        'yo': ['Category:Àwọn ọjọ́ìbí ní %s' % (year) for year in years], 
        'zea': ['Category:Historisch persoôn'], 
    }
    langs = list(categories.keys())
    #langs = ['ca', 'da', 'de', 'eu', 'fi', 'it', 'pt', 'sv']
    random.shuffle(langs)
    for targetlang in langs:
        wikisite = pywikibot.Site(targetlang, 'wikipedia')
        if not targetlang in categories.keys():
            print('Idioma %s no conocido' % (targetlang))
            continue
        cats = categories[targetlang]
        random.shuffle(cats)
        for catname in cats:
            cat = pywikibot.Category(wikisite, catname)
            if not cat.exists():
                continue
            gen = pagegenerators.CategorizedPageGenerator(cat, recurse=False)
            pre = pagegenerators.PreloadingGenerator(gen, groupsize=50)
            
            for page in pre:
                if page.isRedirectPage():
                    continue
                print('\n==', page.title().encode('utf-8'), '==')
                item = ''
                try:
                    item = pywikibot.ItemPage.fromPage(page)
                except:
                    pass
                if item:
                    print('Page has item')
                    print('https://www.wikidata.org/wiki/%s' % (item.title()))
                    
                    if item.title() in ignore:
                        print('Item in ignore list, skiping...')
                        continue
                    
                    if not qIsHuman(item=item):
                        print('Item not human Q5')
                        continue
                    
                    if re.search(r"\'\'\' ?[\"\']? ?\'\'\'", page.text):
                        print("Lio de ''' en el nombre")
                        continue
                    m = re.findall(r"(?im)^\'\'\'([A-Za-z \-]+?)\'\'\'", page.text)
                    print(m)
                    if len(m) < 1:
                        print('No encontramos candidatos, saltamos')
                        continue
                    elif len(m) > 1:
                        print('Ambiguo, saltamos')
                        continue
                    aliascandidate = m[0].strip()
                    aliascandidate = re.sub(r' +', ' ', aliascandidate)
                    if not ' ' in aliascandidate or len(aliascandidate) < 10: #https://www.wikidata.org/w/index.php?title=Q542337&type=revision&diff=1482744856&oldid=1400873196
                        print('Alias muy corto o unipalabra, saltamos')
                        continue
                    if len(aliascandidate) > 50:
                        print('Alias muy largo, saltamos')
                        continue
                    
                    if sum([len(x) > 2 and x in aliascandidate.lower() and 1 or 0 for x in page.title().lower().split()]) < 1:
                        # at least 1 word in title must be in alias candidate
                        print('No se encontro ninguna palabra del titulo en el alias, saltamos')
                        continue
                    
                    aliases = item.aliases
                    labels = item.labels
                    if not targetlang in labels:
                        print('No tiene label, saltamos')
                        continue
                    if aliascandidate.lower().strip() == labels[targetlang].lower().strip():
                        print('Es igual que el label, saltamos')
                        continue
                    if targetlang in aliases and aliascandidate.lower().strip() in [x.lower().strip() for x in aliases[targetlang]]:
                        print('Ya esta en los aliases, saltamos')
                        continue
                    
                    print(aliases)
                    if not targetlang in aliases:
                        aliases[targetlang] = [aliascandidate]
                    else:
                        aliases[targetlang].append(aliascandidate)
                    print(aliases)
                    print(aliases[targetlang])
                    
                    data = { 'aliases': aliases }
                    summary = "BOT - Adding 1 aliases (%s): %s" % (targetlang, aliascandidate)
                    print(summary.encode('utf-8'))
                    try:
                        item.editEntity(data, summary=summary)
                    except:
                        print('Error while saving')
                        continue
                else:
                    print('Page without item')
    
    print("Finished successfully")
        
if __name__ == "__main__":
    main()
