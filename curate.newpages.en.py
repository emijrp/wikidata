#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2019 emijrp <emijrp@gmail.com>
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
import sys
import urllib

import pywikibot
from pywikibot import pagegenerators

from wikidatafun import *

def addImportedFrom(repo='', claim=''):
    importedfrom = pywikibot.Claim(repo, 'P143') #imported from
    importedwp = pywikibot.ItemPage(repo, 'Q328') #enwp
    importedfrom.setTarget(importedwp)
    claim.addSource(importedfrom, summary='BOT - Adding 1 reference: [[Property:P143]]: [[Q328]]')

def addHumanClaim(repo='', item=''):
    if repo and item:
        claim = pywikibot.Claim(repo, 'P31')
        target = pywikibot.ItemPage(repo, 'Q5')
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim)

def addGenderClaim(repo='', item='', gender=''):
    gender2q = { 'female': 'Q6581072', 'male': 'Q6581097' }
    if repo and item and gender and gender in gender2q.keys():
        claim = pywikibot.Claim(repo, 'P21')
        target = pywikibot.ItemPage(repo, gender2q[gender])
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim)

def addBirthDateClaim(repo='', item='', date=''):
    return addDateClaim(repo=repo, item=item, claim='P569', date=date)

def addDeathDateClaim(repo='', item='', date=''):
    return addDateClaim(repo=repo, item=item, claim='P570', date=date)

def addDateClaim(repo='', item='', claim='', date=''):
    if repo and item and claim and date:
        claim = pywikibot.Claim(repo, claim)
        if len(date.split('-')) == 3:
            claim.setTarget(pywikibot.WbTime(year=date.split('-')[0], month=date.split('-')[1], day=date.split('-')[2]))
        elif len(date.split('-')) == 2:
            claim.setTarget(pywikibot.WbTime(year=date.split('-')[0], month=date.split('-')[1]))
        elif len(date.split('-')) == 1:
            claim.setTarget(pywikibot.WbTime(year=date.split('-')[0]))
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim)

def addOccupationsClaim(repo='', item='', occupations=[]):
    if repo and item and occupations:
        for occupation in occupations:
            claim = pywikibot.Claim(repo, 'P106')
            target = pywikibot.ItemPage(repo, occupation.title())
            claim.setTarget(target)
            item.addClaim(claim, summary='BOT - Adding 1 claim')
            addImportedFrom(repo=repo, claim=claim)

def authorIsNewbie(page=''):
    if page:
        hist = page.getVersionHistory(reverse=True, total=1)
        if hist:
            editcount = getUserEditCount(user=hist[0].user, site='en.wikipedia.org')
            if editcount >= 200:
                return False
    return True

def calculateGender(page=''):
    femalepoints = len(re.findall(r'(?i)\b(she|her|hers)\b', page.text))
    malepoints = len(re.findall(r'(?i)\b(he|his|him)\b', page.text))
    if re.search(r'(?i)\b(Category *:[^\]]*?female|Category *:[^\]]*?women|Category *:[^\]]*?actresses)\b', page.text) or \
       (len(page.text) <= 2000 and femalepoints >= 1 and malepoints == 0) or \
       (femalepoints >= 2 and femalepoints > malepoints*3):
        return 'female'
    elif re.search(r'(?i)\b(Category *:[^\]]*? male|Category *:[^\]]*? men)\b', page.text) or \
       (len(page.text) <= 2000 and malepoints >= 1 and femalepoints == 0) or \
       (malepoints >= 2 and malepoints > femalepoints*3):
        return 'male'
    return ''

def calculateBirthDate(page=''):
    m = re.findall(r'Category:(\d+) births', page.text)
    if m:
        return m[0]
    return ''

def calculateDeathDate(page=''):
    m = re.findall(r'Category:(\d+) deaths', page.text)
    if m:
        return m[0]
    return ''

def calculateOccupations(site='', page=''):
    ignoreoccupations = [
        'Q2066131', #sportpeople, too general
    ]
    occupations = []
    cats = re.findall(r'(?i)\[\[\s*Category\s*\:([^\[\]\|]+?)[\]\|]', page.text)
    for cat in cats:
        cat = cat.strip()
        catpage = pywikibot.Page(site, 'Category:%s' % (cat))
        catitem = ''
        try:
            catitem = pywikibot.ItemPage.fromPage(catpage)
        except:
            continue
        if not catitem:
            continue
        catclaims = catitem.claims
        if catclaims:
            if 'P4224' in catitem.claims:
                for p4224 in catitem.claims['P4224']:
                    if p4224.getTarget().title() != 'Q5':
                        continue
                    if 'P106' in p4224.qualifiers:
                        qualifier = p4224.qualifiers['P106']
                        occ = qualifier[0].getTarget()
                        if not occ.title() in ignoreoccupations:
                            occupations.append(occ)
    occupations = list(set(occupations))
    return occupations

def pageCategories(page=''):
    return len(re.findall(r'(?i)\[\[\s*Category\s*\:', page.text))

def pageReferences(page=''):
    return len(re.findall(r'(?i)</ref>', page.text))

