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
import urllib

import pywikibot
from pywikibot import pagegenerators

from wikidatafun import *

def addHumanClaim(repo='', item=''):
    if repo and item:
        claim = pywikibot.Claim(repo, 'P31')
        target = pywikibot.ItemPage(repo, 'Q5')
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')

def addGenderClaim(repo='', item='', gender=''):
    gender2q = { 'female': 'Q6581072', 'male': 'Q6581097' }
    if repo and item and gender and gender in gender2q.keys():
        claim = pywikibot.Claim(repo, 'P21')
        target = pywikibot.ItemPage(repo, gender2q[gender])
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')

def calculateGender(page=''):
    femalepoints = len(re.findall(r'(?i)\b(she|her|hers|Category:[^\]]+ female|Category:[^\]]+ women)\b', page.text))
    malepoints = len(re.findall(r'(?i)\b(he|his|him|Category:[^\]]+ male|Category:[^\]]+ men)\b', page.text))
    if femalepoints > malepoints*3:
        return 'female'
    elif malepoints > femalepoints*3:
        return 'male'
    return ''

def pageCategories(page=''):
    return len(re.findall(r'(?i)\[\[\s*Category\s*\:', page.text))

def pageReferences(page=''):
    return len(re.findall(r'(?i)</ref>', page.text))

def pageIsBiography(page=''):
    if re.search(r'(?im)(\'{3} \(born \d|Category:\d{4} (births|deaths)|Category:Living people|birth_date *=|birth_place *=|death_date *=|death_place *=|== *Biography *==|Category:People from)', page.text):
        return True
    return False

def pageIsRubbish(page=''):
    if re.search(r'\{\{ *db|AfD|\{\{ *[Aa]rticle for deletion|\{\{ *[Nn]otability', page.text):
        return True
    return False

def main():
    lang = 'en'
    wikisite = pywikibot.Site(lang, 'wikipedia')
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    repo = wdsite.data_repository()
    gen = pagegenerators.NewpagesPageGenerator(site=wikisite, namespaces=[0], total=50000)
    pre = pagegenerators.PreloadingGenerator(gen, groupsize=50)
    for page in pre:
        if not pageIsBiography(page=page):
            continue
        gender = calculateGender(page=page)
        item = ''
        try:
            item = pywikibot.ItemPage.fromPage(page)
        except:
            pass
        if item:
            try:
                item.get()
            except:
                print('Error while retrieving item, skiping...')
                continue
            p31 = ''
            p21 = ''
            claims = item.claims
            if claims:
                if 'P31' in item.claims:
                    p31 = item.claims['P31'][0].getTarget()
                if 'P21' in item.claims:
                    p21 = item.claims['P21'][0].getTarget()
            print(page.title(), item, gender, p31, p21)
            if not p31:
                addHumanClaim(repo=repo, item=item)
            if not p21:
                addGenderClaim(repo=repo, item=item, gender=gender)
        else:
            #search for a valid item, otherwise create
            if pageIsRubbish(page=page) or \
               pageCategories(page=page) < 3 or \
               pageReferences(page=page) < 3 or \
               len(list(page.getReferences(namespaces=[0]))) < 3:
                continue
            
            print('\n')
            print(page.title(), 'need item', gender)
            wtitle = page.title()
            wtitle_ = wtitle.split('(')[0].strip()
            searchitemurl = 'https://www.wikidata.org/wiki/Special:ItemDisambiguation?language=&label=%s' % (urllib.parse.quote(wtitle_))
            raw = getURL(searchitemurl)
            
            if 'Sorry, no item with that label was found' in raw:
                print('No useful item found. Creating a new one...')
                #create item
                newitemlabels = { 'en': wtitle_ }
                newitem = pywikibot.ItemPage(repo)
                newitem.editLabels(labels=newitemlabels, summary="BOT - Creating item for [[:%s:%s|%s]] (%s)" % (lang, wtitle, wtitle, lang))
                newitem.get()
                addHumanClaim(repo=repo, item=newitem)
                addGenderClaim(repo=repo, item=newitem, gender=gender)
                newitem.setSitelink(page, summary='BOT - Adding 1 sitelink: [[:%s:%s|%s]] (%s)' % (lang, page.title(), page.title(), lang))
            else:
                print(searchitemurl)
                #check birthdate and if it matches add interwiki 
                m = re.findall(r'<li class="wikibase-disambiguation"><a title="(Q\d+)"', raw)
                if len(m) > 3:
                    continue
                for itemfoundq in m:
                    itemfound = pywikibot.ItemPage(repo, itemfoundq)
                    itemfound.get()
                    if ('%swiki' % (lang)) in itemfound.sitelinks:
                        continue
                    if 'P569' in itemfound.claims:
                        birthyear = itemfound.claims['P569'][0].getTarget().year
                        if birthyear and re.search(r'[[Category:%s births]]' % (birthyear), page.text):
                            print('%s birthyear found in item. Category:%s births found in page' % (birthyear, birthyear))
                            print('Adding sitelink %s:%s' % (lang, page.title()))
                            itemfound.setSitelink(page, summary='BOT - Adding 1 sitelink: [[:%s:%s|%s]] (%s)' % (lang, page.title(), page.title(), lang))
                            addGenderClaim(repo=repo, item=newitem, gender=gender)
                            break
    
if __name__ == "__main__":
    main()
