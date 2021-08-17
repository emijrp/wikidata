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

def main():
    #recorrer categorías de nacimientos por año, y buscar el texto bold del nombre, y compararlo con el label y aliases de wikidata, sino están, añadirlo
    #tirar de interwikis y repetir para es, it, fr, ..., alfabeto latino
    
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    repo = wdsite.data_repository()
    wikisite = pywikibot.Site('en', 'wikipedia')
    
    years = range(1750, 1980)
    random.shuffle(years)
    for year in years:
        cat = pywikibot.Category(wikisite, 'Category:%s births' % (year))
        gen = pagegenerators.CategorizedPageGenerator(cat, recurse=False)
        pre = pagegenerators.PreloadingGenerator(gen, groupsize=50)
        targetlang = 'en'
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
                
                m = re.findall(r"(?im)^\'\'\'([A-Za-z \-]+?)\'\'\'", page.text)
                print(m)
                if len(m) < 1:
                    print('No encontramos candidatos, saltamos')
                    continue
                elif len(m) > 1:
                    print('Ambiguo, saltamos')
                    continue
                aliascandidate = m[0]
                if not ' ' in aliascandidate or len(aliascandidate) < 10: #https://www.wikidata.org/w/index.php?title=Q542337&type=revision&diff=1482744856&oldid=1400873196
                    print('Alias muy corto o unipalabra, saltamos')
                    continue
                if sum([len(x) > 2 and x in aliascandidate.lower() and 1 or 0 for x in page.title().lower().split()]) < 1:
                    # at least 1 word in title must be in alias candidate
                    print('No se encontro ninguna palabra del titulo en el alias, saltamos')
                    continue
                
                aliases = item.aliases
                labels = item.labels
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
