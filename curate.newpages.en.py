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
        print("Adding claim: human")
        claim = pywikibot.Claim(repo, 'P31')
        target = pywikibot.ItemPage(repo, 'Q5')
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim)

def addGenderClaim(repo='', item='', gender=''):
    gender2q = { 'female': 'Q6581072', 'male': 'Q6581097' }
    if repo and item and gender and gender in gender2q.keys():
        print("Adding gender: %s" % (gender))
        claim = pywikibot.Claim(repo, 'P21')
        target = pywikibot.ItemPage(repo, gender2q[gender])
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        addImportedFrom(repo=repo, claim=claim)

def addBirthDateClaim(repo='', item='', date=''):
    if repo and item and date:
        print("Adding birth date: %s" % (date))
        return addDateClaim(repo=repo, item=item, claim='P569', date=date)

def addDeathDateClaim(repo='', item='', date=''):
    if repo and item and date:
        print("Adding death date: %s" % (date))
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
            print("Adding occupation: %s" % (occupation.title().encode('utf-8')))
            claim = pywikibot.Claim(repo, 'P106')
            target = pywikibot.ItemPage(repo, occupation.title())
            claim.setTarget(target)
            item.addClaim(claim, summary='BOT - Adding 1 claim')
            addImportedFrom(repo=repo, claim=claim)

def authorIsNewbie(page='', lang=''):
    if page:
        hist = page.getVersionHistory(reverse=True, total=1)
        if hist:
            editcount = getUserEditCount(user=hist[0].user, site='%s.wikipedia.org' % (lang))
            if editcount >= 200:
                return False
    return True

def calculateGender(page='', lang=''):
    if not page:
        return ''
    if lang == 'en':
        femalepoints = len(re.findall(r'(?i)\b(she|her|hers)\b', page.text))
        malepoints = len(re.findall(r'(?i)\b(he|his|him)\b', page.text))
        if re.search(r'(?im)\b(Category\s*:[^\]]*?female|Category\s*:[^\]]*?women|Category\s*:[^\]]*?actresses)\b', page.text) or \
           (len(page.text) <= 2000 and femalepoints >= 1 and malepoints == 0) or \
           (femalepoints >= 2 and femalepoints > malepoints*3):
            return 'female'
        elif re.search(r'(?im)\b(Category\s*:[^\]]*? male|Category\s*:[^\]]*? men)\b', page.text) or \
           (len(page.text) <= 2000 and malepoints >= 1 and femalepoints == 0) or \
           (malepoints >= 2 and malepoints > femalepoints*3):
            return 'male'
    return ''

def calculateBirthDate(page='', lang=''):
    if not page:
        return ''
    if lang == 'en':
        m = re.findall(r'(?im)\[\[\s*Category\s*:\s*(\d+) births\s*[\|\]]', page.text)
        if m:
            return m[0]
    return ''

def calculateDeathDate(page='', lang=''):
    if not page:
        return ''
    if lang == 'en':
        m = re.findall(r'(?im)\[\[\s*Category\s*:\s*(\d+) deaths\s*[\|\]]', page.text)
        if m:
            return m[0]
    return ''

def calculateOccupations(wikisite='', page='', lang=''):
    ignoreoccupations = [
        'Q2066131', #sportpeople, too general
    ]
    occupations = []
    if wikisite and page:
        if lang == 'en' or lang == '':
            cats = re.findall(r'(?i)\[\[\s*Category\s*\:([^\[\]\|]+?)[\]\|]', page.text)
        for cat in cats:
            cat = cat.strip()
            catpage = pywikibot.Page(wikisite, 'Category:%s' % (cat))
            catitem = ''
            try:
                catitem = pywikibot.ItemPage.fromPage(catpage)
            except:
                continue
            if not catitem:
                continue
            catitem.get()
            if catitem.claims:
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

