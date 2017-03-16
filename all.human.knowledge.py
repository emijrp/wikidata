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

def getp31count(p31=''):
    if p31 and p31.startswith('Q'):
        try:
            url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%20%23%20%3FitemLabel%0AWHERE%20{%0A%20%20%3Fitem%20wdt%3AP31%2Fwdt%3AP279*%20wd%3A'+p31+'.%0A%20%20SERVICE%20wikibase%3Alabel%20{%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20}%0A}%0A'
            url = '%s&format=json' % (url)
            sparql = getURL(url=url)
            json1 = loadSPARQL(sparql=sparql)
            return json1['results']['bindings'][0]['count']['value']
        except:
            return ''
    return ''

def main():
    site = pywikibot.Site('en', 'wikipedia')
    ahk = pywikibot.Page(site, 'User:Emijrp/All human knowledge')
    ahktext = ahk.text
    ahknewtext = ahk.text
    
    #update inline stuff
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    wpenstatsurl = 'https://en.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json'
    jsonwpen = json.loads(getURL(url=wpenstatsurl))
    wpenarticles = jsonwpen['query']['statistics']['articles']
    wdstatsurl = 'https://www.wikidata.org/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json'
    jsonwd = json.loads(getURL(url=wdstatsurl))
    wdarticles = jsonwd['query']['statistics']['articles']
    wpenwdstats = "<!-- wpenwdstats -->As of {{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}, [[English Wikipedia]] has {{formatnum:%s}} articles<ref>{{cite web | url=https://en.wikipedia.org/wiki/Special:Statistics | title=Special:Statistics | publisher=English Wikipedia | date=%s | accessdate=%s | quote=Content pages: {{formatnum:%s}}}}</ref> and [[Wikidata]] includes {{formatnum:%s}} items.<ref>{{cite web|url=https://www.wikidata.org/wiki/Special:Statistics | title=Special:Statistics | publisher=Wikidata | date=%s | accessdate=%s | quote=Content pages: {{formatnum:%s}}}}</ref><!-- /wpenwdstats -->" % (wpenarticles, today, today, wpenarticles, wdarticles, today, today, wdarticles)
    ahknewtext = re.sub(r'<!-- wpenwdstats -->.*?<!-- /wpenwdstats -->', wpenwdstats, ahknewtext)
    
    #update tables
    lines = ahknewtext.splitlines()
    newlines = []
    newtotalwikidata = 0
    newtotalestimate = 0
    row_r = r'({{User:Emijrp/AHKrow\|P31=([^\|\}]*?)\|wikidata=(\d*?)\|estimate=(\d*?)}})'
    rowtotal_r = r'({{User:Emijrp/AHKrowtotal\|wikidata=(\d*?)\|estimate=(\d*?)}})'
    for line in lines:
        newline = line
        
        #update row
        m = re.findall(row_r, newline)
        for i in m:
            row, p31, wikidata, estimate = i
            newwikidata = getp31count(p31=p31)
            newrow = row.replace('wikidata=%s|' % (wikidata), 'wikidata=%s|' % (newwikidata))
            newline = newline.replace(row, newrow)
            newtotalwikidata += newwikidata and int(newwikidata) or 0
            newtotalestimate += estimate and int(estimate) or (newwikidata and int(newwikidata) or 0)
        
        #update row total
        m = re.findall(rowtotal_r, newline)
        for i in m:
            totalrow, totalwikidata, totalestimate = i
            newtotalrow = totalrow
            newtotalrow = newtotalrow.replace('wikidata=%s|' % (totalwikidata), 'wikidata=%s|' % (newtotalwikidata))
            newtotalrow = newtotalrow.replace('estimate=%s}}' % (totalestimate), 'estimate=%s}}' % (newtotalestimate))
            newline = newline.replace(totalrow, newtotalrow)
            #reset
            newtotalwikidata = 0
            newtotalestimate = 0
        
        newlines.append(newline)
    ahknewtext = '\n'.join(newlines)
    
    if ahknewtext and ahktext != ahknewtext:
        #pywikibot.showDiff(ahktext, ahknewtext)
        ahk.text = ahknewtext
        ahk.save('BOT - Updating The Catalogue of Catalogues')
    
if __name__ == '__main__':
    main()
