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

import pwb
import pywikibot
from wikidatafun import *

def main():
    enwpsite = pywikibot.Site('en', 'wikipedia')
    site = pywikibot.Site('wikidata', 'wikidata')
    ahk = pywikibot.Page(site, 'User:Emijrp/All Human Knowledge')
    ahktext = ahk.text
    ahknewtext = ahktext
    
    """
    #[[links]] -> {{Q|123}}
    m = re.findall(r'(?im)(\[\[([^\[\]\:\|]+?)\]\]([A-Za-z]*))', ahknewtext)
    for i in m:
        enwppage = pywikibot.Page(enwpsite, i[1])
        try:
            if enwppage.isRedirectPage():
                enwppage = enwppage.getRedirectTarget()
            q = pywikibot.ItemPage.fromPage(enwppage)
            print(i, q.title())
            ahknewtext = ahknewtext.replace(i[0], "{{Q|%s}}" % q.title(), 1)
        except:
            continue
    """
    #[[link|links]] -> [[Q123|links]]
    m = re.findall(r'(?im)(\[\[([^\[\]\:]+?)\|([^\[\]\:]+?)\]\]([A-Za-z]*))', ahknewtext)
    for i in m:
        enwppage = pywikibot.Page(enwpsite, i[1])
        try:
            if enwppage.isRedirectPage():
                enwppage = enwppage.getRedirectTarget()
            q = pywikibot.ItemPage.fromPage(enwppage)
            print(i, q.title())
            ahknewtext = ahknewtext.replace(i[0], "[[%s|%s%s]]" % (q.title(), i[2], i[3]), 1)
        except:
            continue
    
    pywikibot.showDiff(ahktext, ahknewtext)
    ahk.text = ahknewtext
    ahk.save("BOT - Switching links to {{Q}}")

if __name__ == '__main__':
    main()
