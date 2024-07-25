#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 emijrp <emijrp@gmail.com>
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

import random
import re
import sys
import time
import urllib.parse

import pywikibot
from wikidatafun import *

def main():
    month2number = { "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06", "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12" }
    month2abrv = { "enero": "ene", "febrero": "feb", "marzo": "mar", "abril": "abr", "mayo": "may", "junio": "jun", "julio": "jul", "agosto": "ago", "septiembre": "sep", "octubre": "oct", "noviembre": "nov", "diciembre": "dic" }
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    skip = ''
    queries = [
    """
    SELECT DISTINCT ?item
    WHERE {
        ?item wdt:P31 wd:Q2912 .
    }
    """
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
            if not q:
                break
            print('\n== %s ==' % (q))
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
            
            #check if date
            labels = item.labels
            if not labels["es"]:
                print("No tiene label es, saltamos")
                continue
            if not re.search(r"(?m)^\d{1,2} de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de \d{4}$", labels["es"]):
                print("No tiene label en formato correcto, saltamos")
                continue
            
            day, month, year = labels["es"].split(" de ")
            if int(day) > 31 or int(day) < 1 or int(year) > 2100 or int(year) < 1583:
                print("Fecha se sale del rango, saltamos")
                continue
            
            #candidate aliases
            aliasDDMMAAAAhyphen00 = "%s-%s-%s" % ("%02d" % (int(day)), "%02d" % (int(month2number[month])), year)
            aliasDDMMAAAAhyphen0 = "%s-%s-%s" % (str(int(day)), str(int(month2number[month])), year)
            aliasDDMMAAAAhyphenabrv = "%s-%s-%s" % (str(int(day)), month2abrv[month], year)
            aliasDDMMAAAAhyphen = "%s-%s-%s" % (str(int(day)), month, year)
            
            aliasDDMMAAAAslash00 = "%s/%s/%s" % ("%02d" % (int(day)), "%02d" % (int(month2number[month])), year)
            aliasDDMMAAAAslash0 = "%s/%s/%s" % (str(int(day)), str(int(month2number[month])), year)
            aliasDDMMAAAAslashabrv = "%s/%s/%s" % (str(int(day)), month2abrv[month], year)
            aliasDDMMAAAAslash = "%s/%s/%s" % (str(int(day)), month, year)
            
            aliasDDMMAAAAnode00 = "%s %s %s" % ("%02d" % (int(day)), month, year)
            aliasDDMMAAAAnode0 = "%s %s %s" % (str(int(day)), month, year)
            
            aliasDDMMAAAAnodeabrv00 = "%s %s %s" % ("%02d" % (int(day)), month2abrv[month], year)
            aliasDDMMAAAAnodeabrv0 = "%s %s %s" % (str(int(day)), month2abrv[month], year)
            
            aliasescandidates = list(set([aliasDDMMAAAAhyphen00, aliasDDMMAAAAhyphen0, aliasDDMMAAAAhyphenabrv, aliasDDMMAAAAhyphen, aliasDDMMAAAAslash00, aliasDDMMAAAAslash0, aliasDDMMAAAAslashabrv, aliasDDMMAAAAslash, aliasDDMMAAAAnode00, aliasDDMMAAAAnode0, aliasDDMMAAAAnodeabrv00, aliasDDMMAAAAnodeabrv0]))
            
            #aliases
            aliases = item.aliases
            for aliascandidate in aliasescandidates:
                addedsomething = False
                if not "es" in aliases:
                    aliases["es"] = [aliascandidate]
                    addedsomething = True
                else:
                    if not aliascandidate in aliases["es"] and not aliascandidate in [x.lower() for x in aliases["es"]]:
                        aliases["es"].append(aliascandidate)
                        addedsomething = True
                if addedsomething:
                    aliasessort = aliases["es"]
                    aliasessort.sort()
                    aliases["es"] = aliasessort
                    print(aliases["es"])
                    data = { 'aliases': aliases }
                    summary = "BOT - Adding 1 aliases (es): %s" % (aliascandidate)
                    print(summary.encode('utf-8'))
                    try:
                        item.editEntity(data, summary=summary)
                    except:
                        print('Error while saving')
                        continue
            sys.exit()

if __name__ == '__main__':
    main()
