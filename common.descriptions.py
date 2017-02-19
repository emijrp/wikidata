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
from wikidatafun import *

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

#cuadro de https://www.wikidata.org/wiki/Q22661785

def main():
    translations = {
        'chemical compound': {
            'ast': 'compuestu químicu',
            'ca': 'compost químic',
            'de': 'chemische Verbindung',
            'en': 'chemical compound',
            'eo': 'kemia kombinaĵo',
            'es': 'compuesto químico',
            'eu': 'konposatu kimiko',
            'fr': 'composé chimique',
            'gl': 'composto químico',
            'he': 'תרכובת',
            'hy': 'քիմիական միացություն',
            'it': 'composto chimico',
            'nb': 'kjemisk forbindelse',
            'nl': 'chemische stof',
            'nn': 'kjemisk sambinding',
            'oc': 'component quimic',
            'pl': 'związek chemiczny',
            'pt': 'composto químico',
            'pt-br': 'composto químico',
            'ro': 'compus chimic',
        }, 
        'genus of algae': {
            'en': 'genus of algae',
            'es': 'género de algas',
            'gl': 'xénero de algas',
        }, 
        'genus of amphibians': {
            'en': 'genus of amphibians',
            'es': 'género de anfibios',
        }, 
        'genus of arachnids': {
            'ca': "gènere d'aràcnids",
            'en': 'genus of arachnids',
            'es': 'género de arañas',
        }, 
        'genus of birds': {
            'ca': "gènere d'ocells",
            'en': 'genus of birds',
            'es': 'género de aves',
            'gl': 'xénero de aves',
        }, 
        'genus of fishes': {
            'en': 'genus of fishes',
            'es': 'género de peces',
        }, 
        'genus of fungi': {
            'en': 'genus of fungi',
            'es': 'género de hongos',
            'gl': 'xénero de fungos',
        }, 
        'genus of insects': {
            'ca': "gènere d'insectes",
            'en': 'genus of insects',
            'es': 'género de insectos',
        }, 
        'genus of mammals': {
            'ca': 'gènere de mamífers',
            'en': 'genus of mammals',
            'es': 'género de mamíferos',
            'gl': 'xénero de mamíferos',
        }, 
        'genus of molluscs': {
            'en': 'genus of molluscs',
            'es': 'género de moluscos',
            'gl': 'xénero de moluscos',
        }, 
        'genus of plants': {
            'ca': 'gènere de plantes',
            'en': 'genus of plants',
            'es': 'género de plantas',
            'gl': 'xénero de plantas',
        }, 
        'genus of reptiles': {
            'ca': 'gènere de rèptils',
            'en': 'genus of reptiles',
            'es': 'género de reptiles',
        }, 
        'female given name': {
            'af': 'vroulike voornaam',
            'ar': 'أسم مؤنث معطى',
            'ast': 'nome femenín',
            'bar': 'Weiwanam',
            'be': 'жаночае асабістае імя',
            'bn': 'প্রদত্ত মহিলা নাম',
            'br': 'anv merc’hed',
            'bs': 'žensko ime',
            'ca': 'prenom femení',
            'ce': 'зудчун шен цӀе',
            'cs': 'ženské křestní jméno',
            'cy': 'enw personol benywaidd',
            'da': 'pigenavn',
            'de': 'weiblicher Vorname',
            'de-at': 'weiblicher Vorname',
            'de-ch': 'weiblicher Vorname',
            'el': 'γυναικείο όνομα',
            'en': 'female given name',
            'en-ca': 'female given name',
            'en-gb': 'female given name',
            'eo': 'virina persona nomo',
            'es': 'nombre femenino',
            'et': 'naisenimi',
            'fa': 'نام‌های زنانه',
            'fi': 'naisen etunimi',
            'fr': 'prénom féminin',
            'he': 'שם פרטי של אישה',
            'hr': 'žensko ime',
            'hsb': 'žonjace předmjeno',
            'hu': 'női keresztnév',
            'hy': 'իգական անձնանուն',
            'id': 'nama perempuan feminin',
            'it': 'prenome femminile',
            'ja': '女性の名前',
            'ko': '여성의 이름',
            'la': 'praenomen femininum',
            'lb': 'weibleche Virnumm',
            'lt': 'moteriškas vardas',
            'lv': 'sieviešu personvārds',
            'mk': 'женско лично име',
            'nb': 'kvinnenavn',
            'ne': 'स्त्रीलिङ्गी नाम',
            'nl': 'vrouwelijke voornaam',
            'nn': 'kvinnenamn',
            'pl': 'imię żeńskie',
            'pt': 'nome próprio feminino',
            'pt-br': 'nome próprio feminino',
            'ro': 'prenume feminin',
            'ru': 'женское личное имя',
            'sr': 'женско лично име',
            'sr-ec': 'женско лично име',
            'scn': 'nomu di battìu fimmininu',
            'sco': 'female gien name',
            'sk': 'ženské krstné meno',
            'sl': 'žensko osebno ime',
            'sr-el': 'žensko lično ime',
            'sv': 'kvinnonamn',
            'tr': 'kadın ismidir',
            'uk': 'жіноче особове ім’я',
            'yue': '女性人名',
            'zh': '女性人名',
            'zh-cn': '女性人名 ',
            'zh-hans': '女性人名',
            'zh-hant': '女性人名',
            'zh-hk': '女性人名',
            'zh-mo': '女性人名',
            'zh-my': '女性人名',
            'zh-sg': '女性人名',
            'zh-tw': '女性人名'
        }, 
        'Hebrew calendar year': {
            'ca': 'any de calendari hebreu', 
            'en': 'Hebrew calendar year', 
            'es': 'año del calendario hebreo', 
            'he': 'שנה בלוח השנה העברי',
        }, 
        'Islamic calendar year': {
            'en': 'Islamic calendar year', 
            'es': 'año del calendario musulmán',
            'he': 'שנה בלוח השנה המוסלמי', 
        }, 
        'male given name': {
            'af': 'manlike voornaam',
            'ar': 'أسم مذكر معطى',
            'ast': 'nome masculín',
            'bar': 'Mannanam',
            'be': 'мужчынскае асабістае імя',
            'be-tarask': 'мужчынскае асабістае імя',
            'bn': 'প্রদত্ত পুরুষ নাম',
            'br': 'anv paotr',
            'bs': 'muško ime',
            'ca': 'prenom masculí',
            'ce': 'стеган шен цӀе',
            'cs': 'mužské křestní jméno',
            'cy': 'enw personol gwrywaidd',
            'da': 'drengenavn',
            'de': 'männlicher Vorname',
            'de-at': 'männlicher Vorname',
            'de-ch': 'männlicher Vorname',
            'el': 'ανδρικό όνομα',
            'en': 'male given name',
            'en-ca': 'male given name',
            'en-gb': 'male given name',
            'eo': 'vira persona nomo',
            'es': 'nombre masculino',
            'et': 'mehenimi',
            'eu': 'gizonezko izena',
            'fa': 'نام کوچک مردانه',
            'fi': 'miehen etunimi',
            'fr': 'prénom masculin',
            'fy': 'Jongesnamme',
            'gl': 'nome masculino',
            'gsw': 'männlige Vorname',
            'he': 'שם פרטי של גבר',
            'hr': 'muško ime',
            'hu': 'férfi keresztnév',
            'hy': 'արական անձնանուն',
            'id': 'nama pemberian maskulin',
            'is': 'mannsnafn',
            'it': 'prenome maschile',
            'ja': '男性の名前',
            'ko': '남성의 이름',
            'la': 'praenomen masculinum',
            'lb': 'männleche Virnumm',
            'lt': 'vyriškas vardas',
            'lv': 'vīriešu personvārds',
            'mk': 'машко лично име',
            'nb': 'mannsnavn',
            'ne': 'पुलिङ्गी नाम',
            'nl': 'mannelijke voornaam',
            'nn': 'mannsnamn',
            'pl': 'imię męskie',
            'pt': 'nome próprio masculino',
            'pt-br': 'nome próprio masculino',
            'ro': 'prenume masculin',
            'ru': 'мужское личное имя',
            'scn': 'nomu di battìu masculinu',
            'sco': 'male first name',
            'sk': 'mužské meno',
            'sl': 'moško osebno ime',
            'sr': 'мушко лично име',
            'sr-el': 'muško lično ime',
            'sr-ec': 'мушко лично име',
            'sv': 'mansnamn',
            'tr': 'erkek ismidir',
            'uk': 'чоловіче особове ім’я',
            'yue': '男性人名',
            'zh': '男性人名',
            'zh-cn': '男性人名',
            'zh-hans': '男性名',
            'zh-hant': '男性人名',
            'zh-hk': '男性人名',
            'zh-mo': '男性人名',
            'zh-my': '男性人名',
            'zh-sg': '男性人名',
            'zh-tw': '男性人名'
        },         
        'surname': {
            #'an': '', #no esta claro si es apellido o apelliu?
            'ar': 'اسم العائلة', 
            'ast': 'apellíu', 
            'az': 'Soyad', 
            'bar': 'Schreibnam', 
            'be': 'прозвішча', 
            'bg': 'презиме', 
            'bn': 'পারিবারিক নাম', 
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
            'fo': 'ættarnavn',
            'fr': 'nom de famille', 
            'gl': 'apelido', 
            'gsw': 'Familiename', 
            'gu': 'અટક', 
            'he': 'שם משפחה', 
            'hr': 'prezime', 
            'hu': 'vezetéknév', 
            'hy': 'ազգանուն', 
            'id': 'nama asli', 
            'is': 'eftirnafn',
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
            'zh-cn': '姓氏', 
            'zh-hans': '姓氏', 
            'zh-hant': '姓氏', 
            'zh-hk': '姓氏', 
            'zh-mo': '姓氏', 
            'zh-my': '姓氏', 
            'zh-sg': '姓氏', 
            'zh-tw': '姓氏',  
            'zu': 'isibongo', 
        }, 
    }
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    queries = {
        #'chemical compound': 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ11173%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ4167410%20%7D%20.%20%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22chemical%20compound%22%40en.%0A%09OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%7D', 
        'female given name': 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ11879590%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ4167410%20%7D%20.%20%0A%7D', 
        #'Hebrew calendar year': '', # buscar como hacer la query con qualifiers https://www.wikidata.org/wiki/Q2817509
        #'Islamic calendar year': 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ577%20.%0A%20%20%20%20%3Fitem%20wdt%3AP361%20wd%3AQ28892%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ4167410%20%7D%20.%20%0A%7D', 
        'male given name': 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ12308941%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ4167410%20%7D%20.%20%0A%7D', 
        #'natural number': '', 
        #species of insect, plant
        'surname': 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ101352%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ4167410%20%7D%20.%20%0A%7D', 
    }
    for topic in queries.keys():
        url = queries[topic]
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            print('\n== %s [%s] ==' % (q, topic))
            item = pywikibot.ItemPage(repo, q)
            item.get()
            descriptions = item.descriptions
            addedlangs = []
            for lang in translations[topic].keys():
                if lang not in descriptions.keys():
                    descriptions[lang] = translations[topic][lang]
                    addedlangs.append(lang)
                    #print('%s\tD%s\t"%s"' % (q, lang, translations[topic][lang])) #quickstatements mode
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