def pageCategories(page='', lang=''):
    if lang == 'en':
        return len(re.findall(r'(?i)\[\[\s*Category\s*\:', page.text))
    return 0

def pageReferences(page='', lang=''):
    return len(re.findall(r'(?i)</ref>', page.text))

def pageIsBiography(page='', lang=''):
    if lang == 'en':
        if re.search('(?im)Category\s*:\s*\d+ animal (births|deaths)', page.text):
            return False
        elif not page.title().startswith('List ') and not page.title().startswith('Lists '):
            if len(page.title().split(' ')) <= 5:
                if re.search(r'(?im)(\'{3} \(born \d|Category\s*:\s*\d+ (births|deaths)|Category\s*:\s*Living people|birth_date\s*=|birth_place\s*=|death_date\s*=|death_place\s*=|==\s*Biography\s*==|Category\s*:\s*People from)', page.text):
                    return True
    return False

def pageIsRubbish(page='', lang=''):
    if lang == 'en' and re.search(r'(?im)\{\{\s*(db|AfD|Article for deletion|Notability)', page.text):
        return True
    return False

def addBiographyClaims(repo='', wikisite='', item='', page='', lang=''):
    if repo and wikisite and item and page:
        gender = calculateGender(page=page, lang=lang)
        birthdate = calculateBirthDate(page=page, lang=lang)
        deathdate = calculateDeathDate(page=page, lang=lang)
        occupations = calculateOccupations(wikisite=wikisite, page=page, lang=lang)
        try:
            item.get()
        except:
            print('Error while retrieving item, skiping...')
            return ''
        if not 'P31' in item.claims:
            addHumanClaim(repo=repo, item=item)
        if not 'P21' in item.claims and gender:
            addGenderClaim(repo=repo, item=item, gender=gender)
        if not 'P569' in item.claims and birthdate:
            addBirthDateClaim(repo=repo, item=item, date=birthdate)
        if not 'P570' in item.claims and deathdate:
            addDeathDateClaim(repo=repo, item=item, date=deathdate)
        if not 'P106' in item.claims and occupations:
            addOccupationsClaim(repo=repo, item=item, occupations=occupations)

