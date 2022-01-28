#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2022 emijrp <emijrp@gmail.com>
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

import pwb
import pywikibot
from wikidatafun import *

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    pasleim = pywikibot.Page(site, "User:Mr. Ibrahem/Language statistics for items")
    pasleimtext = pasleim.text
    langs = re.findall(r"(?im){{#language:([a-z\-]+)\|en}}", pasleimtext)
    print(langs, len(langs))
    
    qlabels = {
        "Q33836537": "😂", 
    }
    qaliases = {
        #"Q2": ["🗺", "♁", "🜨", "🌍", "🌏", "🌎"], 
        "Q2": ["🗺", "♁", "🜨", "🌍", "🌏", "🌎"], 
    }
    for q, label in qlabels.items():
        nomorelangs = False
        for i in range(100):
            if nomorelangs:
                break
            item = pywikibot.ItemPage(repo, q)
            try: #to detect Redirect because .isRedirectPage fails
                item.get()
            except:
                print('Error while .get()')
                continue
            
            addedlangs = []
            itemlabels = item.labels
            for lang in langs:
                if not lang in itemlabels:
                    itemlabels[lang] = label
                    if not lang in addedlangs:
                        addedlangs.append(lang)
                if len(addedlangs) >= 25:
                    break
            if len(addedlangs) == 0:
                nomorelangs = True
            else:
                addedlangs.sort()
                data = { 'labels': itemlabels }
                summary = 'BOT - Adding labels (%d languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                print(q, summary)
                try:
                    item.editEntity(data, summary=summary)
                    #break
                except:
                    print('Error while saving')
                    continue
    
    for q, aliases in qaliases.items():
        nomorelangs = False
        for i in range(100):
            if nomorelangs:
                break
            item = pywikibot.ItemPage(repo, q)
            try: #to detect Redirect because .isRedirectPage fails
                item.get()
            except:
                print('Error while .get()')
                continue
            
            addedlangs = []
            itemaliases = item.aliases
            for lang in langs:
                if not lang in itemaliases:
                    itemaliases[lang] = aliases
                    if not lang in addedlangs:
                        addedlangs.append(lang)
                else:
                    for alias in aliases:
                        if not alias in itemaliases[lang]:
                            itemaliases[lang].append(alias)
                            if not lang in addedlangs:
                                addedlangs.append(lang)
                if len(addedlangs) >= 25:
                    break
            if len(addedlangs) == 0:
                nomorelangs = True
            else:
                addedlangs.sort()
                data = { 'aliases': itemaliases }
                summary = 'BOT - Adding aliases (%d languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                print(q, summary)
                try:
                    item.editEntity(data, summary=summary)
                    #break
                except:
                    print('Error while saving')
                    continue

if __name__ == "__main__":
    main()
