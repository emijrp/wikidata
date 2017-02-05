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
from quickstatements import *

def main():
    translations = {
        #'an': '', #no esta claro si es apellido o apelliu?
        'ast': 'apellíu', 
    }
    """
        'ca': 'cognom', 
        'de': 'Familienname', 
        'de-at': 'Familienname', 
        'de-ch': 'Familienname', 
        'es': 'apellido', 
        'fr': 'nom de famille', 
        'gl': 'apelido', 
        'it': 'cognome', 
        'pt': 'sobrenome', 
        'pt-br': 'nome de família',
    }"""
    for lang in translations.keys():
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ101352%20.%0A%20%20%09OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+lang+'%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%7D'
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            print('%s\tD%s\t"%s"' % (q, lang, translations[lang]))
    
if __name__ == "__main__":
    main()
