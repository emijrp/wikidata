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

import json
import re
import urllib
import urllib.request
import urllib.parse

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        sleep = 10 # seconds
        maxsleep = 100
        while sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            try:
                raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
            except:
                pass
            sleep = sleep * 2
    return raw

def main():
    gender = { 'Q6581097': 'male', 'Q6581072': 'female', 'male': 'Q6581097', 'female': 'Q6581072' }
    statements = [
        { 'p31': 'Q5', 'p21': 'Q6581097', 'p27': 'Q183', 'p106': 'Q36180', 'desc@en': 'German writer' }, #male German writers
        { 'p31': 'Q5', 'p21': 'Q6581072', 'p27': 'Q183', 'p106': 'Q36180', 'desc@en': 'German writer' }, #female German writers
        { 'p31': 'Q5', 'p21': 'Q6581097', 'p27': 'Q29', 'p106': 'Q36180', 'desc@en': 'Spanish writer' }, #male Spanish writers
        { 'p31': 'Q5', 'p21': 'Q6581072', 'p27': 'Q29', 'p106': 'Q36180', 'desc@en': 'Spanish writer' }, #female Spanish writers
    ]
    translations = {
        'Spanish writer': {
            'male': {
                'an': 'escritor espanyol', 
                'ast': 'escritor español', 
                'ca': 'escriptor espanyol', 
                'es': 'escritor español', 
                'gl': 'escritor español', 
                'oc': 'escrivan espanhòl', 
            }, 
            'female': {
                'an': 'escritora espanyola', 
                'ast': 'escritora española', 
                'ca': 'escriptora espanyola', 
                'es': 'escritora española', 
                'gl': 'escritora española', 
                'oc': 'escrivana espanhòla', 
            }, 
        }, 
        'German writer': {
            'male': {
                'an': 'escritor alemán', 
                'ast': 'escritor alemán', 
                'ca': 'escriptor alemany', 
                'es': 'escritor alemán', 
                'gl': 'escritor alemán', 
                'oc': 'escrivan alemand', 
            }, 
            'female': {
                'an': 'escritora alemana', 
                'ast': 'escritora alemana', 
                'ca': 'escriptora alemanya', 
                'es': 'escritora alemana', 
                'gl': 'escritora alemá', 
                'oc': 'escrivana alemanda', 
            }, 
        }, 
    }
    for statement in statements:
        for lang in translations[statement['desc@en']][gender[statement['p21']]].keys():
            url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20DISTINCT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3A'+statement['p31']+'%20.%20%23instance%20of%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3A'+statement['p21']+'%20.%20%23gender%0A%20%20%20%20%3Fitem%20wdt%3AP106%20wd%3A'+statement['p106']+'%20.%20%23occupation%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3A'+statement['p27']+'%20.%20%23country%20of%20citizenship%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22'+re.sub(' ', '%20', statement['desc@en'])+'%22%40en.%0A%09OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+lang+'%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22es%22%7D%0A%7D%0A'
            url = '%s&format=json' % (url)
            sparql = getURL(url=url)
            
            if sparql:
                try:
                    json1 = json.loads(sparql)
                except:
                    print('Error downloading SPARQL? Malformatted JSON? Skiping\n')
            else:
                print('Server return empty file')
            
            for result in json1['results']['bindings']:
                q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                translation = translations[statement['desc@en']][gender[statement['p21']]][lang]
                print('%s\tD%s\t"%s"' % (q, lang, translation))
    
if __name__ == "__main__":
    main()
