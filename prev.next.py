#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 emijrp <emijrp@gmail.com>
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

import pwb
import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

def addImportedFrom(repo='', claim='', lang=''):
    langs = { 'en': 'Q328', 'fr': 'Q8447', 'de': 'Q48183', }
    if repo and claim and lang and lang in langs.keys():
        importedfrom = pywikibot.Claim(repo, 'P143') #imported from
        importedwp = pywikibot.ItemPage(repo, langs[lang])
        importedfrom.setTarget(importedwp)
        claim.addSource(importedfrom, summary='BOT - Adding 1 reference: [[Property:P143]]: [[Q328]]')

def addPrevClaim(repo='', item='', itemprev='', lang=''):
    prop = 'P155'
    if repo and item and item and itemprev and lang:
        print("Adding %s (prev): %s" % (prop, itemprev.title()))
        claim = pywikibot.Claim(repo, prop)
        target = pywikibot.ItemPage(repo, itemprev.title())
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim, lang=lang)

def addNextClaim(repo='', item='', itemnext='', lang=''):
    prop = 'P156'
    if repo and item and item and itemnext and lang:
        print("Adding %s (next): %s" % (prop, itemnext.title()))
        claim = pywikibot.Claim(repo, prop)
        target = pywikibot.ItemPage(repo, itemnext.title())
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim, lang=lang)

def core(repo='', item='', page='', lang='', wikisite='', titleprev='', titlenext=''):
    if repo and item and page and lang and wikisite and titleprev and titlenext:
        print('Page: %s (%s)' % (page.title().encode('utf-8'), item.title()))
        item.get()
        if titleprev:
            if not 'P155' in item.claims:
                pageprev = pywikibot.Page(wikisite, titleprev)
                if not pageprev.exists() or pageprev.isRedirectPage():
                    print("Pageprev doesnt exist or is redirect: %s" % (pageprev.title().encode('utf-8')))
                else:
                    itemprev = ''
                    try:
                        itemprev = pywikibot.ItemPage.fromPage(pageprev)
                    except:
                        print("No wikidata item for pageprev")
                    if itemprev:
                        print('Pageprev: %s (%s)' % (pageprev.title().encode('utf-8'), itemprev.title()))
                        addPrevClaim(repo=repo, item=item, itemprev=itemprev, lang=lang)
            else:
                print("Item has P155 (prev)")
        
        if titlenext:
            if not 'P156' in item.claims:
                pagenext = pywikibot.Page(wikisite, titlenext)
                if not pagenext.exists() or pagenext.isRedirectPage():
                    print("Pagenext doesnt exist or is redirect: %s" % (pagenext.title().encode('utf-8')))
                else:
                    itemnext = ''
                    try:
                        itemnext = pywikibot.ItemPage.fromPage(pagenext)
                    except:
                        print("No wikidata item for pagenext")
                    if itemnext:
                        print('Pagenext: %s (%s)' % (pagenext.title().encode('utf-8'), itemnext.title()))
                        addNextClaim(repo=repo, item=item, itemnext=itemnext, lang=lang)
            else:
                print("Item has P156 (next)")
            
