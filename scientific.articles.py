#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2022 emijrp <emijrp@gmail.com>
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
import random
import re
import sys
import time
import urllib.parse

import pywikibot
from wikidatafun import *

#mas adelante hacer queries para descripciones como (scientific article published on 01 January 1986)
#el pubdate lo capturamos asi que da igual
#https://query.wikidata.org/#SELECT%20%3FitemDescBase%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%20%20SERVICE%20bd%3Asample%20%7B%0A%20%20%20%20%3Fitem%20wdt%3AP31%20%3Fp31%20.%0A%20%20%20%20bd%3AserviceParam%20bd%3Asample.limit%20100000%20.%0A%20%20%20%20bd%3AserviceParam%20bd%3Asample.sampleType%20%22RANDOM%22%20.%0A%20%20%7D%0A%20%20%23%3Fitem%20wdt%3AP21%20wd%3AQ6581097.%0A%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescBase.%20FILTER%28LANG%28%3FitemDescBase%29%20%3D%20%22en%22%29.%20%20%7D%0A%20%20FILTER%20%28BOUND%28%3FitemDescBase%29%29%0A%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescTarget.%20FILTER%28LANG%28%3FitemDescTarget%29%20%3D%20%22es%22%29.%20%20%7D%0A%20%20FILTER%20%28%21BOUND%28%3FitemDescTarget%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescBase%0AORDER%20BY%20DESC%28%3Fcount%29%0ALIMIT%20100

def bnyear(year=''):
    digits = { '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯' }
    year = str(year)
    for k, v in digits.items():
        year = re.sub(k, v, year)
    return year

def generateTranslations(pubdate=''):
    fixthiswhenfound = {
        'bn': ['বৈজ্ঞানিক নিবন্ধ'], 
        'da': ['videnskabelig artikel'], 
        'es': ['artículo científico'], 
        'fr': ['article scientifique'], 
        'pt': ['artigo científico'], 
        'pt-br': ['artigo científico'],
    }
    translations = {
        'ar': 'مقالة علمية',
        'ast': 'artículu científicu',
        'bg': 'научна статия',
        'bn': '%s-এ প্রকাশিত বৈজ্ঞানিক নিবন্ধ' % (bnyear(pubdate.year)),
        'ca': 'article científic',
        'cs': 'vědecký článek',
        'da': 'videnskabelig artikel (udgivet %s)' % (pubdate.year),
        'de': 'wissenschaftlicher Artikel',
        'el': 'επιστημονικό άρθρο',
        #'en': 'scientific article',
        'eo': 'scienca artikolo',
        'es': 'artículo científico publicado en %s' % (pubdate.year),
        'et': 'teaduslik artikkel',
        'fa': 'مقالهٔ علمی', 
        'fi': 'tieteellinen artikkeli',
        'fr': 'article scientifique (publié %s)' % (pubdate.year),
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
        'pt': 'artigo científico (publicado na %s)' % (pubdate.year),
        'pt-br': 'artigo científico (publicado na %s)' % (pubdate.year),
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
        'ur': 'سائنسی مضمون',
        'vi': 'bài báo khoa học',
        'wuu': '%s年学术文章' % (pubdate.year),
        'yue': '%s年學術文章' % (pubdate.year),
        'zh': '%s年學術文章' % (pubdate.year),
        'zh-cn': '%s年学术文章' % (pubdate.year),
        'zh-hans': '%s年学术文章' % (pubdate.year),
        'zh-hant': '%s年學術文章' % (pubdate.year),
        'zh-hk': '%s年學術文章' % (pubdate.year),
        'zh-mo': '%s年學術文章' % (pubdate.year),
        'zh-my': '%s年学术文章' % (pubdate.year),
        'zh-sg': '%s年学术文章' % (pubdate.year),
        'zh-tw': '%s年學術文章' % (pubdate.year),
    }
    return fixthiswhenfound, translations

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    querylimit = 10000
    skip = ''
    #old query
    queries = [
    """
    SELECT ?item ?pubdate
    WHERE {
        ?item wdt:P31 wd:Q13442814.
        ?item wdt:P577 ?pubdate.
    }
    LIMIT %s
    OFFSET %s
    """ % (str(querylimit), str(offset)) for offset in range(10000000, 20000000, querylimit)
    ]
    #random query
    queries = [
    """
    SELECT ?item ?pubdate
    WHERE {
        SERVICE bd:sample {
            ?item wdt:P31 wd:Q13442814 .
            bd:serviceParam bd:sample.limit %s .
            bd:serviceParam bd:sample.sampleType "RANDOM" .
        }
    ?item wdt:P577 ?pubdate.
    ?item schema:description "scientific article"@en.
    OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "%s").  }
    FILTER (!BOUND(?itemDescription))
    }
    #random%s
    """ % (str(querylimit+i), random.choice(list(generateTranslations(pubdate=datetime.datetime.strptime('2099-01-01', '%Y-%m-%d'))[1].keys())), random.randint(1,1000000)) for i in range(1, 10000)
    ]
    
    for query in queries:
        time.sleep(1)
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
            for edit in ["add", "fix"]:
                fixthiswhenfound, translations = generateTranslations(pubdate=pubdate)
                if edit == "add":
                    fixthiswhenfound = {}
                
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
                    #time.sleep(1)
    print("Finished successfully")

if __name__ == '__main__':
    main()
