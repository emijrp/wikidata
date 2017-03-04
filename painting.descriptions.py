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
    
    targetlangs = ['es', 'ca', 'gl', 'ast', 'oc', ]
    translations = {
        'ast': 'pintura de ~CREATOR~', 
        'ca': 'quadre de ~CREATOR~', 
        'es': 'cuadro de ~CREATOR~', 
        'gl': 'pintura de ~CREATOR~', 
        'oc': 'pintura de ~CREATOR~', 
    }
    translationsSpecial = { #for different prepositions when needed
        'ast': "pintura d'~CREATOR~", 
        'ca': "quadre d'~CREATOR~", 
        'es': 'cuadro de ~CREATOR~', 
        'gl': 'pintura de ~CREATOR~', 
        'oc': "pintura d'~CREATOR~", 
    }
    for targetlang in targetlangs:
        print('==', targetlang, '==')
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%20%3FitemDescriptionEN%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ3305213.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%3FitemDescriptionEN.%0A%20%20%20%20FILTER%20(STRSTARTS(%3FitemDescriptionEN%2C%20%22painting%20by%22)).%20%0A%09OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+targetlang+'%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%7D'
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            descen = result['itemDescriptionEN']['value']
            if not q or not descen:
                continue
            if not 'painting by ' in descen:
                continue
            item = pywikibot.ItemPage(repo, q)
            item.get()
            
            if item.claims:
                if 'P170' in item.claims: #creator
                    try:
                        creator = item.claims['P170'][0].getTarget()
                        creator.get()
                    except:
                        print('Error while retrieving Creator')
                        continue
                    creatorlabels = creator.labels
                    descriptions = item.descriptions
                    addedlangs = []
                    for lang in translations.keys():
                        if not lang in descriptions.keys():
                            if not lang in creatorlabels:
                                continue
                            translation = ''
                            
                            #rules
                            if lang == 'es':
                                translation = translations[lang].replace('~CREATOR~', creatorlabels[lang])
                            
                            elif lang == 'ast':
                                if removeAccents(creatorlabels[lang][0]).lower() in ['a', 'e', 'i', 'o', 'u']:
                                    translation = translationsSpecial[lang].replace('~CREATOR~', creatorlabels[lang])
                                else:
                                    translation = translations[lang].replace('~CREATOR~', creatorlabels[lang])
                            
                            elif lang == 'ca':
                                if removeAccents(creatorlabels[lang][0]).lower() in ['a', 'e', 'i', 'o', 'u', 'h']:
                                    translation = translationsSpecial[lang].replace('~CREATOR~', creatorlabels[lang])
                                else:
                                    translation = translations[lang].replace('~CREATOR~', creatorlabels[lang])
                            
                            elif lang == 'gl':
                                translation = translations[lang].replace('~CREATOR~', creatorlabels[lang])
                            
                            elif lang == 'oc':
                                if removeAccents(creatorlabels[lang][0]).lower() in ['a', 'e', 'i', 'o', 'u']:
                                    translation = translationsSpecial[lang].replace('~CREATOR~', creatorlabels[lang])
                                else:
                                    translation = translations[lang].replace('~CREATOR~', creatorlabels[lang])
                            
                            else:
                                continue
                            
                            if translation:
                                print(translation)
                                descriptions[lang] = translation
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