def main():
    lang = 'en'
    wikisite = pywikibot.Site(lang, 'wikipedia')
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    #https://en.wikipedia.org/wiki/Category:YearParamUsageCheck_tracking_categories
    #https://en.wikipedia.org/wiki/Category:Year_by_category_%E2%80%94_used_with_year_parameter(s)_equals_year_in_page_title
    
    method = 'all'
    if len(sys.argv) > 1:
        method = sys.argv[1]
    
    if method == 'all' or method == 'method1':
        groups = [
            #['Category:%s births' % (i) for i in range(100, 2050)], 
            #['Category:%s deaths' % (i) for i in range(100, 2050)], 
            #['Category:%s establishments' % (i) for i in range(100, 2050)], 
            #['Category:%s disestablishments' % (i) for i in range(100, 2050)], 
            
            #['Category:%s books' % (i) for i in range(100, 2050)], 
            #['Category:%s comic debuts' % (i) for i in range(100, 2050)], 
            #['Category:%s compositions' % (i) for i in range(100, 2050)], 
            #['Category:%s documents' % (i) for i in range(100, 2050)], 
            #['Category:%s films' % (i) for i in range(1850, 2050)], 
            #['Category:%s musicals' % (i) for i in range(100, 2050)], 
            #['Category:%s operas' % (i) for i in range(100, 2050)], 
            #['Category:%s paintings' % (i) for i in range(100, 2050)], 
            #['Category:%s plays' % (i) for i in range(100, 2050)], 
            #['Category:%s poems' % (i) for i in range(100, 2050)], 
            #['Category:%s sculptures‎' % (i) for i in range(100, 2050)], 
            #['Category:%s short stories' % (i) for i in range(100, 2050)], 
            #['Category:%s songs' % (i) for i in range(100, 2050)], 
            #['Category:%s treaties' % (i) for i in range(100, 2050)], 
            #['Category:%s works' % (i) for i in range(100, 2050)], 
            
            #['%s in film' % (i) for i in range(1850, 2050)], 
        ]
        for titles in groups:
            for c in range(0, len(titles)):
                title = titles[c]
                titleprev = c > 0 and titles[c-1] or ''
                titlenext = c < len(titles)-1 and titles[c+1] or ''
                print('\n==', title.encode('utf-8'), '==')
                page = pywikibot.Page(wikisite, title)
                if not page.exists() or page.isRedirectPage():
                    print("Page doesnt exist or is redirect: %s" % (page.title().encode('utf-8')))
                    continue
                item = pywikibot.ItemPage.fromPage(page)
                if item:
                    core(repo=repo, item=item, page=page, lang=lang, wikisite=wikisite, titleprev=titleprev, titlenext=titlenext)
                else:
                    print("Page doest have item")
    
    if method == 'all' or method == 'method2':
        #cat = pywikibot.Category(wikisite, 'Category:Year by category — used with year parameter(s) equals year in page title')
        cat = pywikibot.Category(wikisite, 'Category:YearParamUsageCheck tracking categories')
        #gen = pagegenerators.SubCategoriesPageGenerator(cat)
        gen = pagegenerators.SubCategoriesPageGenerator(cat, recurse=4)
        for page in gen:
            print('\n==', page.title().encode('utf-8'), '==')
            year = ''
            titleprev = ''
            titlenext = ''
            if re.findall(r'(?m)^Category:(\d{4}) [^\d]+$', page.title()):
                year = int(re.findall(r'(?m)^Category:(\d{4}) [^\d]+$', page.title())[0])
                titleprev = re.sub(r'(?m)^(Category):%s ([^\d]+)$' % (year), r'\1:%s \2' % (year-1), page.title())
                titlenext = re.sub(r'(?m)^(Category):%s ([^\d]+)$' % (year), r'\1:%s \2' % (year+1), page.title())
            elif re.findall(r'(?m)^Category:[^\d]+ in (\d{4})$', page.title()):
                year = int(re.findall(r'(?m)^Category:[^\d]+ in (\d{4})$', page.title())[0])
                titleprev = re.sub(r'(?m)^(Category):([^\d]+ in) %s$' % (year), r'\1:\2 %s' % (year-1), page.title())
                titlenext = re.sub(r'(?m)^(Category):([^\d]+ in) %s$' % (year), r'\1:\2 %s' % (year+1), page.title())
            else:
                print("Not a yearly category")
                continue
            if not year or len(str(year)) != 4:
                print("Couldnt parse correct year from page name")
                continue
            print(year)
            item = ''
            try:
                item = pywikibot.ItemPage.fromPage(page)
            except:
                print("No wikidata item for this page")
                continue
            if item:
                if titleprev and titlenext:
                    core(repo=repo, item=item, page=page, lang=lang, wikisite=wikisite, titleprev=titleprev, titlenext=titlenext)
                else:
                    print("Not titleprev or titlenext")
            else:
                print("Page doest have item")
    
    if method == 'all' or method == 'method3':
        for year in range(1000, 2050):
            prefix = '%s in ' % (year)
            prefixprev = '%s in ' % (year-1)
            prefixnext = '%s in ' % (year+1)
            gen = pagegenerators.PrefixingPageGenerator(prefix, namespace=0, includeredirects=False, site=wikisite, total=None, content=False)
            for page in gen:
                if not page.title().startswith(prefix):
                    break
                if ' in science' in page.title():
                    continue
                print('\n==', page.title().encode('utf-8'), '==')
                titleprev = ''
                titlenext = ''
                if re.findall(r'(?m)^%s([^\d]+)$' % (prefix), page.title()):
                    titleprev = re.sub(r'(?m)^%s([^\d]+)$' % (prefix), r'%s\1' % (prefixprev), page.title())
                    titlenext = re.sub(r'(?m)^%s([^\d]+)$' % (prefix), r'%s\1' % (prefixnext), page.title())
                else:
                    print("Not a yearly page")
                    continue
                item = ''
                try:
                    item = pywikibot.ItemPage.fromPage(page)
                except:
                    print("No wikidata item for this page")
                    continue
                if item:
                    if titleprev and titlenext:
                        core(repo=repo, item=item, page=page, lang=lang, wikisite=wikisite, titleprev=titleprev, titlenext=titlenext)
                    else:
                        print("Not titleprev or titlenext")
                else:
                    print("Page doest have item")

if __name__ == "__main__":
    main()
