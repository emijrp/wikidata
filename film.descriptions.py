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

import os
import re
import sys
import time
import urllib.parse

import pwb
import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    targetlangs = ['es', 'ca', 'gl', 'ast', 'an', 'ext', 'oc', 'it', 'pt', 'sv', 'de', 'nl', 'fy', 'fr', 'he', 'ar', 'ro', 'et', ]
    #he: it only adds YEAR by now
    translations = {
        'an': 'cinta de ~YEAR~ dirichita por ~AUTHOR~', 
        'ar': 'فيلم أنتج عام ~YEAR~', 
        'ast': 'película de ~YEAR~ dirixida por ~AUTHOR~', 
        'ca': 'pel·lícula de ~YEAR~ dirigida per ~AUTHOR~', 
        'de': 'Film von ~AUTHOR~ (~YEAR~)', 
        'es': 'película de ~YEAR~ dirigida por ~AUTHOR~', 
        'et': '~YEAR~. aasta film, lavastanud ~AUTHOR~', 
        'ext': 'pinicla de ~YEAR~ dirigía por ~AUTHOR~', 
        'fr': 'film de ~AUTHOR~, sorti en ~YEAR~', 
        'fy': 'film út ~YEAR~ fan ~AUTHOR~', 
        'gl': 'filme de ~YEAR~ dirixido por ~AUTHOR~', 
        #'he': 'סרט של ~AUTHOR~ משנת ~YEAR~', #warning, avoid mix Latin and Hebrew chars for directors name
        'he': 'סרט משנת ~YEAR~', 
        'it': 'film del ~YEAR~ diretto da ~AUTHOR~', 
        'nl': 'film uit ~YEAR~ van ~AUTHOR~', 
        'oc': 'filme de ~YEAR~ dirigit per ~AUTHOR~', 
        'pt': 'filme de ~YEAR~ dirigido por ~AUTHOR~', 
        'ro': 'film din ~YEAR~ regizat de ~AUTHOR~', 
        'sv': 'film från ~YEAR~ regisserad av ~AUTHOR~', 
    }
    translationsand = {
        'an': ' y ', 
        'ar': ' و', 
        'ast': ' y ', 
        'ca': ' i ', 
        'de': ' und ', 
        'es': ' y ', 
        'et': ' ja ', 
        'ext': ' y ', 
        'fr': ' et ',  
        'fy': ' en ', 
        'he': ' ו',
        'gl': ' e ', 
        'it': ' e ', 
        'nl': ' en ', 
        'oc': ' e ', 
        'pt': ' e ', 
        'ro': ' și ', 
        'sv': ' och ', 
    }
    for targetlang in targetlangs:
        for year in range(1880, 2020):
            print(targetlang, year)
            for defaultdescen in [str(year)+'%20film%20by', str(year)+'%20film%20directed%20by', ]:
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%20%3FitemDescriptionEN%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ11424.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%3FitemDescriptionEN.%0A%20%20%20%20FILTER%20(CONTAINS(%3FitemDescriptionEN%2C%20%22'+defaultdescen+'%22)).%20%0A%09OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+targetlang+'%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%7D'
                url = '%s&format=json' % (url)
                sparql = getURL(url=url)
                json1 = loadSPARQL(sparql=sparql)
                for result in json1['results']['bindings']:
                    q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                    descen = result['itemDescriptionEN']['value']
                    if not q or not descen:
                        continue
                    if not 'film by ' in descen:
                        continue
                    author = descen.split('film by ')[1].split(', ')
                    if not author or len(author[0]) == 0:
                        continue
                    item = pywikibot.ItemPage(repo, q)
                    item.get()
                    descriptions = item.descriptions
                    addedlangs = []
                    for lang in translations.keys():
                        if not lang in descriptions.keys():
                            translation = translations[lang]
                            translation = translation.replace('~YEAR~', str(year))
                            if len(author) == 1:
                                translation = translation.replace('~AUTHOR~', ''.join(author))
                            elif len(author) == 2:
                                translation = translation.replace('~AUTHOR~', translationsand[lang].join(author))
                            elif len(author) > 2:
                                author_ = ', '.join(author[:-1])
                                author_ = '%s%s%s' % (author_, translationsand[lang], author[-1])
                                translation = translation.replace('~AUTHOR~', author_)
                            descriptions[lang] = translation
                            print(q, author, lang, translation)
                            addedlangs.append(lang)
                    data = { 'descriptions': descriptions }
                    addedlangs.sort()
                    if addedlangs:
                        summary = 'BOT - Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                        print(summary)
                        try:
                            item.editEntity(data, summary=summary)
                        except:
                            #pywikibot.data.api.APIError: modification-failed: Item Q... already has label "..." associated with language code ..., using the same description text.
                            print('Error while saving')
                            continue
                    else:
                        print('No changes needed')

if __name__ == "__main__":
    main()