def pageIsBiography(page=''):
    if re.search('(?im)Category:\d+ animal (births|deaths)', page.text):
        return False
    elif not page.title().startswith('List'):
        if len(page.title().split(' ')) <= 5:
            if re.search(r'(?im)(\'{3} \(born \d|Category:\d+ (births|deaths)|Category:Living people|birth_date *=|birth_place *=|death_date *=|death_place *=|== *Biography *==|Category:People from)', page.text):
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
    total = 100
    if len(sys.argv) >= 2:
        total = int(sys.argv[1])
    gen = pagegenerators.NewpagesPageGenerator(site=wikisite, namespaces=[0], total=total)
    pre = pagegenerators.PreloadingGenerator(gen, groupsize=50)
    for page in pre:
        if page.isRedirectPage():
            continue
        if not pageIsBiography(page=page):
            continue
        print('\n==', page.title().encode('utf-8'), '==')
        gender = calculateGender(page=page)
        birthdate = calculateBirthDate(page=page)
        deathdate = calculateDeathDate(page=page)
        occupations = calculateOccupations(site=wikisite, page=page)
        item = ''
        try:
            item = pywikibot.ItemPage.fromPage(page)
        except:
            pass
        if item:
            print('Page has item')
            print('https://www.wikidata.org/wiki/%s' % (item.title()))
            try:
                item.get()
            except:
                print('Error while retrieving item, skiping...')
                continue
            p31 = '' #instanceof
            p21 = '' #gender
            p569 = '' #birthdate
            p570 = '' #deathdate
            p106 = '' #occupations
            claims = item.claims
            if claims:
                if 'P31' in item.claims:
                    p31 = item.claims['P31'][0].getTarget()
                if 'P21' in item.claims:
                    p21 = item.claims['P21'][0].getTarget()
                if 'P569' in item.claims:
                    p569 = item.claims['P569'][0].getTarget()
                if 'P570' in item.claims:
                    p570 = item.claims['P570'][0].getTarget()
                if 'P106' in item.claims:
                    p106 = item.claims['P106'][0].getTarget()
            print(page.title().encode('utf-8'), item, gender, p31, p21)
            if not p31:
                addHumanClaim(repo=repo, item=item)
            if not p21 and gender:
                addGenderClaim(repo=repo, item=item, gender=gender)
            if not p569 and birthdate:
                addBirthDateClaim(repo=repo, item=item, date=birthdate)
            if not p570 and deathdate:
                addDeathDateClaim(repo=repo, item=item, date=deathdate)
            if not p106 and occupations:
                addOccupationsClaim(repo=repo, item=item, occupations=occupations)
        else:
            print('Page without item')
            #search for a valid item, otherwise create
            if authorIsNewbie(page=page):
                if pageIsRubbish(page=page) or \
                   (not pageCategories(page=page)) or \
                   (not pageReferences(page=page)) or \
                   (not len(list(page.getReferences(namespaces=[0])))):
                    continue
            
            print(page.title().encode('utf-8'), 'need item', gender)
            wtitle = page.title()
            wtitle_ = wtitle.split('(')[0].strip()
            #searchitemurl = 'https://www.wikidata.org/wiki/Special:ItemDisambiguation?language=&label=%s' % (urllib.parse.quote(wtitle_))
            #Special:itemDisambiguation was disabled https://phabricator.wikimedia.org/T195756
            searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=en&format=xml' % (urllib.parse.quote(wtitle_))
            raw = getURL(searchitemurl)
            print(searchitemurl.encode('utf-8'))
            
            #if 'Sorry, no item with that label was found' in raw: #Special:itemDisambiguation
            if '<search />' in raw:
                print('No useful item found. Creating a new one...')
                #create item
                newitemlabels = { lang: wtitle_ }
                newitem = pywikibot.ItemPage(repo)
                newitem.editLabels(labels=newitemlabels, summary="BOT - Creating item for [[:%s:%s|%s]] (%s): %s %s" % (lang, wtitle, wtitle, lang, 'human', gender))
                newitem.get()
                addHumanClaim(repo=repo, item=newitem)
                addGenderClaim(repo=repo, item=newitem, gender=gender)
                addBirthDateClaim(repo=repo, item=newitem, date=birthdate)
                addDeathDateClaim(repo=repo, item=newitem, date=deathdate)
                addOccupationsClaim(repo=repo, item=newitem, occupations=occupations)
                newitem.setSitelink(page, summary='BOT - Adding 1 sitelink: [[:%s:%s|%s]] (%s)' % (lang, page.title(), page.title(), lang))
            else:
                #check birthdate and if it matches, then add data
                m = re.findall(r'id="(Q\d+)"', raw)
                if len(m) > 5:
                    continue
                for itemfoundq in m:
                    itemfound = pywikibot.ItemPage(repo, itemfoundq)
                    itemfound.get()
                    if ('%swiki' % (lang)) in itemfound.sitelinks:
                        continue
                    if 'P569' in itemfound.claims:
                        birthyear = itemfound.claims['P569'][0].getTarget().year
                        if birthyear and re.search(r'(?i)\[\[ *Category *\: *%s births *\]\]' % (birthyear), page.text):
                            print('%s birthyear found in item. Category:%s births found in page' % (birthyear, birthyear))
                            print('Adding sitelink %s:%s' % (lang, page.title().encode('utf-8')))
                            try:
                                itemfound.setSitelink(page, summary='BOT - Adding 1 sitelink: [[:%s:%s|%s]] (%s)' % (lang, page.title(), page.title(), lang))
                            except:
                                print("Error adding sitelink")
                                break
                            if not 'P31' in itemfound.claims:
                                addHumanClaim(repo=repo, item=itemfound)
                            if not 'P21' in itemfound.claims and gender:
                                addGenderClaim(repo=repo, item=itemfound, gender=gender)
                            if not 'P569' in itemfound.claims and birthdate:
                                addBirthDateClaim(repo=repo, item=itemfound, date=birthdate)
                            if not 'P570' in itemfound.claims and deathdate:
                                addDeathDateClaim(repo=repo, item=itemfound, date=deathdate)
                            if not 'P106' in itemfound.claims and occupations:
                                addOccupationsClaim(repo=repo, item=itemfound, occupations=occupations)
                            break
    
if __name__ == "__main__":
    main()
