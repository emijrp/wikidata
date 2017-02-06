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

import pwb
import pywikibot
from quickstatements import *

def main():
    translations = {
        #'an': '', #no esta claro si es apellido o apelliu?
        'ar': 'اسم العائلة', 
        'ast': 'apellíu', 
        'az': 'Soyad', 
        'bar': 'Familiennåmen', 
        'be': 'прозвішча', 
        'bg': 'презиме', 
        'bs': 'prezime', 
        'ca': 'cognom', 
        'cs': 'příjmení', 
        'cy': 'cyfenw', 
        'da': 'efternavn', 
        'de': 'Familienname', 
        'de-at': 'Familienname', 
        'de-ch': 'Familienname', 
        'el': 'επώνυμο', 
        'en': 'family name', 
        'es': 'apellido', 
        'et': 'perekonnanimi', 
        'eu': 'abizen', 
        'fa': 'نام خانوادگی', 
        'fi': 'sukunimi', 
        'fr': 'nom de famille', 
        'gl': 'apelido', 
        'gsw': 'Familiename', 
        'he': 'שם משפחה', 
        'hr': 'prezime', 
        'hu': 'vezetéknév', 
        'hy': 'ազգանուն', 
        'id': 'nama asli', 
        'it': 'cognome', 
        'ja': '姓', 
        'ka': 'გვარი', 
        'ko': '성씨', 
        'lb': 'Familljennumm', 
        'lt': 'pavardė', 
        'lv': 'uzvārds', 
        'min': 'namo asli', 
        'mk': 'презиме', 
        'nb': 'etternavn', 
        'nds': 'Familiennaam', 
        'nl': 'achternaam', 
        'nn': 'etternamn', 
        'pl': 'nazwisko', 
        'pt': 'sobrenome', 
        'pt-br': 'nome de família', 
        'ro': 'nume de familie', 
        'ru': 'фамилия', 
        'sh': 'prezime', 
        'sk': 'priezvisko', 
        'sl': 'priimek', 
        'sq': 'mbiemri', 
        'sr': 'презиме', 
        'sv': 'efternamn', 
        'tl': 'apelyido', 
        'tr': 'soyadı', 
        'uk': 'прізвище', 
        'zh': '姓氏', 
        'zu': 'isibongo', 
    }
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    """
    #filter by language
    SELECT ?item
    WHERE {
        ?item wdt:P31 wd:Q101352 .
        FILTER NOT EXISTS { ?item wdt:P31 wd:Q4167410 } . 
        OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "ca").  }
        FILTER (!BOUND(?itemDescription))
    }
    #all surnames
    SELECT ?item
    WHERE {
        ?item wdt:P31 wd:Q101352 .
        FILTER NOT EXISTS { ?item wdt:P31 wd:Q4167410 } . 
    }
    """
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ101352%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ4167410%20%7D%20.%20%0A%7D'
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
        for lang in translations.keys():
            if lang not in descriptions.keys():
                descriptions[lang] = translations[lang]
                addedlangs.append(lang)
                #print('%s\tD%s\t"%s"' % (q, lang, translations[lang])) #quickstatements mode
        data = { 'descriptions': descriptions }
        addedlangs.sort()
        if addedlangs:
            summary = 'BOT - Adding descriptions: %s' % (', '.join(addedlangs))
            print(summary)
            try:
                item.editEntity(data, summary=summary)
            except:
                print('Error while saving')
                continue

if __name__ == "__main__":
    main()
