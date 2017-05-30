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
import re
import time

import pwb
import pywikibot
from wikidatafun import *

def getCount(url=''):
    if url:
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        for result in json1['results']['bindings']:
            count = int(result['count']['value'])
            return count
    return 0

def getExistCountForCountry(q=''):
    if q:
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20(COUNT(DISTINCT%20%3Fitem)%20AS%20%3Fcount)%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3AQ6581072.%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3A'+q+'.%0A%20%20%20%20FILTER%20EXISTS%20%7B%20%3Fwen%20schema%3Aabout%20%3Fitem%20.%20%3Fwen%20schema%3AinLanguage%20%22en%22%20%7D%0A%7D'
        return getCount(url=url)
    return 0
    
def getExistCountForUnknownCountry():
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20(COUNT(DISTINCT%20%3Fitem)%20AS%20%3Fcount)%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3AQ6581072.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP27%20%3Fcountry.%20%7D%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fwen%20schema%3Aabout%20%3Fitem%20.%20%3Fwen%20schema%3AinLanguage%20%22en%22%20%7D%0A%7D'
    return getCount(url=url)

def getTotalCountForCountry(q=''):
    if q:
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20(COUNT(DISTINCT%20%3Fitem)%20AS%20%3Fcount)%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3AQ6581072.%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3A'+q+'.%0A%7D'
        return getCount(url=url)
    return 0
    
def getTotalCountForUnknownCountry():
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20(COUNT(DISTINCT%20%3Fitem)%20AS%20%3Fcount)%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3AQ6581072.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP27%20%3Fcountry.%20%7D%20%23country%0A%7D'
    return getCount(url=url)

def main():
    countries = getAllCountries()
    totalexists = 0
    totaltotal = 0
    totalmissing = 0
    totaldonepercent = 0.0
    rowsplain = ''
    for countryLabel, countryQ in countries:
        exists = getExistCountForCountry(q=countryQ)
        total = getTotalCountForCountry(q=countryQ)
        missing = total - exists
        if total:
            donepercent = exists / (total / 100.0)
        else:
            donepercent = 0.0
        print(countryLabel, exists, total, donepercent)
        rowsplain += '\n{{User:Emijrp/All Human Knowledge/Women/row|country=%s|enwiki=%d|wikidata=%d|percentage=%.1d|redlinks=%d|country item=%s}}' % (countryLabel, exists, total, donepercent, missing, countryQ)
        totalexists += exists
        totaltotal += total
        totalmissing += missing
    #unknown country
    unknownexists = getExistCountForUnknownCountry()
    unknowntotal = getTotalCountForUnknownCountry()
    unknownmissing = unknowntotal - unknownexists
    totalexists += unknownexists
    totaltotal += unknowntotal
    totalmissing += unknownmissing
    unknowndonepercent = unknownexists / (unknowntotal / 100.0)
    rowsplain += '\n{{User:Emijrp/All Human Knowledge/Women/row|country=%s|enwiki=%d|wikidata=%d|percentage=%.1d|redlinks=%d|country item=}}' % ('Unknown', unknownexists, unknowntotal, unknowndonepercent, unknownmissing)
    #totals
    totaldonepercent = totalexists / (totaltotal / 100.0)
    print('Total', totalexists, totaltotal, totaldonepercent)
    output = """{| class="wikitable sortable plainlinks" style="text-align: center;"
! width=150px | Country !! Enwiki !! Wikidata !! Percent done !! Missing bios
|-
%s
|-
! Total !! data-sort-value=%d | {{formatnum:%d}} !! data-sort-value=%d | {{formatnum:%d}} !! data-sort-value=%.1d | {{Percentage bar|%.1d}} !! data-sort-value=%d | {{formatnum:%d}}
|}""" % (rowsplain, totalexists, totalexists, totaltotal, totaltotal, totaldonepercent, totaldonepercent, totalmissing, totalmissing)
    enwiki = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(enwiki, 'User:Emijrp/All Human Knowledge/Women')
    page.text = output
    page.save('BOT - Updating table')

if __name__ == '__main__':
    main()
