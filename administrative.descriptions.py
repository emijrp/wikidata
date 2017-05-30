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

import pwb
import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    raw = ''
    with open('administrative.descriptions.i18n.txt', 'r') as f:
        raw = f.read()
    raw2 = []
    for l in raw.splitlines():
        l = l.strip()
        if not l.startswith('#'):
            raw2.append(l)
    raw = '\n'.join(raw2)
    raw = re.sub(r'\,\s*\}', '}', raw)
    dic = json.loads(raw)
    
    #poner el having 1 para evitar describir cosas con mas de un p31
    for admq, translations in dic.items():
        print(admq, translations)
        for lang, translation in translations.items():
            print(admq, lang, translation)
            #https://query.wikidata.org/#SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ753113%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstanceof.%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING%28COUNT%28%3Finstanceof%29%20%3D%201%29
            
            #los admq tienen unos label y luego la gente ha puesto otros label en los elementos...
    
if __name__ == "__main__":
    main()
