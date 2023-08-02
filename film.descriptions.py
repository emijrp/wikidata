#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2023 emijrp <emijrp@gmail.com>
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
import random
import re
import sys
import time
import urllib.parse

import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    inputyear = False
    if len(sys.argv) > 1:
        inputyear = int(sys.argv[1])
    
    targetlangs = ['es', 'ca', 'gl', 'ast', 'an', 'ext', 'oc', 'it', 'pt', 'sv', 'de', 'nl', 'fy', 'fr', 'he', 'ar', 'ro', 'et', ]
    targetlangs = ['es'] #dejo es y uno poco probable que este completo
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
    if inputyear:
        yearstart = inputyear
        yearend = inputyear+1
    else:
        yearstart = 1880
        yearend = 2024
    years = list(range(yearstart, yearend))
    random.shuffle(targetlangs)
    #random.shuffle(years)
    for targetlang in targetlangs:
        for year in years:
            print(targetlang, year)
            for defaultdescen in [str(year)+' film by', str(year)+' film directed by', ]:
                query = """
SELECT ?item ?itemDescriptionEN
WHERE {
    ?item wdt:P31 wd:Q11424.
    ?item schema:description ?itemDescriptionEN.
    FILTER (CONTAINS(?itemDescriptionEN, "%s")). 
    OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "%s"). }
    FILTER (!BOUND(?itemDescription))
}""" % (defaultdescen, targetlang)
                
                #los q tienen ' and ' en español
                query = """
SELECT DISTINCT ?item ?itemDescriptionEN
WHERE {
    ?item wdt:P31 wd:Q11424.
    ?item schema:description ?itemDescriptionEN.
    FILTER (CONTAINS(?itemDescriptionEN, "%s")). 
    ?item schema:description ?itemDescriptionEN. FILTER(LANG(?itemDescriptionEN) = "en"). 
    FILTER (CONTAINS(?itemDescription, " and ")). 
    ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "%s").
}""" % (defaultdescen, targetlang)

                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
                url = '%s&format=json' % (url)
                print("Loading...", url)
                sparql = getURL(url=url)
                json1 = loadSPARQL(sparql=sparql)
                for result in json1['results']['bindings']:
                    q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                    descen = result['itemDescriptionEN']['value']
                    if not q or not descen:
                        continue
                    if not 'film by ' in descen:
                        continue
                    author = descen.split('film by ')[1].split(',')
                    if not author or len(author[0]) == 0:
                        continue
                    authors = []
                    for a in author:
                        if ' and ' in a:
                            authors += [aa.strip(',').strip(' ').strip(',') for aa in a.split(' and ')]
                        else:
                            authors.append(a.strip(',').strip(' ').strip(','))
                    item = pywikibot.ItemPage(repo, q)
                    item.get()
                    descriptions = item.descriptions
                    addedlangs = []
                    for lang in translations.keys():
                        if not lang in descriptions.keys() or (lang != "en" and lang in descriptions.keys() and ' and ' in descriptions[lang]):
                            translation = translations[lang]
                            translation = translation.replace('~YEAR~', str(year))
                            if len(authors) == 1:
                                translation = translation.replace('~AUTHOR~', ''.join(authors))
                            elif len(authors) == 2:
                                translation = translation.replace('~AUTHOR~', translationsand[lang].join(authors))
                            elif len(authors) > 2:
                                author_ = ', '.join(authors[:-1])
                                author_ = '%s%s%s' % (author_, translationsand[lang], authors[-1])
                                translation = translation.replace('~AUTHOR~', author_)
                            descriptions[lang] = translation
                            print(q, lang) #, authors.encode('utf-8'), lang, translation.encode('utf-8'))
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
