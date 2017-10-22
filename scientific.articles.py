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

import datetime
import dateutil.parser
import os
import re
import sys
import time
import urllib.parse

import pwb
import pywikibot
from wikidatafun import *

def bnyear(year=''):
    digits = { '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯' }
    year = str(year)
    for k, v in digits.items():
        year = re.sub(k, v, year)
    return year

def generateTranslations(pubdate=''):
    fixthiswhenfound = {
        'bn': ['বৈজ্ঞানিক নিবন্ধ'],
        'es': ['artículo científico'], 
    }
    translations = {
        'ar': 'مقالة علمية',
        'ast': 'artículu científicu',
        'bg': 'научна статия',
        'bn': '%s-এ প্রকাশিত বৈজ্ঞানিক নিবন্ধ' % (bnyear(pubdate.year)),
        'ca': 'article científic',
        'cs': 'vědecký článek',
        'da': 'videnskabelig artikel',
        'de': 'wissenschaftlicher Artikel',
        'el': 'επιστημονικό άρθρο',
        #'en': 'scientific article',
        'eo': 'scienca artikolo',
        'es': 'artículo científico publicado en %s' % (pubdate.year),
        'et': 'teaduslik artikkel',
        'fa': 'مقالهٔ علمی', 
        'fi': 'tieteellinen artikkeli',
        'fr': 'article scientifique',
        'gl': 'artigo científico',
        'he': 'מאמר מדעי',
        'hu': 'tudományos cikk',
        'hy': 'գիտական հոդված',
        #'id': 'artikel ilmiah', #or 'artikel sains' ?
        'it': 'articolo scientifico',
        'ja': '%s年の論文' % (pubdate.year),
        'ka': 'სამეცნიერო სტატია',
        'ko': '%s년 논문' % (pubdate.year),
        'lt': 'mokslinis straipsnis',
        'nan': '%s nî lūn-bûn' % (pubdate.year),
        'nb': 'vitenskapelig artikkel',
        'nl': 'wetenschappelijk artikel',
        'nn': 'vitskapeleg artikkel',
        'oc': 'article scientific',
        'pl': 'artykuł naukowy',
        'pt': 'artigo científico',
        'pt-br': 'artigo científico',
        'ro': 'articol științific',
        'ru': 'научная статья',
        'sk': 'vedecký článok',
        'sq': 'artikull shkencor',
        'sr': 'научни чланак',
        'sr-ec': 'научни чланак',
        'sr-el': 'naučni članak',
        'sv': 'vetenskaplig artikel',
        'tg': 'мақолаи илмӣ',
        'tg-cyrl': 'мақолаи илмӣ',
        'th': 'บทความทางวิทยาศาสตร์',
        'tl': 'artikulong pang-agham',
        'tr': 'bilimsel makale',
        'uk': 'наукова стаття',
        'vi': 'bài báo khoa học',
        'wuu': '%s年论文' % (pubdate.year),
        'yue': '%s年論文' % (pubdate.year),
        'zh': '%s年论文' % (pubdate.year),
        'zh-cn': '%s年论文' % (pubdate.year),
        'zh-hans': '%s年论文' % (pubdate.year),
        'zh-hant': '%s年論文' % (pubdate.year),
        'zh-hk': '%s年論文' % (pubdate.year),
        'zh-mo': '%s年論文' % (pubdate.year),
        'zh-my': '%s年论文' % (pubdate.year),
        'zh-sg': '%s年论文' % (pubdate.year),
        'zh-tw': '%s年論文' % (pubdate.year),
    }
    return fixthiswhenfound, translations

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    querylimit = 10000
    skip = 'Q36014642'
    queries = [
    """
    SELECT ?item ?pubdate
    WHERE {
        ?item wdt:P31 wd:Q13442814.
        ?item wdt:P577 ?pubdate.
    }
    LIMIT %s
    OFFSET %s
    """ % (str(querylimit), str(offset)) for offset in range(0, 10000000, querylimit)
    ]
    
    for query in queries:
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
        url = '%s&format=json' % (url)
        print("Loading...", url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            pubdate = result['pubdate']['value']
            if not q or not pubdate:
                break
            print('\n== %s ==' % (q))
            if skip:
                if q != skip:
                    print('Skiping...')
                    continue
                else:
                    skip = ''
            
            pubdate = dateutil.parser.parse(pubdate)
            fixthiswhenfound, translations = generateTranslations(pubdate=pubdate)
            item = pywikibot.ItemPage(repo, q)
            try: #to detect Redirect because .isRedirectPage fails
                item.get()
            except:
                print('Error while .get()')
                continue
            
            descriptions = item.descriptions
            #skip papers without english description
            if not 'en' in descriptions or not 'scientific article' in descriptions['en']:
                continue
            
            addedlangs = []
            fixedlangs = []
            for lang in translations.keys():
                if lang in descriptions:
                    if lang in fixthiswhenfound and \
                       descriptions[lang] in fixthiswhenfound[lang]:
                        descriptions[lang] = translations[lang]
                        fixedlangs.append(lang)
                else:
                    descriptions[lang] = translations[lang]
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

if __name__ == '__main__':
    main()