def main():
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    repo = wdsite.data_repository()
    langs = ['en']
    for lang in langs:
        wikisite = pywikibot.Site(lang, 'wikipedia')
        total = 100
        if len(sys.argv) >= 2:
            total = int(sys.argv[1])
        gen = pagegenerators.NewpagesPageGenerator(site=wikisite, namespaces=[0], total=total)
        #cat = pywikibot.Category(wikisite, 'Category:Articles without Wikidata item')
        #gen = pagegenerators.CategorizedPageGenerator(cat, recurse=False)
        pre = pagegenerators.PreloadingGenerator(gen, groupsize=50)
        for page in pre:
            if page.isRedirectPage():
                continue
            if not pageIsBiography(page=page, lang=lang):
                continue
            print('\n==', page.title().encode('utf-8'), '==')
            gender = calculateGender(page=page, lang=lang)
            item = ''
            try:
                item = pywikibot.ItemPage.fromPage(page)
            except:
                pass
            if item:
                print('Page has item')
                print('https://www.wikidata.org/wiki/%s' % (item.title()))
                addBiographyClaims(repo=repo, wikisite=wikisite, item=item, page=page, lang=lang)
            else:
                print('Page without item')
                #search for a valid item, otherwise create
                if authorIsNewbie(page=page, lang=lang):
                    print("Newbie author, checking quality...")
                    if pageIsRubbish(page=page, lang=lang) or \
                       (not pageCategories(page=page, lang=lang)) or \
                       (not pageReferences(page=page)) or \
                       (not len(list(page.getReferences(namespaces=[0])))):
                        print("Page didnt pass minimum quality, skiping")
                        continue
                
                print(page.title().encode('utf-8'), 'need item', gender)
                wtitle = page.title()
                wtitle_ = wtitle.split('(')[0].strip()
                searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=%s&format=xml' % (urllib.parse.quote(wtitle_), lang)
                raw = getURL(searchitemurl)
                print(searchitemurl.encode('utf-8'))
                
                #check birthdate and if it matches, then add data
                numcandidates = '' #do not set to zero
                if not '<search />' in raw:
                    m = re.findall(r'id="(Q\d+)"', raw)
                    numcandidates = len(m)
                    print("Found %s candidates" % (numcandidates))
                    if numcandidates > 5: #too many candidates, skiping
                        print("Too many, skiping")
                        continue
                    for itemfoundq in m:
                        itemfound = pywikibot.ItemPage(repo, itemfoundq)
                        itemfound.get()
                        if ('%swiki' % (lang)) in itemfound.sitelinks:
                            print("Candidate %s has sitelink, skiping" % (itemfoundq))
                            numcandidates -= 1
                            continue
                        pagebirthyear = calculateBirthDate(page=page, lang=lang)
                        pagebirthyear = pagebirthyear and int(pagebirthyear.split('-')[0]) or ''
                        if not pagebirthyear:
                            print("Page doesnt have birthdate, skiping")
                            break #break, dont continue. Without birthdate we cant decide correctly
                        if 'P569' in itemfound.claims and itemfound.claims['P569'][0].getTarget().precision in [9, 10, 11]:
                            #https://www.wikidata.org/wiki/Help:Dates#Precision
                            itemfoundbirthyear = int(itemfound.claims['P569'][0].getTarget().year)
                            print("candidate birthdate = %s, page birthdate = %s" % (itemfoundbirthyear, pagebirthyear))
                            mindatelen = 4
                            if len(str(itemfoundbirthyear)) != mindatelen or len(str(pagebirthyear)) != mindatelen:
                                print("%s birthdate length != %s" % (itemfoundq, mindatelen))
                                continue
                            #reduce candidates if birthyear are different
                            minyeardiff = 3
                            if itemfoundbirthyear >= pagebirthyear + minyeardiff or itemfoundbirthyear <= pagebirthyear - minyeardiff:
                                print("Candidate %s birthdate out of range, skiping" % (itemfoundq))
                                numcandidates -= 1
                                continue
                            #but only assume it is the same person if birthyears match
                            if itemfoundbirthyear == pagebirthyear:
                                print('%s birthyear found in candidate %s. Category:%s births found in page. OK!' % (itemfoundbirthyear, itemfoundq, itemfoundbirthyear))
                                print('Adding sitelink %s:%s' % (lang, page.title().encode('utf-8')))
                                try:
                                    itemfound.setSitelink(page, summary='BOT - Adding 1 sitelink: [[:%s:%s|%s]] (%s)' % (lang, page.title(), page.title(), lang))
                                except:
                                    print("Error adding sitelink. Skiping.")
                                    break
                                addBiographyClaims(repo=repo, wikisite=wikisite, item=itemfound, page=page, lang=lang)
                                break
                
                #no item found, or no candidates are useful
                if '<search />' in raw or (numcandidates == 0):
                    print('No useful item found. Creating a new one...')
                    #create item
                    newitemlabels = { lang: wtitle_ }
                    newitem = pywikibot.ItemPage(repo)
                    newitem.editLabels(labels=newitemlabels, summary="BOT - Creating item for [[:%s:%s|%s]] (%s): %s %s" % (lang, wtitle, wtitle, lang, 'human', gender))
                    newitem.get()
                    try:
                        newitem.setSitelink(page, summary='BOT - Adding 1 sitelink: [[:%s:%s|%s]] (%s)' % (lang, page.title(), page.title(), lang))
                    except:
                        print("Error adding sitelink. Skiping.")
                        break
                    addBiographyClaims(repo=repo, wikisite=wikisite, item=newitem, page=page, lang=lang)

if __name__ == "__main__":
    main()
