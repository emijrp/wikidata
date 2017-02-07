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
import time

import pwb
import pywikibot
from quickstatements import *

def getp31count(p31=''):
    if p31 and p31.startswith('Q'):
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%20%23%20%3FitemLabel%0AWHERE%20{%0A%20%20%3Fitem%20wdt%3AP31%2Fwdt%3AP279*%20wd%3A'+p31+'.%0A%20%20SERVICE%20wikibase%3Alabel%20{%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20}%0A}%0A'
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        return json1['results']['bindings'][0]['count']['value']
    return ''

def main():
    site = pywikibot.Site('en', 'wikipedia')
    ahk = pywikibot.Page(site, 'User:Emijrp/All human knowledge')
    ahktext = ahk.text
    ahknewtext = ahk.text
    
    #update rows
    m = re.findall(r'({{User:Emijrp/AHKrow\|P31=(Q\d+)\|wikidata=(\d*)\|estimate=(\d*)}})', ahknewtext)
    for i in m:
        row = i[0]
        p31 = i[1]
        wikidata = i[2]
        estimate = i[3]
        count = getp31count(p31=p31)
        time.sleep(1)
        newrow = row.replace('wikidata=%s|' % (wikidata), 'wikidata=%s|' % (count))
        ahknewtext = ahknewtext.replace(row, newrow)
        print(row)
        print('Old value:', wikidata, 'New value:', count)
    
    #update totals
    sections = ahknewtext.split('== ')
    newsections = [sections[0]]
    for section in sections[1:]:
        title = section.split(' ==')[0]
        newsection = section
        m = re.findall(r'({{User:Emijrp/AHKrow\|[^\|]+?\|wikidata=(\d*)\|estimate=(\d*)}})', newsection)
        newwikidata = 0
        newestimate = 0
        for i in m:
            newwikidata += i[1] and int(i[1]) or 0
            newestimate += i[2] and int(i[2]) or 0
        try:
            rowtotal, wikidata, estimate = re.findall(r'({{User:Emijrp/AHKrowtotal\|wikidata=(\d*)\|estimate=(\d*)}})', newsection)[0]
        except:
            newsections.append(newsection)
            continue
        newrowtotal = rowtotal
        newrowtotal = newrowtotal.replace('wikidata=%s|' % (wikidata), 'wikidata=%s|' % (newwikidata))
        newrowtotal = newrowtotal.replace('estimate=%s}}' % (estimate), 'estimate=%s}}' % (newestimate))
        newsection = newsection.replace(rowtotal, newrowtotal)
        newsections.append(newsection)
    ahknewtext = '== '.join(newsections)
        
    if ahknewtext and ahktext != ahknewtext:
        pywikibot.showDiff(ahktext, ahknewtext)
        ahk.text = ahknewtext
        ahk.save('BOT - Updating')
    
if __name__ == '__main__':
    main()
