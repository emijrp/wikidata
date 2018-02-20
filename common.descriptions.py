#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2018 emijrp <emijrp@gmail.com>
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
import time
import urllib.parse

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
#family
#genus
#species
#proteins https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3FitemDescription%20(COUNT(%3Fitem)%20AS%20%3Fcount)%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP279%20wd%3AQ8054.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22mammalian%20protein%20found%20in%20Mus%20musculus%22%40en.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09FILTER%20(BOUND(%3FitemDescription))%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC(%3Fcount)

def main():
    fixthiswhenfound = { #fix (overwrite) old, wrong or poor translations
        'chemical compound': {
            'nl': ['chemische stof'], #https://www.wikidata.org/w/index.php?title=Q27165025&type=revision&diff=486050731&oldid=466952438
        },
        'family name': {
            'sq': ['mbiemri'], #because "mbiemri" = "the family name"
        },
        'species of insect': {
            'sq': ['specie e insekteve'], #https://github.com/emijrp/wikidata/pull/47
        },
        'village in China': {
            'bn': ['চীনের গ্রাম'], #https://www.wikidata.org/w/index.php?title=User_talk:Emijrp&diff=prev&oldid=510797889
            'fi': ['kiinalainen kylä'], #https://www.wikidata.org/w/index.php?title=User_talk:Emijrp&diff=468197059&oldid=463649230
            'id': ['desa di Cina'],
        }, 
        'Wikimedia category': {
            'be': ['катэгарызацыя'], #https://www.wikidata.org/w/index.php?title=User:Emijrp/Wikimedia_project_pages_matrix&diff=next&oldid=500158307
            'be-tarask': ['Катэгорыя'],#https://www.wikidata.org/w/index.php?title=User:Emijrp/Wikimedia_project_pages_matrix&diff=next&oldid=500158307
            'es': ['categoría de Wikipedia'],
            'mk': ['категорија на Википедија'],
            'uk': ['Категорії', 'категорія в проекті Вікімедіа'], #https://www.wikidata.org/w/index.php?title=User_talk%3AEmijrp&type=revision&diff=527336622&oldid=525302741
        }, 
        'Wikimedia disambiguation page': {
            'el': ['σελίδα αποσαφήνισης'],#https://www.wikidata.org/w/index.php?title=Q29449981&diff=prev&oldid=567203989
            'es': ['desambiguación de Wikipedia'], 
            'fy': ['Betsjuttingsside'], #https://www.wikidata.org/w/index.php?title=User:Emijrp/Wikimedia_project_pages_matrix&curid=30597789&diff=499110338&oldid=498167178
            'id': ['halaman disambiguasi'], 
            'tg': ['саҳифаи ибҳомзудоии Викимаълумот'], #https://www.wikidata.org/w/index.php?title=Topic:Ts4qkooukddjcuq9&topic_showPostId=ts4rax4ro9brqqgj#flow-post-ts4rax4ro9brqqgj
            'tt': ['Википедия:Күп мәгънәле мәкаләләр'],
            'uk': ['сторінка значень в проекті Вікімедіа'],
        }, 
        'Wikimedia list article': {
            'tg': ['саҳифае, ки аз рӯйхат иборат аст'], #https://www.wikidata.org/w/index.php?title=Q13406463&diff=prev&oldid=498154491
            'uk': ['сторінка-список в проекті Вікімедіа'], #https://www.wikidata.org/w/index.php?title=Q13406463&diff=617531932&oldid=606446211
        }, 
        'Wikimedia template': {
            'be': ['шаблон Вікіпедыя'],
            'be-tarask': ['шаблён Вікіпэдыя'],
            'eu': ['Wikimediarako txantiloia'], #https://www.wikidata.org/w/index.php?title=Q11266439&type=revision&diff=469566880&oldid=469541605
            'id': ['templat Wikipedia'],
            'nb': ['Wikipedia mal'],
            'nn': ['Wikipedia mal'],
            'pl': ['szablon Wikipedii'],
            'sq': ['Wikipedia stampa'],
            'sv': ['Wikipedia mall'],
            'sw': ['kigezo Wikipedia'],
            'tg': ['Шаблони Викимедиа', 'шаблон Википедиа'], #https://www.wikidata.org/w/index.php?title=Q11266439&diff=prev&oldid=498153879
            'tr': ['şablon Vikipedi'],
            'uk': ['шаблон Вікіпедії', 'шаблон проекту Вікімедіа'],
            'yo': ['àdàkọ Wikipedia'],
            'vi': ['bản mẫu Wikipedia'],
        },
        'Wikinews article': {
            'nl': ['Wikinews-artikel'], 
        },
    }
    translations = {
        'asteroid': { #Q3863
            'af': 'asteroïde',
            'an': 'asteroide',
            'ar': 'كويكب',
            'ast': 'asteroide',
            'az': 'asteroid',
            'ba': 'Астероид',
            'bar': 'Asteroid',
            'be': 'астэроід',
            'be-tarask': 'астэроід',
            'bg': 'астероид',
            'bn': 'গ্রহাণু',
            'br': 'asteroidenn',
            'bs': 'Asteroid',
            'ca': 'asteroide',
            'ce': 'Астероид',
            'cs': 'asteroid',
            'cv': 'астероид',
            'cy': 'asteroid',
            'da': 'asteroide',
            'de': 'Asteroid',
            'el': 'αστεροειδής',
            'eml': 'Asteròid',
            'en': 'asteroid',
            'eo': 'asteroido',
            'es': 'asteroide',
            'et': 'asteroid',
            'eu': 'asteroide',
            'fa': 'سیارک',
            'fi': 'asteroidi',
            'fr': 'astéroïde',
            'fy': 'asteroïde',
            'ga': 'astaróideach',
            'gl': 'asteroide',
            'he': 'אסטרואיד',
            'hi': 'क्षुद्रग्रह',
            'hr': 'asteroidi',
            'ht': 'astewoyid',
            'hu': 'kisbolygó',
            'hy': 'աստերոիդ',
            'ia': 'asteroide',
            'id': 'asteroid',
            'ilo': 'asteroid',
            'io': 'asteroido',
            'it': 'asteroide',
            'ja': '小惑星',
            'ko': '소행성',
            'krc': 'Астероид',
            'ksh': 'Asteroid',
            'ku': 'asteroîd',
            'ky': 'астероид',
            'lb': 'Asteroid',
            'lez': 'астероид',
            'nl': 'asteroïde',
            'ru': 'астероид',
            'sh': 'asteroid',
            'sk': 'asteroid',
            'sl': 'asteroid',
            'sv': 'asteroid',
            'zh': '小行星',
        }, 
        'chemical compound': { #Q11173
            'af': 'chemiese verbinding', 
            'an': 'compuesto quimico', 
            'ar': 'مركب كيميائي',
            'ast': 'compuestu químicu',
            'bn': 'রাসায়নিক যৌগ',
            'ca': 'compost químic',
            'cs': 'chemická sloučenina',
            'da': 'kemisk forbindelse',
            'de': 'chemische Verbindung',
            'de-ch': 'chemische Verbindung',
            'en': 'chemical compound',
            'en-ca': 'chemical compound',
            'en-gb': 'chemical compound',
            'eo': 'kemia kombinaĵo',
            'es': 'compuesto químico',
            'et': 'keemiline ühend',
            'eu': 'konposatu kimiko',
            'fr': 'composé chimique',
            'fy': 'gemyske ferbining',
            'gl': 'composto químico',
            'he': 'תרכובת',
            'hy': 'քիմիական միացություն',
            'id': 'senyawa kimia',
            'it': 'composto chimico',
            'la': 'compositum chemicum',
            'lb': 'chemesch Verbindung',
            'lv': 'ķīmisks savienojums',
            'nb': 'kjemisk forbindelse',
            'nl': 'chemische verbinding',
            'nn': 'kjemisk sambinding',
            'oc': 'component quimic',
            'pl': 'związek chemiczny',
            'pt': 'composto químico',
            'pt-br': 'composto químico',
            'ro': 'compus chimic',
            'sk': 'chemická zlúčenina',
            'sq': 'komponim kimik',
        }, 
        'encyclopedic article': {
            'ar': 'مقالة موسوعية',
            'bn': 'বিশ্বকোষীয় নিবন্ধ',
            'ca': 'article enciclopèdic',
            'cs': 'encyklopedický článek',
            'da': 'encyklopædiartikel',
            'en': 'encyclopedic article',
            'eo': 'enciklopedia artikolo',
            'es': 'artículo de enciclopedia',
            'et': 'entsüklopeedia artikkel',
            'fr': "article d'encyclopédie",
            'fy': 'ensyklopedysk artikel',
            'gl': 'artigo enciclopédico',
            'hy': 'հանրագիտարանային հոդված',
            'id': 'artikel ensiklopedia',
            'io': 'enciklopediala artiklo',
            'nb': 'encyklopedisk artikkel',
            'nl': 'encyclopedisch artikel',
            'nn': 'ensyklopedisk artikkel',
            'pl': 'artykuł w encyklopedii',
            'ro': 'articol enciclopedic',
            'ru': 'энциклопедическая статья',
            'sl': 'enciklopedični članek',
            'sq': 'artikull enciklopedik',
            'sv': 'encyklopedisk artikel',
            'he': 'ערך אנציקלופדי',
        }, 
        #more families https://query.wikidata.org/#SELECT %3FitemDescription (COUNT(%3Fitem) AS %3Fcount)%0AWHERE {%0A%09%3Fitem wdt%3AP31 wd%3AQ16521.%0A %3Fitem wdt%3AP105 wd%3AQ35409.%0A %23%3Fitem schema%3Adescription "family of insects"%40en.%0A OPTIONAL { %3Fitem schema%3Adescription %3FitemDescription. FILTER(LANG(%3FitemDescription) %3D "en"). }%0A%09FILTER (BOUND(%3FitemDescription))%0A}%0AGROUP BY %3FitemDescription%0AORDER BY DESC(%3Fcount)
        'family of crustaceans': {
            'en': 'family of crustaceans',
            'es': 'familia de crustáceos',
            'he': 'משפחה של סרטנאים',
            'io': 'familio di krustacei',
            'ro': 'familie de crustacee',
        }, 
        'family of insects': {
            'bn': 'কীটপতঙ্গের পরিবার',
            'en': 'family of insects',
            'es': 'familia de insectos',
            'fr': 'famille d\'insectes',
            'he': 'משפחה של חרקים',
            'io': 'familio di insekti',
            'ro': 'familie de insecte',
        }, 
        'family of molluscs': {
            'bn': 'মলাস্কার পরিবার',
            'en': 'family of molluscs',
            'es': 'familia de moluscos',
            'he': 'משפחה של רכיכות',
            'io': 'familio di moluski',
            'ro': 'familie de moluște',
        }, 
        'family of plants': {
            'bn': 'উদ্ভিদের পরিবার',
            'en': 'family of plants',
            'es': 'familia de plantas',
            'he': 'משפחה של צמחים',
            'io': 'familio di planti',
            'ro': 'familie de plante',
        }, 
        'genus of algae': {
            'ar': 'جنس من الطحالب',
            'bn': 'শৈবালের গণ',
            'en': 'genus of algae',
            'es': 'género de algas',
            'gl': 'xénero de algas',
            'he': 'סוג של אצה',
            'id': 'genus alga',
            'io': 'genero di algi',
            'nb': 'algeslekt',
            'nn': 'algeslekt',
            'ro': 'gen de alge',
            'sq': 'gjini e algave',
        }, 
        'genus of amphibians': {
            'ar': 'جنس من البرمائيات',
            'bn': 'উভচর প্রাণীর গণ',
            'en': 'genus of amphibians',
            'es': 'género de anfibios',
            'fr': "genre d'amphibiens",
            'he': 'סוג של דו־חיים',
            'id': 'genus amfibi',
            'io': 'genero di amfibii',
            'it': 'genere di anfibi',
            'nb': 'amfibieslekt',
            'nn': 'amfibieslekt',
            'ro': 'gen de amfibieni',
            'ru': 'род амфибий',
            'sq': 'gjini e amfibeve',
        }, 
        'genus of arachnids': {
            'ar': 'جنس من العنكبوتيات',
            'bn': 'অ্যারাকনিডের গণ',
            'ca': "gènere d'aràcnids",
            'en': 'genus of arachnids',
            'es': 'género de arañas',
            'fr': "genre d'araignées",
            'he': 'סוג של עכביש',
            'id': 'genus arachnida',
            'io': 'genero di aranei',
            'it': 'genere di ragni',
            'nb': 'edderkoppslekt',
            'nn': 'edderkoppslekt',
            'ro': 'gen de arahnide',
        }, 
        'genus of birds': {
            'ar': 'جنس من الطيور',
            'bn': 'পাখির গণ',
            'ca': "gènere d'ocells",
            'en': 'genus of birds',
            'es': 'género de aves',
            'fr': "genre d'oiseaux",
            'gl': 'xénero de aves',
            'he': 'סוג של ציפור',
            'id': 'genus burung',
            'io': 'genero di uceli',
            'it': 'genere di uccelli',
            'ro': 'gen de păsări',
            'sq': 'gjini e zogjve',
        }, 
        'genus of fishes': {
            'ar': 'جنس من الأسماك',
            'bn': 'মাছের গণ',
            'en': 'genus of fishes',
            'es': 'género de peces',
            'fr': 'genre de poissons',
            'he': 'סוג של דג',
            'id': 'genus ikan',
            'io': 'genero di fishi',
            'it': 'genere di pesci',
            'nb': 'fiskeslekt',
            'nn': 'fiskeslekt',
            'pt': 'género de peixes',
            'pt-br': 'gênero de peixes',
            'ro': 'gen de pești',
            'sq': 'gjini e peshqëve',
        }, 
        'genus of fungi': {
            'ar': 'جنس من الفطريات',
            'bn': 'চত্রাকের গণ',
            'en': 'genus of fungi',
            'es': 'género de hongos',
            'fr': 'genre de champignons',
            'gl': 'xénero de fungos',
            'he': 'סוג של פטריה',
            'id': 'genus fungi',
            'io': 'genero di fungi',
            'it': 'genere di funghi',
            'nb': 'soppslekt',
            'nn': 'soppslekt',
            'pt': 'género de fungos',
            'pt-br': 'gênero de fungos',
#            'ro': 'gen de fungi',# or 'gen de ciuperci'
            'sq': 'gjini e kërpudhave',
        }, 
        'genus of insects': {
            'ar': 'جنس من الحشرات',
            'bn': 'কীটপতঙ্গের গণ',
            'ca': "gènere d'insectes",
            'en': 'genus of insects',
            'es': 'género de insectos',
            'fr': "genre d'insectes",
            'he': 'סוג של חרק',
            'id': 'genus serangga',
            'io': 'genero di insekti',
            'it': 'genere di insetti',
            'nb': 'insektslekt',
            'nn': 'insektslekt',
            'pt': 'género de insetos',
            'pt-br': 'gênero de insetos',
            'ro': 'gen de insecte',
            'ru': 'род насекомых',
            'sq': 'gjini e insekteve',
        }, 
        'genus of mammals': {
            'ar': 'جنس من الثدييات',
            'bn': 'স্তন্যপায়ীর গণ',
            'ca': 'gènere de mamífers',
            'en': 'genus of mammals',
            'es': 'género de mamíferos',
            'fr': 'genre de mammifères',
            'gl': 'xénero de mamíferos',
            'he': 'סוג של יונק',
            'id': 'genus mamalia',
            'io': 'genero di mamiferi',
            'nb': 'pattedyrslekt',
            'nn': 'pattedyrslekt',
            'ro': 'gen de mamifere',
            'sq': 'gjini e gjitarëve',
        }, 
        'genus of molluscs': {
            'ar': 'جنس من الرخويات',
            'bn': 'মলাস্কার গণ',
            'ca': 'gènere de mol·luscs',
            'en': 'genus of molluscs',
            'es': 'género de moluscos',
            'fr': 'genre de mollusques',
            'gl': 'xénero de moluscos',
            'he': 'סוג של רכיכה',
            'id': 'genus moluska',
            'io': 'genero di moluski',
            'it': 'genere di molluschi',
            'nb': 'bløtdyrslekt',
            'nn': 'blautdyrslekt',
            'ro': 'gen de moluște',
            'sq': 'gjini e molusqeve',
        }, 
        'genus of plants': {
            'ar': 'جنس من النباتات',
            'ca': 'gènere de plantes',
            'bn': 'উদ্ভিদের গণ',
            'en': 'genus of plants',
            'es': 'género de plantas',
            'fr': 'genre de plantes',
            'gl': 'xénero de plantas',
            'he': 'סוג של צמח',
            'id': 'genus tumbuh-tumbuhan',
            'io': 'genero di planti',
            'nb': 'planteslekt',
            'nn': 'planteslekt',
            'pt': 'género de plantas',
            'pt-br': 'gênero de plantas',
            'ro': 'gen de plante',
            'sq': 'gjini e bimëve',
        }, 
        'genus of reptiles': {
            'ar': 'جنس من الزواحف',
            'bn': 'সরীসৃপের গণ',
            'ca': 'gènere de rèptils',
            'en': 'genus of reptiles',
            'es': 'género de reptiles',
            'fr': 'genre de reptiles',
            'he': 'סוג של זוחל',
            'id': 'genus reptilia',
            'io': 'genero di repteri',
            'nb': 'krypdyrslekt',
            'nn': 'krypdyrslekt',
            'ro': 'gen de reptile',
            'sq': 'e zvarranikëve',
        }, 
        'family name': {
            'an': 'apelliu', 
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
            'eo': 'familia nomo', 
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
            'id': 'nama keluarga', 
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
            'se': 'goargu',
            'sh': 'prezime', 
            'sje': 'maŋŋepnamma',
            'sk': 'priezvisko', 
            'sl': 'priimek',
            'sma': 'fuelhkienomme',
            'smj': 'maŋepnamma',
            'sq': 'mbiemër', 
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
        'female given name': {
            'af': 'vroulike voornaam',
            'ar': 'اسم شخصي مذكر',
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
            'fy': 'froulike foarnamme',
            'he': 'שם פרטי של אישה',
            'hr': 'žensko ime',
            'hsb': 'žonjace předmjeno',
            'hu': 'női keresztnév',
            'hy': 'իգական անձնանուն',
            'id': 'nama depan wanita',
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
            'sq': 'emër femëror',
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
            'ar': 'سنة في التقويم العبري',
            'bn': 'হিব্রু পঞ্জিকার বছর', 
            'ca': 'any de calendari hebreu', 
            'en': 'Hebrew calendar year', 
            'es': 'año del calendario hebreo', 
            'fa': 'سال در گاه‌شماری عبری', 
            'fr': 'année hébraïque', 
            'he': 'שנה עברית',
            'hy': 'Հրեական օրացույցի տարեթիվ',
            'id': 'tahun kalendar Ibrani',
            'nb': 'hebraisk kalenderår',
            'nn': 'hebraisk kalenderår',
            'ru': 'год еврейского календаря', 
            'sq': 'vit i kalendarik hebraik',
        }, 
        'Islamic calendar year': {
            'ar': 'سنة في التقويم الإسلامي',
            'bn': 'ইসলামী পঞ্জিকার বছর',
            'en': 'Islamic calendar year', 
            'es': 'año del calendario musulmán',
            'he': 'שנה בלוח השנה המוסלמי', 
            'id': 'tahun kalendar Islam',
            'nb': 'islamsk kalenderår',
            'nn': 'islamsk kalenderår',
            'sq': 'vit i kalendarik islamik',
        }, 
        'male given name': {
            'af': 'manlike voornaam',
            'ar': 'اسم شخصي مذكر',
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
            'fy': 'manlike foarnamme',
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
            'sq': 'emër mashkullor',
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
        'natural number': {
            'af': 'natuurlike getal',
            'als': 'natürlige Zahle',
            'an': 'numero natural',
            'ar': 'عدد طبيعي',
            'bn': 'প্রাকৃতিক সংখ্যা',
            'ca': 'nombre natural',
            'en': 'natural number',
            'en-ca': 'natural number',
            'en-gb': 'natural number',
            'eo': 'natura nombro',
            'es': 'número natural',
            'et': 'naturaalarv',
            'he': 'מספר טבעי',
            'hi': 'प्राकृतिक संख्या',
            'hy': 'Բնական թիվ',
            'ia': 'numero natural',
            'id': 'angka alami',
            'io': 'naturala nombro',
            'ka': 'ნატურალური რიცხვი',
            'kn': 'ಸ್ವಾಭಾವಿಕ ಸಂಖ್ಯೆ',
            'it': 'numero naturale',
            'la': 'numerus naturalis',
            'mwl': 'númaro natural',
            'nb': 'naturlig tall',
            'nn': 'naturleg tal',
            'pms': 'nùmer natural',
            'pt': 'número natural',
            'ro': 'număr natural',
            'scn': 'nùmmuru naturali',
            'sco': 'naitural nummer',
            'sc': 'nùmeru naturale',
            'szl': 'naturalno nůmera',
            'ru': 'натуральное число',
            'sq': 'numër natyror',
            'uk': 'натуральне число',
        },
        'scientific article': { # hay quien pone la fecha https://www.wikidata.org/wiki/Q19983493
            'ar': 'مقالة علمية',
            'ast': 'artículu científicu',
            'bn': 'বৈজ্ঞানিক নিবন্ধ',
            'ca': 'article científic',
            'en': 'scientific article',
            'eo': 'scienca artikolo',
            'es': 'artículo científico',
            'et': 'teaduslik artikkel',
            'fr': 'article scientifique',
            'fy': 'wittenskiplik artikel',
            'he': 'מאמר מדעי',
            'gl': 'artigo científico',
            'id': 'artikel ilmiah',
            'io': 'ciencala artiklo',
            'it': 'articolo scientifico',
            'nb': 'vitenskapelig artikkel',
            'nl': 'wetenschappelijk artikel',
            'nn': 'vitskapeleg artikkel',
            'pt': 'artigo científico',
            'pt-br': 'artigo científico',
            'ro': 'articol științific',
            'ru': 'научная статья',
            'sq': 'artikull shkencor',
            'uk': 'наукова стаття',
        }, 
        'species of alga': {
            'bn': 'শৈবালের প্রজাতি',
            'en': 'species of alga',
            'es': 'especie de alga',
            'gl': 'especie de alga',
            'he': 'מין של אצה',
            'io': 'speco di algo',
            'ro': 'specie de alge',
            'sq': 'lloj i algave',
        },
        'species of amphibian': {
            'bn': 'উভচর প্রাণীর প্রজাতি',
            'ca': 'espècie d\'amfibi',
            'en': 'species of amphibian',
            'es': 'especie de amfibio',
            'fr': 'espèce d\'amphibiens',
            'io': 'speco di amfibio',
            #'it': 'specie di anfibio', or anfibi?
            'pt': 'espécie de anfíbio',
            'he': 'מין של דו-חיים',
            'ro': 'specie de amfibieni',
            'sq': 'lloj i amfibeve',
        },
        'species of arachnid': {
            'bn': 'অ্যারাকনিডের প্রজাতি',
            'ca': 'espècie d\'aràcnid',
            'en': 'species of arachnid',
            'es': 'especie de arácnido',
            'fr': 'espèce d\'araignées',
            'io': 'speco di araneo',
            'it': 'specie di ragno',
            'pt': 'espécie de aracnídeo',
            'he': 'מין של עכביש',
            'ro': 'specie de arahnide',
        },
        'species of insect': { #las descripciones DE y FR tienen mayor precision y serian mas deseables
        #decidir que hacer
        # https://query.wikidata.org/#SELECT%20%3FitemDescription%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ16521.%0A%20%20%20%20%3Fitem%20wdt%3AP105%20wd%3AQ7432.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22species%20of%20insect%22%40en.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER%28LANG%28%3FitemDescription%29%20%3D%20%22de%22%29.%20%20%7D%0A%09FILTER%20%28BOUND%28%3FitemDescription%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC%28%3Fcount%29
            'an': 'especie d\'insecto',
            'bg': 'вид насекомо',
            'bn': 'কীটপতঙ্গের প্রজাতি',
            'ca': "espècie d'insecte",
            'en': 'species of insect',
            'es': 'especie de insecto',
            'fr': 'espèce d\'insectes',
            'gl': 'especie de insecto',
            'hy': 'միջատների տեսակ',
            'id': 'spesies serangga',
            'io': 'speco di insekto',
            'nb': 'insektart',
            'nn': 'insektart',
            'pt': 'espécie de inseto',
            'pt-br': 'espécie de inseto',
            'ro': 'specie de insecte',
            'ru': 'вид насекомых',
            'sq': 'lloj i insekteve',
            'ta': 'பூச்சி இனம்',
            'he': 'מין של חרק',
        },
        'species of mollusc': {
            'bn': 'মলাস্কার প্রজাতি',
            'ca': 'espècie de mol·lusc',
            'en': 'species of mollusc',
            'es': 'especie de molusco',
            'gl': 'especie de molusco',
            'io': 'speco di molusko',
            'pt': 'espécie de molusco',
            'he': 'מין של רכיכה',
            'ro': 'specie de moluște',
            'ru': 'вид моллюсков',
            'sq': 'lloj i molusqeve',
        },
        'species of plant': {
            'bg': 'вид растение',
            'bn': 'উদ্ভিদের প্রজাতি',
            'ca': 'espècie de planta',
            'en': 'species of plant',
            'es': 'especie de planta',
            'gl': 'especie de planta',
            'hy': 'բույսերի տեսակ',
            'he': 'מין של צמח',
            'io': 'speco di planto',
            'ro': 'specie de plante',
            'ru': 'вид растений',
            'sq': 'lloj i bimëve',
        },
        'village in China': {
            'an': 'pueblo d\'a Republica Popular de China', #o 'pueblo de China'
            'ar': 'قرية في الصين',
            'as': 'চীনৰ এখন গাওঁ',
            'bn': 'চীনের একটি গ্রাম',
            'bpy': 'চীনর আহান গাঙ',
            'ca': 'poble de la Xina',
            'de': 'Dorf in China',
            'el': 'οικισμός της Λαϊκής Δημοκρατίας της Κίνας',
            'en': 'village in China',
            'eo': 'vilaĝo en Ĉinio',
            'es': 'aldea de la República Popular China',
            'et': 'küla Hiinas',
            'fi': 'kylä Kiinassa',
            'fr': 'village chinois',
            'fy': 'doarp yn Sina',
            'gu': 'ચીનનું ગામ',
            'he': 'כפר ברפובליקה העממית של סין',
            'hi': 'चीन का गाँव',
            'hy': 'գյուղ Չինաստանում',
            'id': 'desa di Tiongkok',
            'io': 'vilajo en Chinia',
            'it': 'villaggio cinese',
            'ja': '中国の村',
            'kn': 'ಚೈನಾ ದೇಶದ ಗ್ರಾಮ',
            'mr': 'चीनमधील गाव',
            'nb': 'landsby i Kina',
            'ne': 'चीनका गाउँहरू',
            'nn': 'landsby i Kina',
            'nl': 'dorp in China',
            'oc': 'vilatge chinés',
            'or': 'ଚୀନର ଗାଁ',
            'pt-br': 'vila chinesa',
            'ur': 'چین کا گاؤں',
            'ro': 'sat din China',
            'ru': 'деревня КНР',
            'sq': 'fshat në Kinë',
            'ta': 'சீனாவின் கிராமம்',
            'te': 'చైనాలో గ్రామం',
        },
        'Wikimedia category': { #Q4167836
            'ace': 'kawan Wikimèdia',
            'af': 'Wikimedia-kategorie',
            'an': 'categoría de Wikimedia',
            'ar': 'تصنيف ويكيميديا',
            #'arz': 'ويكيبيديا:تصنيف',
            'ast': 'categoría de Wikimedia',
            'ba': 'Викимедиа категорияһы',
            'bar': 'Wikimedia-Kategorie',
            'be': 'катэгорыя ў праекце Вікімедыя',
            'be-tarask': 'катэгорыя ў праекце Вікімэдыя',
            'bg': 'категория на Уикимедия',
            'bho': 'विकिपीडिया:श्रेणी',
            'bjn': 'tumbung Wikimedia',
            'bn': 'উইকিমিডিয়া বিষয়শ্রেণী',
            'br': 'pajenn rummata eus Wikimedia',
            'bs': 'kategorija na Wikimediji',
            'bug': 'kategori Wikimedia',
            'ca': 'categoria de Wikimedia',
            #'ce': 'Викимедиа проектан категореш',
            #'ceb': 'Wikimedia:Kategorisasyon',
            'ckb': 'پۆلی ویکیمیدیا',
            'cs': 'kategorie na projektech Wikimedia',
            'cy': 'tudalen categori Wikimedia',
            'da': 'Wikimedia-kategori',
            'de-at': 'Wikimedia-Kategorie',
            'de-ch': 'Wikimedia-Kategorie',
            'de': 'Wikimedia-Kategorie',
            'el': 'κατηγορία εγχειρημάτων Wikimedia',
            'en': 'Wikimedia category',
            'en-ca': 'Wikimedia category',
            'en-gb': 'Wikimedia category',
            'eo': 'kategorio en Vikimedio',
            'es': 'categoría de Wikimedia',
            'et': 'Wikimedia kategooria',
            'eu': 'Wikimediako kategoria',
            'fa': 'ردهٔ ویکی‌پدیا',
            'fi': 'Wikimedia-luokka',
            'fr': 'page de catégorie de Wikimedia',
            'fy': 'Wikimedia-kategory',
            'gl': 'categoría de Wikimedia',
            'gsw': 'Wikimedia-Kategorie',
            'gu': 'વિકિપીડિયા શ્રેણી',
            'he': 'דף קטגוריה',
            'hi': 'विकिमीडिया श्रेणी',
            'hr': 'kategorija na Wikimediji',
            'hu': 'Wikimédia-kategória',
            'hy': 'Վիքիմեդիայի նախագծի կատեգորիա',
            'id': 'kategori Wikimedia',
            'ilo': 'kategoria ti Wikimedia',
            'it': 'categoria di un progetto Wikimedia',
            'ja': 'ウィキメディアのカテゴリ',
            'ko': '위키미디어 분류',
            'ky': 'Wikimedia категориясы',
            'lb': 'Wikimedia-Kategorie',
            'li': 'Wikimedia-categorie',
            'lv': 'Wikimedia projekta kategorija',
            'mk': 'Викимедиина категорија',
            'nap': 'categurìa \'e nu pruggette Wikimedia',
            'nb': 'Wikimedia-kategori',
            'nds': 'Wikimedia-Kategorie',
            'nl': 'Wikimedia-categorie',
            'nn': 'Wikimedia-kategori',
            'pl': 'kategoria w projekcie Wikimedia',
            'pt': 'categoria de um projeto da Wikimedia',
            'pt-br': 'categoria de um projeto da Wikimedia',
            'ro': 'categorie în cadrul unui proiect Wikimedia',
            'ru': 'категория в проекте Викимедиа',
            'sco': 'Wikimedia category',
            'se': 'Wikimedia-kategoriija',
            'sk': 'kategória projektov Wikimedia',
            'sl': 'kategorija Wikimedije',
            'sq': 'kategori e Wikimedias',
            'sr': 'категорија на Викимедији',
            'sv': 'Wikimedia-kategori',
            'tg': 'гурӯҳи Викимедиа',
            'tg-cyrl': 'гурӯҳ дар лоиҳаи Викимедиа',
            'tg-latn': 'gurühi Vikimedia',
            'tr': 'Vikimedya kategorisi',
            'uk': 'категорія проекту Вікімедіа',
            'vi': 'thể loại Wikimedia',
            'yo': 'ẹ̀ka Wikimedia',
            'yue': '維基媒體分類',
            'zea': 'Wikimedia-categorie',
            'zh': '维基媒体分类',
            'zh-cn': '维基媒体分类',
            'zh-hans': '维基媒体分类',
            'zh-hant': '維基媒體分類',
            'zh-hk': '維基媒體分類',
            'zh-mo': '維基媒體分類',
            'zh-my': '维基媒体分类',
            'zh-sg': '维基媒体分类',
            'zh-tw': '維基媒體分類',
        },
        'Wikimedia disambiguation page': { #Q4167410
            'an': 'pachina de desambigación',
            'ar': 'صفحة توضيح لويكيميديا',
            'bg': 'Уикимедия пояснителна страница',
            'bn': 'উইকিমিডিয়া দ্ব্যর্থতা নিরসন পাতা',
            'bs': 'čvor stranica na Wikimediji',
            'ca': 'pàgina de desambiguació de Wikimedia',
            'ckb': 'پەڕەی ڕوونکردنەوەی ویکیمیدیا',
            'cs': 'rozcestník na projektech Wikimedia',
            'da': 'Wikimedia-flertydigside',
            'de': 'Wikimedia-Begriffsklärungsseite',
            'de-at': 'Wikimedia-Begriffsklärungsseite',
            'de-ch': 'Wikimedia-Begriffsklärungsseite',
            'el': 'σελίδα αποσαφήνισης εγχειρημάτων Wikimedia',
            'en': 'Wikimedia disambiguation page',
            'en-ca': 'Wikimedia disambiguation page',
            'en-gb': 'Wikimedia disambiguation page',
            'eo': 'Vikimedia apartigilo',
            'es': 'página de desambiguación de Wikimedia',
            'et': 'Wikimedia täpsustuslehekülg',
            'eu': 'Wikimediako argipen orri',
            'fa': 'یک صفحهٔ ابهام\u200cزدایی در ویکی\u200cپدیا',
            'fi': 'Wikimedia-täsmennyssivu',
            'fr': 'page d\'homonymie de Wikimedia',
            'fy': 'Wikimedia-betsjuttingsside',
            'gl': 'páxina de homónimos de Wikimedia',
            'gsw': 'Wikimedia-Begriffsklärigssite',
            'gu': 'સ્પષ્ટતા પાનું',
            'he': 'דף פירושונים',
            'hi': 'बहुविकल्पी पृष्ठ',
            'hr': 'razdvojbena stranica na Wikimediji',
            'hu': 'Wikimédia-egyértelműsítőlap',
            'hy': 'Վիքիմեդիայի նախագծի բազմիմաստության փարատման էջ',
            'id': 'halaman disambiguasi Wikimedia',
            'is': 'aðgreiningarsíða á Wikipediu',
            'it': 'pagina di disambiguazione di un progetto Wikimedia',
            'ja': 'ウィキメディアの曖昧さ回避ページ',
            'ka': 'მრავალმნიშვნელოვანი',
            'ko': '위키미디어 동음이의어 문서',
            'lb': 'Wikimedia-Homonymiesäit',
            'li': 'Wikimedia-verdudelikingspazjena',
            'lv': 'Wikimedia projekta nozīmju atdalīšanas lapa',
            'min': 'laman disambiguasi',
            'mk': 'појаснителна страница',
            'ms': 'laman nyahkekaburan',
            'nb': 'Wikimedia-pekerside',
            'nds': 'Sied för en mehrdüdig Begreep op Wikimedia',
            'nl': 'Wikimedia-doorverwijspagina',
            'nn': 'Wikimedia-fleirtydingsside',
            'or': 'ବହୁବିକଳ୍ପ ପୃଷ୍ଠା',
            'pl': 'strona ujednoznaczniająca w projekcie Wikimedia',
            'pt': 'página de desambiguação da Wikimedia',
            'ro': 'pagină de dezambiguizare Wikimedia',
            'ru': 'страница значений в проекте Викимедиа',
            'sco': 'Wikimedia disambiguation page',
            'sk': 'rozlišovacia stránka',
            'sl': 'razločitvena stran Wikimedije',
            'sq': 'faqe kthjelluese e Wikimedias',
            'sr': 'вишезначна одредница на Викимедији',
            'sv': 'Wikimedia-förgreningssida',
            'tg': 'саҳифаи маъноҳои Викимедиа',
            'tg-cyrl': 'саҳифаи маъноҳои Викимедиа',
            'tg-latn': "sahifai ma'nohoi Vikimedia",
            'tr': 'Vikimedya anlam ayrımı sayfası',
            'tt': 'Мәгънәләр бите Викимедиа проектында',
            'tt-cyrl': 'Мәгънәләр бите Викимедиа проектында',
            'tt-latn': 'Mäğnälär bite Wikimedia proyektında',
            'uk': 'сторінка значень у проекті Вікімедіа',
            'vi': 'trang định hướng Wikimedia',
            'yo': 'ojúewé ìṣojútùú Wikimedia',
            'yue': '維基媒體搞清楚頁',
            'zea': 'Wikimedia-deurverwiespagina',
            'zh': '维基媒体消歧义页',
            'zh-cn': '维基媒体消歧义页',
            'zh-hans': '维基媒体消歧义页',
            'zh-hant': '維基媒體消歧義頁',
            'zh-hk': '維基媒體消歧義頁',
            'zh-mo': '維基媒體消歧義頁',
            'zh-my': '维基媒体消歧义页',
            'zh-sg': '维基媒体消歧义页',
            'zh-tw': '維基媒體消歧義頁',
        },
        'Wikimedia list article': { #Q13406463
            'ace': 'teunuléh dapeuta Wikimèdia',
            'af': 'Wikimedia lysartikel',
            'an': 'articlo de lista de Wikimedia',
            'ar': 'قائمة ويكيميديا',
            'as': 'ৱিকিপিডিয়া:ৰচনাশৈলীৰ হাতপুথি',
            'ast': 'artículu de llista de Wikimedia',
            'ba': 'Wikimedia-Listn',
            'be': 'спіс атыкулаў у адным з праектаў Вікімедыя',
            'bn': 'উইকিমিডিয়ার তালিকা নিবন্ধ',
            'bs': 'spisak na Wikimediji',
            'ca': 'article de llista de Wikimedia',
            'cs': 'seznam na projektech Wikimedia',
            'da': 'Wikimedia liste',
            'de': 'Wikimedia-Liste',
            'de-at': 'Wikimedia-Liste',
            'de-ch': 'Wikimedia-Liste',
            'el': 'κατάλογος εγχειρήματος Wikimedia',
            'en': 'Wikimedia list article',
            'en-ca': 'Wikimedia list article',
            'en-gb': 'Wikimedia list article',
            'eo': 'listartikolo en Vikimedio',
            'es': 'artículo de lista de Wikimedia',
            'et': 'Wikimedia loend',
            'eu': 'Wikimediako zerrenda artikulua',
            'fi': 'Wikimedia-luetteloartikkeli',
            'fr': 'page de liste de Wikimedia',
            'fy': 'Wikimedia-list',
            'gl': 'artigo de listas da Wikimedia',
            'he': 'רשימת ערכים',
            'hr': 'popis na Wikimediji',
            'hy': 'Վիքիմեդիայի նախագծի ցանկ',
            'id': 'artikel daftar Wikimedia',
            'ia': 'lista de un projecto de Wikimedia',
            'it': 'lista di un progetto Wikimedia',
            'ja': 'ウィキメディアの一覧記事',
            'ko': '위키미디어 목록 항목',
            'lb': 'Wikimedia-Lëschtenartikel',
            'li': 'Wikimedia-lies',
            'mk': 'список на статии на Викимедија',
            'ms': 'rencana senarai Wikimedia',
            'nb': 'Wikimedia-listeartikkel',
            'nl': 'Wikimedia-lijst',
            'nn': 'Wikimedia-listeartikkel',
            'oc': 'lista d\'un projècte Wikimèdia',
            'pl': 'lista w projekcie Wikimedia',
            'ro': 'articol-listă în cadrul unui proiect Wikimedia',
            'ru': 'статья-список в проекте Викимедиа',
            'sco': 'Wikimedia leet airticle',
            'si': 'විකිමීඩියා ලැයිස්තු ලිපිය',
            'sk': 'zoznamový článok projektov Wikimedia',
            'sl': 'seznam Wikimedije',
            'sq': 'artikull-listë e Wikimedias',
            'sr': 'списак на Викимедији',
            'sv': 'Wikimedia-listartikel',
            'ta': 'விக்கிப்பீடியா:பட்டியலிடல்',
            'tg': 'саҳифаи феҳристӣ',
            'tg-cyrl': 'мақолаи феҳристӣ',
            'tg-latn': 'sahifai fehristī',
            'th': 'บทความรายชื่อวิกิมีเดีย',
            'tr': 'Vikimedya liste maddesi',
            'uk': 'сторінка-список у проекті Вікімедіа',
            'vi': 'bài viết danh sách Wikimedia',
            'yi': 'וויקימעדיע ליסטע',
            'yo': 'ojúewé àtojọ Wikimedia',
            'zea': 'Wikimedia-lieste',
            'zh': '维基媒体列表条目',
            'zh-cn': '维基媒体列表条目',
            'zh-hans': '维基媒体列表条目',
            'zh-hant': '維基媒體列表條目',
            'zh-hk': '維基媒體列表條目',
            'zh-mo': '維基媒體列表條目',
            'zh-my': '维基媒体列表条目',
            'zh-sg': '维基媒体列表条目',
            'zh-tw': '維基媒體列表條目'
        },
        'Wikimedia template': { #Q11266439
            'an': 'plantilla de Wikimedia',
            'ar': 'قالب ويكيميديا', 
            'arz': 'ويكيبيديا:قوالب', 
            'ast': 'plantía de proyectu', 
            'ba': 'Викимедиа ҡалыбы', 
            'bar': 'Wikimedia-Vorlog', 
            'be': 'шаблон праекта Вікімедыя', 
            'be-tarask': 'шаблён праекту Вікімэдыя', 
            'bg': 'Уикимедия шаблон', 
            'bn': 'উইকিমিডিয়া টেমপ্লেট', 
            'bs': 'šablon Wikimedia', 
            'ca': 'plantilla de Wikimedia', 
            'ce': 'Викимедин проектан кеп', 
            'cs': 'šablona na projektech Wikimedia', 
            'cy': 'nodyn Wikimedia', 
            'da': 'Wikimedia-skabelon', 
            'de': 'Wikimedia-Vorlage', 
            'el': 'Πρότυπο εγχειρήματος Wikimedia', 
            'en': 'Wikimedia template', 
            'en-ca': 'Wikimedia template', 
            'en-gb': 'Wikimedia template', 
            'eo': 'Vikimedia ŝablono', 
            'es': 'plantilla de Wikimedia', 
            'et': 'Wikimedia mall', 
            'eu': 'Wikimediako txantiloia', 
            'fa': 'الگوی ویکی‌مدیا', 
            'fi': 'Wikimedia-malline', 
            'fo': 'fyrimynd Wikimedia', 
            'fr': 'modèle de Wikimedia', 
            'frr': 'Wikimedia-föörlaag', 
            'fy': 'Wikimedia-berjocht', 
            'gl': 'modelo da Wikimedia', 
            'gsw': 'Wikimedia-Vorlage', 
            'gu': 'વિકિપીડિયા ઢાંચો', 
            'he': 'תבנית של ויקימדיה', 
            'hu': 'Wikimédia-sablon', 
            'hy': 'Վիքիմեդիայի նախագծի կաղապար', 
            'id': 'templat Wikimedia', 
            'ilo': 'plantilia ti Wikimedia', 
            'it': 'template di un progetto Wikimedia', 
            'ja': 'ウィキメディアのテンプレート', 
            'jv': 'cithakan Wikimedia', 
            'ka': 'ვიკიმედიის თარგი', 
            'ko': '위키미디어 틀', 
            'ku-latn': 'şablona Wîkîmediyayê', 
            'la': 'formula Vicimediorum', 
            'lb': 'Wikimedia-Schabloun', 
            'li': 'Wikimedia-sjabloon', 
            'lt': 'Vikimedijos šablonas', 
            'lv': 'Wikimedia projekta veidne', 
            'mk': 'шаблон на Викимедија', 
            'ml': 'വിക്കിമീഡിയ ഫലകം', 
            'mr': 'विकिपीडिया:साचा', 
            'ms': 'Templat Wikimedia', 
            'nb': 'Wikimedia-mal', 
            'nds': 'Wikimedia-Vörlaag', 
            'nds-nl': 'Wikimedia-mal', 
            'nl': 'Wikimedia-sjabloon', 
            'nn': 'Wikimedia-mal',
            'oc': 'modèl de Wikimèdia', 
            'or': 'ଉଇକିମିଡ଼ିଆ ଛାଞ୍ଚ', 
            'pam': 'Ulmang pang-Wikimedia', 
            'pl': 'szablon w projekcie Wikimedia', 
            'ps': 'ويکيمېډيا کينډۍ', 
            'pt': 'predefinição da Wikimedia', 
            'pt-br': 'predefinição da Wikimedia', 
            'ro': 'format Wikimedia', 
            'ru': 'шаблон проекта Викимедиа', 
            'sco': 'Wikimedia template', 
            'se': 'Wikimedia-málle',
            'sk': 'šablóna projektov Wikimedia', 
            'sq': 'stampë e Wikimedias', 
            'sr': 'Викимедијин шаблон', 
            'sr-ec': 'Викимедијин шаблон', 
            'stq': 'Wikimedia-Foarloage', 
            'sv': 'Wikimedia-mall', 
            'sw': 'kigezo cha Wikimedia', 
            'ta': 'விக்கிமீடியா வார்ப்புரு', 
            'te': 'వికీమీడియా మూస', 
            'tg': 'шаблони лоиҳаи Викимедиа', 
            'tg-cyrl': 'шаблони лоиҳаи Викимедиа', 
            'tg-latn': 'shabloni loihai Vikimedia', 
            'th': 'หน้าแม่แบบวิกิมีเดีย', 
            'tl': 'Padrong pang-Wikimedia', 
            'tr': 'Vikimedya şablonu',
            'uk': 'шаблон у проекті Вікімедіа', 
            'vi': 'bản mẫu Wikimedia', 
            'yo': 'àdàkọ Wikimedia',
            'yue': '維基媒體模',
            'zea': 'Wikimedia-sjabloon',
            'zh': '维基媒体模板', 
            'zh-cn': '维基媒体模板', 
            'zh-hans': '维基媒体模板', 
            'zh-hant': '維基媒體模板', 
            'zh-hk': '維基媒體模板', 
            'zh-tw': '維基媒體模板', 
        },
        'Wikinews article': { #Q17633526
            'an': 'articlo de Wikinews',
            'ar': 'مقالة ويكي أخبار',
            'bar': 'Artike bei Wikinews',
            'bn': 'উইকিসংবাদের নিবন্ধ',
            'bs': 'Wikinews članak',
            'ca': 'article de Viquinotícies', 
            'cs': 'článek na Wikizprávách',
            'da': 'Wikinews-artikel',
            'de': 'Artikel bei Wikinews', 
            'el': 'Άρθρο των Βικινέων', 
            'en': 'Wikinews article', 
            'en-ca': 'Wikinews article', 
            'en-gb': 'Wikinews article', 
            'eo': 'artikolo de Vikinovaĵoj', 
            'es': 'artículo de Wikinoticias', 
            'eu': 'Wikialbisteakeko artikulua',
            'fi': 'Wikiuutisten artikkeli',
            'fr': 'article de Wikinews', 
            'fy': 'Wikinews-artikel', 
            'he': 'כתבה בוויקיחדשות',
            'hu': 'Wikihírek-cikk',
            'hy': 'Վիքիլուրերի հոդված',
            'id': 'artikel Wikinews',
            'it': 'articolo di Wikinotizie', 
            'ja': 'ウィキニュースの記事',
            'ko': '위키뉴스 기사',
            'ku-latn': 'gotara li ser Wîkînûçeyê',
            'li': 'Wikinews-artikel', 
            'lt': 'Vikinaujienų straipsnis', 
            'mk': 'напис на Викивести', 
            'nb': 'Wikinytt-artikkel', 
            'nl': 'Wikinieuws-artikel', 
            'nn': 'Wikinytt-artikkel',
            'or': 'ଉଇକି ସୂଚନା ପତ୍ରିକା',
            'pl': 'artykuł w Wikinews', 
            'ps': 'د ويکيخبرونو ليکنه',
            'pt': 'artigo do Wikinotícias', 
            'ro': 'articol în Wikiștiri', 
            'ru': 'статья Викиновостей',
            'sq': 'artikull i Wikinews',
            'sr': 'чланак са Викивести',
            'sv': 'Wikinews-artikel',
            'te': 'వికీవార్త వ్యాసం',
            'tg': 'саҳифаи Викиахбор',
            'tg-cyrl': 'саҳифаи Викиахбор',
            'tg-latn': 'sahifai Vikiakhbor',
            'th': 'เนื้อหาวิกิข่าว', 
            'tr': 'Vikihaber maddesi',
            'uk': 'стаття Вікіновин', 
            'zea': 'Wikinews-artikel',
            'zh': '維基新聞新聞稿', 
            'zh-cn': '维基新闻新闻稿', 
            'zh-hans': '维基新闻新闻稿', 
            'zh-hant': '維基新聞新聞稿', 
            'zh-hk': '維基新聞新聞稿', 
            'zh-mo': '維基新聞新聞稿', 
            'zh-my': '维基新闻新闻稿', 
            'zh-sg': '维基新闻新闻稿', 
            'zh-tw': '維基新聞新聞稿', 
        }, 
        'year': {
            'af': 'jaar',
            'an': 'anyo',
            'ar': 'سنة',
            'ast': 'añu',
            'be': 'год', 
            'be-tarask': 'год',
            'bg': 'година',
            'bn': 'বছর',
            'br': 'bloavezh',
            'bs': 'godina',
            'ca': 'any',
            'cs': 'rok',
            'da': 'år',
            'de': 'Jahr',
            'el': 'έτος',
            'en': 'year',
            'en-ca': 'year',
            'en-gb': 'year',
            'eo': 'jaro',
            'es': 'año',
            'et': 'aasta',
            'fi': 'vuosi',
            'fr': 'année',
            'fy': 'jier',
            'gl': 'ano',
            'gsw': 'joor',
            'he': 'שנה',
            'hr': 'Godina',
            'ht': 'Lane',
            'hu': 'Év',
            'hy': 'տարեթիվ',
            'ia': 'anno',
            'id': 'tahun',
            'ilo': 'tawen',
            'io': 'yaro',
            'is': 'ár',
            'it': 'anno',
            'ja': '年',
            'ka': 'წელი',
            'ko': '연도',
            'ku': 'Sal',
            'la': 'annus',
            'lt': 'Metai',
            'lv': 'gads',
            'mhr': 'Идалык',
            'min': 'taun',
            'mk': 'година',
            'ms': 'Tahun',
            'nan': 'nî',
            'nb': 'år',
            'nds': 'Johr',
            'nl': 'jaar',
            'nn': 'år',
            'or': 'ବର୍ଷ',
            'pl': 'rok',
            'pt': 'ano',
            'ro': 'an',
            'ru': 'год',
            'sh': 'godina',
            'sk': 'Rok',
            'sl': 'Leto',
            #'sq': 'vit', or viti?
            'sr': 'Година',
            'srn': 'Yari',
            'sv': 'år',
            'th': 'ปี',
            'tl': 'taon',
            'tr': 'yıl',
            'uk': 'рік',
            'vo': 'yel',
            'vi': 'năm',
            'war': 'Tuig',
            'yi': 'יאר',
            'yue': '年',
            'zh': '年',
            'zh-hans': '年份',
            'zh-hant': '年份',
        },
    }
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    querylimit = 10000
    queries = {
        'asteroid': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q3863 ;
                  wdt:P31 ?instance .
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 200000, querylimit)
        ],
        
        'chemical compound': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q11173 ;
                  wdt:P31 ?instance .
            #?item schema:description "chemical compound"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 250000, querylimit)
        ],
        
        'encyclopedic article': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q17329259 ;
                  wdt:P31 ?instance .
            ?item schema:description "encyclopedic article"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 300000, querylimit)
        ],
        
        'family name': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q101352 ;
                  wdt:P31 ?instance .
            ?item schema:description "family name"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 200000, querylimit)
        ], 
        
        'family of crustaceans': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of crustaceans"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'family of insects': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of insects"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'family of molluscs': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of molluscs"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'family of plants': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of plants"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'female given name': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q11879590 ;
                  wdt:P31 ?instance .
            ?item schema:description "female given name"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'genus of algae': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of algae"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ], 
        
        'genus of amphibians': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of amphibians"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000, querylimit)
        ], 
        
        'genus of arachnids': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of arachnids"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 20000, querylimit)
        ], 
        
        'genus of birds': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of birds"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000, querylimit)
        ], 
        
        'genus of fishes': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of fishes"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ], 
        
        'genus of fungi': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of fungi"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 20000, querylimit)
        ], 
        
        'genus of insects': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of insects"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 100000, querylimit)
        ], 
        
        'genus of mammals': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of mammals"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ], 
        
        'genus of molluscs': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of molluscs"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 20000, querylimit)
        ], 
        
        'genus of plants': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of plants"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 50000, querylimit)
        ], 
        
        'genus of reptiles': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of reptiles"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000, querylimit)
        ], 
                    
        'Hebrew calendar year': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q577 ;
                  wdt:P31 ?instance .
            ?item schema:description "Hebrew calendar year"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'Islamic calendar year': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q577 ;
                  wdt:P31 ?instance .
            ?item wdt:P361 wd:Q28892 .
            ?item schema:description "Islamic calendar year"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'male given name': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q12308941 ;
                  wdt:P31 ?instance .
            ?item schema:description "male given name"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """        
        ], 
        
        #'natural number': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ21199%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ200227%20%7D%20.%20%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22natural%20number%22%40en.%0A%7D%0A'],
        
        #'scientific article': [''], # hay quien pone la fecha https://www.wikidata.org/wiki/Q19983493
        
        'species of alga': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of alga"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of amphibian': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of amphibian"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of arachnid': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of arachnid"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of insect': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of insect"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000000, querylimit)    
        ], 
        
        'species of mollusc': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of mollusc"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of plant': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of plant"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 600000, querylimit)    
        ], 
        
        #'village in China': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ13100073%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstance%20.%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING(COUNT(%3Finstance)%20%3D%201)'],
        
        'Wikimedia category': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q4167836.
            ?item schema:description "Wikimedia category"@en.
        }
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 5000000, querylimit)
        ],
        
        'Wikimedia disambiguation page': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q4167410 ;
                  wdt:P31 ?instance .
            ?item schema:description "Wikimedia disambiguation page"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 2000000, querylimit)
        ], 
        
        'Wikimedia list article': [
        """
        SELECT ?item
        WHERE
        {
            ?item wdt:P31 wd:Q13406463 ;
                  wdt:P31 ?instance .
            ?item schema:description "Wikimedia list article"@en.
            #OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "es").  }
            #FILTER (!BOUND(?itemDescription))
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 500000, querylimit)
        ],
        
        #'Wikimedia list article': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ13406463%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstance%20.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22Wikimedia%20list%20article%22%40en.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING(COUNT(%3Finstance)%20%3D%201)'], #lists with language selector enabled
        #'Wikimedia list article': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ13406463%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstance%20.%0A%20%20%20%20%23%3Fitem%20schema%3Adescription%20%22Wikimedia%20list%20article%22%40en.%0A%20%20%20%20%23OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09%23FILTER%20(!BOUND(%3FitemDescription))%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING(COUNT(%3Finstance)%20%3D%201)'], #lists even without english description
        
        'Wikimedia template': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q11266439 ;
                  wdt:P31 ?instance .
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000000, querylimit)
        ], 
        
        'Wikinews article': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q17633526 ;
                  wdt:P31 ?instance .
            #?item schema:description "Wikinews article"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'year': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q577 ;
                  wdt:P31 ?instance .
            ?item schema:description "year"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
    }
    queries_list = [x for x in queries.keys()]
    queries_list.sort()
    skip = ''
    topics = [ #uncomment topics you want to add descriptions to
        #'asteroid',
        #'chemical compound',
        'encyclopedic article',
        
        #'family name',
        #'female given name',
        #'male given name',
        
        #'family of crustaceans',
        #'family of insects',
        #'family of molluscs',
        #'family of plants',
        
        #'genus of algae',
        #'genus of amphibians',
        #'genus of arachnids',
        #'genus of birds',
        #'genus of fishes',
        #'genus of fungi',
        #'genus of insects',
        #'genus of mammals',
        #'genus of molluscs',
        #'genus of plants',
        #'genus of reptiles',
        
        #'year',
        #'Hebrew calendar year',
        #'Islamic calendar year',
        
        #'species of alga',
        #'species of amphibian',
        #'species of arachnid',
        #'species of insect',
        #'species of mollusc',
        #'species of plant',
        
        #'Wikimedia disambiguation page', 
        #'Wikimedia list article', 
        #'Wikimedia template', 
    ]
    for topic in queries_list:
        if not topic in topics:
            continue
        for url in queries[topic]:
            url = url.strip()
            if not url.startswith('http'):
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(url))
            url = '%s&format=json' % (url)
            print("Loading...", url)
            sparql = getURL(url=url)
            json1 = loadSPARQL(sparql=sparql)
            
            qlist = []
            for result in json1['results']['bindings']:
                q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                if q:
                    qlist.append(q)
            if not qlist: #empty query result? maybe no more Q
                break
            
            for q in qlist:
                print('\n== %s [%s] ==' % (q, topic))
                if skip:
                    if q != skip:
                        print('Skiping...')
                        continue
                    else:
                        skip = ''
                
                item = pywikibot.ItemPage(repo, q)
                try: #to detect Redirect because .isRedirectPage fails
                    item.get()
                except:
                    print('Error while .get()')
                    continue
                
                #skiping items with en: sitelinks (temporal patch)
                #sitelinks = item.sitelinks
                #if 'enwiki' in sitelinks:
                #    continue
                
                descriptions = item.descriptions
                addedlangs = []
                fixedlangs = []
                for lang in translations[topic].keys():
                    if lang in descriptions.keys():
                        if topic in fixthiswhenfound and \
                           lang in fixthiswhenfound[topic] and \
                           descriptions[lang] in fixthiswhenfound[topic][lang]:
                            descriptions[lang] = translations[topic][lang]
                            fixedlangs.append(lang)
                    else:
                        descriptions[lang] = translations[topic][lang]
                        addedlangs.append(lang)
                
                if addedlangs or fixedlangs:
                    data = { 'descriptions': descriptions }
                    addedlangs.sort()
                    summary = 'BOT - '
                    if addedlangs:
                        if fixedlangs:
                            summary += 'Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs[:15]))
                            summary += ' / Fixing descriptions (%s languages): %s' % (len(fixedlangs), ', '.join(fixedlangs))
                        else:
                            summary += 'Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                    else:
                        if fixedlangs:
                            summary += 'Fixing descriptions (%s languages): %s' % (len(fixedlangs), ', '.join(fixedlangs))
                    print(summary)
                    try:
                        item.editEntity(data, summary=summary)
                    except:
                        print('Error while saving')
                        continue
    print("Finished successfully")

if __name__ == "__main__":
    main()
