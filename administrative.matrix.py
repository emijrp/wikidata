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

import pwb
import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20DISTINCT%20%3Fitem%20%3FcountryLabel%20%3FitemLabel%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP279%20wd%3AQ15916867.%0A%20%20%20%20%3Fitem%20wdt%3AP17%20%3Fcountry.%0A%20%20%20%20%3Fitem%20rdfs%3Alabel%20%3FitemLabel.%0A%20%20%20%20FILTER(STRSTARTS(%3FitemLabel%2C%20%27administrative%20territorial%20entity%27)).%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D%0AORDER%20BY%20%3FitemLabel'
    url = '%s&format=json' % (url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)
    print("{")
    for result in json1['results']['bindings']:
        q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
        countryLabel = result['countryLabel']['value']
        #print(q, countryLabel)
        
        url2 = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20DISTINCT%20%3Fitem%20%3FitemLabel%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP279%20wd%3A'+q+'.%0A%20%20%20%20%3Fitem%20rdfs%3Alabel%20%3FitemLabel.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D%0AORDER%20BY%20%3FitemLabel'
        url2 = '%s&format=json' % (url2)
        sparql2 = getURL(url=url2)
        json2 = loadSPARQL(sparql=sparql2)
        for result2 in json2['results']['bindings']:
            q2 = 'item' in result2 and result2['item']['value'].split('/entity/')[1] or ''
            admLabel = result2['itemLabel']['value']
            #print(q2, admLabel)
            item = pywikibot.ItemPage(repo, q2)
            item.get()
            #print(item.labels)
            translist = ['    #"%s": "%s",' % (x, y) for x, y in item.labels.items()]
            translist.sort()
            output = '"%s": {\n%s\n},' % (q2, '\n'.join(translist))
            print(output)
    print("}")
    
if __name__ == "__main__":
    main()
