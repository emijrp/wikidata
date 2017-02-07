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

import re
import sys

import pwb
import pywikibot
from quickstatements import *

def main():
    targetlangs = ['es', 'ca', 'gl']
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    genders = {
        'Q6581097': 'male', 
        'Q6581072': 'female', 
    }
    
    translationsNationalities = {
        'Argentinian': {
            'ca': { 'male': 'argentí', 'female': 'argentina' },
            'en': { 'male': 'Argentinian', 'female': 'Argentinian' }, 
            'es': { 'male': 'argentino', 'female': 'argentina'}, 
            'gl': { 'male': 'arxentino', 'female': 'arxentina'}, 
        },
        'Chilean': {
            'ca': { 'male': 'xilè', 'female': 'xilena' },
            'en': { 'male': 'Chilean', 'female': 'Chilean' }, 
            'es': { 'male': 'chileno', 'female': 'chilena'}, 
            'gl': { 'male': 'chileno', 'female': 'chilena'}, 
        },
        'Czech': {
            'ca': { 'male': 'txec', 'female': 'txeca' },
            'en': { 'male': 'Czech', 'female': 'Czech' }, 
            'es': { 'male': 'checo', 'female': 'checa'}, 
            'gl': { 'male': 'checo', 'female': 'checa'}, 
        },
        'Ecuadorian': {
            'ca': { 'male': 'equatorià', 'female': 'equatoriana' },
            'en': { 'male': 'Ecuadorian', 'female': 'Ecuadorian' }, 
            'es': { 'male': 'ecuatoriano', 'female': 'ecuatoriana'}, 
            'gl': { 'male': 'ecuatoriano', 'female': 'ecuatoriana'}, 
        },
        'French': {
            'ca': { 'male': 'francés', 'female': 'francesa' },
            'en': { 'male': 'French', 'female': 'French' }, 
            'es': { 'male': 'francés', 'female': 'francesa'}, 
            'gl': { 'male': 'francés', 'female': 'francesa'}, 
        },
        'German': {
            'ca': { 'male': 'alemany', 'female': 'alemanya' },
            'en': { 'male': 'German', 'female': 'German' }, 
            'es': { 'male': 'alemán', 'female': 'alemana'}, 
            'gl': { 'male': 'alemán', 'female': 'alemá'}, 
        },
        'Italian': {
            'ca': { 'male': 'italià', 'female': 'italiana'}, 
            'en': { 'male': 'Italian ', 'female': 'Italian'}, 
            'es': { 'male': 'italiano', 'female': 'italiana'}, 
            'gl': { 'male': 'italiano', 'female': 'italiana'}, 
        }, 
        'Portuguese': {
            'ca': { 'male': 'portuguès', 'female': 'portuguesa'}, 
            'en': { 'male': 'Portuguese', 'female': 'Portuguese'}, 
            'es': { 'male': 'portugués', 'female': 'portuguesa'}, 
            'gl': { 'male': 'portugués', 'female': 'portuguesa'}, 
        }, 
        'Russian': {
            'ca': { 'male': 'rus', 'female': 'russa' }, 
            'en': { 'male': 'Russian', 'female': 'Russian' }, 
            'es': { 'male': 'ruso', 'female': 'rusa' }, 
            'gl': { 'male': 'ruso', 'female': 'rusa' }, 
        }, 
        'Spanish': {
            'ca': { 'male': 'espanyol', 'female': 'espanyola' }, 
            'en': { 'male': 'Spanish', 'female': 'Spanish' }, 
            'es': { 'male': 'español', 'female': 'española' }, 
            'gl': { 'male': 'español', 'female': 'española' }, 
        }, 
    }
    translationsOccupations = {
        '~ association football player': {
            'ca': { 'male': 'futbolista ~', 'female': 'futbolista ~'}, 
            'en': { 'male': '~ association football player', 'female': '~ association football player'}, 
            'es': { 'male': 'futbolista ~', 'female': 'futbolista ~'}, 
            'gl': { 'male': 'futbolista ~', 'female': 'futbolista ~'}, 
        }, 
        '~ footballer': {
            'ca': { 'male': 'futbolista ~', 'female': 'futbolista ~'}, 
            'en': { 'male': '~ footballer', 'female': '~ footballer'}, 
            'es': { 'male': 'futbolista ~', 'female': 'futbolista ~'}, 
            'gl': { 'male': 'futbolista ~', 'female': 'futbolista ~'}, 
        }, 
        '~ politician': {
            'ca': { 'male': 'polític ~', 'female': 'política ~'}, 
            'en': { 'male': '~ politician', 'female': '~ politician'}, 
            'es': { 'male': 'político ~', 'female': 'política ~'}, 
            'gl': { 'male': 'político ~', 'female': 'política ~'}, 
        }, 
        '~ tennis player': {
            'ca': { 'male': 'tennista professional ~', 'female': 'tennista professional ~'}, 
            'en': { 'male': '~ tennis player', 'female': '~ tennis player'}, 
            'es': { 'male': 'tenista profesional ~', 'female': 'tenista profesional ~'}, 
            'gl': { 'male': 'tenista profesional ~', 'female': 'tenista profesional ~'}, 
        }, 
        '~ writer': {
            'ca': { 'male': 'escriptor ~', 'female': 'escriptora ~'}, 
            'en': { 'male': '~ writer', 'female': '~ writer'}, 
            'es': { 'male': 'escritor ~', 'female': 'escritora ~'}, 
            'gl': { 'male': 'escritor ~', 'female': 'escritora ~'}, 
        }, 
    }
    translations = {}
    for occupkey, occupdic in translationsOccupations.items():
        for natkey, natdic in translationsNationalities.items():
            translations[re.sub('~', natkey, occupkey)] = {}
            for translang in occupdic.keys():
                translations[re.sub('~', natkey, occupkey)][translang] = {
                    'male': re.sub('~', natdic[translang]['male'], occupdic[translang]['male']), 
                    'female': re.sub('~', natdic[translang]['female'], occupdic[translang]['female']), 
                }

    for targetlang in targetlangs:
        for genderq, genderlabel in genders.items():
            for translation in translations.keys():
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%20%20%20%20%3Fitem%20wdt%3AP31%20wd%3AQ5%20.%20%23instanceof%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3A'+genderq+'%20.%20%23gender%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22'+re.sub(' ', '%20', translation)+'%22%40en.%20%23description%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+targetlang+'%22).%20%20%7D%0A%20%20%20%20FILTER%20(!BOUND(%3FitemDescription))%0A%7D'
                url = '%s&format=json' % (url)
                sparql = getURL(url=url)
                json1 = loadSPARQL(sparql=sparql)
                
                for result in json1['results']['bindings']:
                    q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                    print('\n== %s ==' % (q))
                    item = pywikibot.ItemPage(repo, q)
                    item.get()
                    descriptions = item.descriptions
                    addedlangs = []
                    for lang in translations[translation].keys():
                        if not lang in descriptions.keys():
                            descriptions[lang] = translations[translation][lang][genderlabel]
                            addedlangs.append(lang)
                    data = { 'descriptions': descriptions }
                    addedlangs.sort()
                    if addedlangs:
                        summary = 'BOT - Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                        print(summary)
                        try:
                            item.editEntity(data, summary=summary)
                        except:
                            print('Error while saving')
                            continue

if __name__ == "__main__":
    main()
