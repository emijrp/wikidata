#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2024 emijrp <emijrp@gmail.com>
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

import datetime
import html
import os
import pickle
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

genders = {
    "femenino": "Q6581072", 
    "masculino": "Q6581097", 
}
languages = {
    "es": "Q1321", 
    "español": "Q1321", 
    "en": "Q1860", 
    "inglés": "Q1860", 
}
occupations = {
    "escritores": "Q36180",
    "médicos": "Q39631",
}
countries = {
    "argentina": { "q": "Q414" }, 
    "españa": { "q": "Q29" }, 
    "estados unidos": { "q": "Q30" }, 
    "francia": { "q": "Q142" }, 
    "reino unido": { "q": "Q145" }, 
}
locations = {
    "barcelona": { "q": "Q1492", "country": countries["españa"]["q"], "regexp": r"(?im)^(barcelona)?$" }, 
    "bilbao": { "q": "Q8692", "country": countries["españa"]["q"], "regexp": r"(?im)^(bilbao)?$" }, 
    "madrid": { "q": "Q2807", "country": countries["españa"]["q"], "regexp": r"(?im)^(madrid)?$" }, 
    "sevilla": { "q": "Q8717", "country": countries["españa"]["q"], "regexp": r"(?im)^(sevilla)?$" }, 
    "valencia": { "q": "Q8818", "country": countries["españa"]["q"], "regexp": r"(?im)^(valencia)?$" }, 
    "zaragoza": { "q": "Q10305", "country": countries["españa"]["q"], "regexp": r"(?im)^(zaragoza)?$" }, 
    
    "buenos aires": { "q": "Q1486", "country": countries["argentina"]["q"], "regexp": r"(?im)^(buenos aires)?$" }, 
    
    "londres": { "q": "Q84", "country": countries["reino unido"]["q"], "regexp": r"(?im)^(londres|london)?$" }, 
    
    "nueva york": { "q": "Q60", "country": countries["estados unidos"]["q"], "regexp": r"(?im)^(new york|nueva york)?$" },
     
    "parís": { "q": "Q90", "country": countries["francia"]["q"], "regexp": r"(?im)^(par[íi]s)?$" }, 
}
publishers = {
    "aconcagua": { "q": "Q124731301", "regexp": r"(?im)^(ed\.?|editorial)? ?(aconcagua) ?(libros?)?$" }, 
    "crítica": { "q": "Q5818611", "regexp": r"(?im)^(ed\.?|editorial)? ?(cr[íi]tica)$" }, 
}

def getBNEid(item=""):
    if not item:
        return
    bneid = ""
    if 'P950' in item.claims:
        if len(item.claims['P950']) == 1:
            bneid = item.claims['P950'][0].getTarget()
            return bneid
        else:
            print("More than one ID, skiping")
            return
    else:
        print("No tiene BNE id, skiping")
        return
    return

def getFullTitle(title="", subtitle=""):
    title = title.strip()
    subtitle = subtitle.strip()
    if not title:
        return ""
    if not subtitle:
        return title
    titlefull = title + " " + subtitle
    titlefull = re.sub(r"(?im)  +", " ", titlefull)
    chunks = []
    for chunk in titlefull.split(" : "):
        chunk = chunk[0].upper() + chunk[1:]
        chunks.append(chunk)
    fulltitle = ". ".join(chunks)
    return fulltitle.strip()

def getLegalDeposit(s=""):
    if not s:
        return 
    s = s.strip()
    if not re.search(r"(?im)^[A-Z]{1,2} \d+-\d{4}$", s):
        return 
    s = "DL " + s
    return s

def getExtensionInPages(s=""):
    if not s:
        return
    pages = 0
    if re.search(r"(?im)(\d+)\s*(?:pg?s?|p[aá]gs?|páginas?)\.?", s):
        pages = re.findall(r"(?im)(\d+)\s*(?:pg?s?|p[aá]gs?|páginas?)\.?", s)[0]
    pages = int(pages)
    return pages

def cleanSymbols(s=""):
    for i in range(50):
        s = s.strip().strip(" ").strip(",").strip(".").strip(":").strip(";")
        s = s.strip("[").strip("]").strip("(").strip(")").strip("{").strip("}")
        s = s.strip("©")
    return s

def getContributorsCore(role="", repo="", contributorsbneids="", s=""):
    if not role or not repo or not contributorsbneids or not s:
        return []
    
    personsq = []
    if role == "contributor":
        persons = re.findall(r"(?im)^([^;\[\]]{7,})", s)
    elif role == "foreword":
        persons = re.findall(r"(?im)(?:pr[óo]logo|prologado),? ?(?:del?|por|por el|por la)? ([^;\[\]]{7,})", s)
    elif role == "translator":
        persons = re.findall(r"(?im)(?:traducci[óo]n|traducid[oa]|traductora?),? ?(?:del?|por|por el|por la)? ([^;\[\]]{7,})", s)
    else:
        return personsq
    
    if persons:
        persons = cleanSymbols(s=persons[0])
        for person in persons.split(","):
            personq = ""
            person = cleanSymbols(s=person)
            if len(person) >= 7 and " " in person: #el espacio es para detectar q es "nombre apellido" al menos
                print("Buscando", person, "en", ",".join(contributorsbneids))
                for contributorbneid in contributorsbneids:
                    if personq:
                        continue
                    candidates = existsInWikidata(s=contributorbneid)
                    for candidate in candidates:
                        if personq:
                            continue
                        q = pywikibot.ItemPage(repo, candidate)
                        q.get()
                        if not "P950" in q.claims or not contributorbneid in [x.getTarget() for x in q.claims["P950"]]:
                            continue
                        for k, v in q.aliases.items():
                            for x in v:
                                if person.lower() == x.lower() or person.lower() in x.lower() or x.lower() in person.lower():
                                    personq = q.title()
                        for k in q.labels:
                            if person.lower() == k.lower() or person.lower() in k.lower() or k.lower() in person.lower():
                                personq = q.title()
                        if personq:
                            personsq.append(personq)
    return personsq

def getContributors(repo="", contributorsbneids="", s=""):
    return getContributorsCore(role="contributor", repo=repo, contributorsbneids=contributorsbneids, s=s)

def getTranslators(repo="", contributorsbneids="", s=""):
    return getContributorsCore(role="translator", repo=repo, contributorsbneids=contributorsbneids, s=s)

def getForewords(repo="", contributorsbneids="", s=""):
    return getContributorsCore(role="foreword", repo=repo, contributorsbneids=contributorsbneids, s=s)

def getPublicationLocation(s=""):
    if not s:
        return 
    s = cleanSymbols(s=s)
    for location, props in locations.items():
        if re.search(props["regexp"], s):
            return props["q"]
    return 

def getPublicationDate(s=""):
    if not s:
        return 
    s = cleanSymbols(s=s)
    if len(s) != 4 or not re.search(r"(?im)^[12]", s):
        return 
    return int(s)

def getPublisher(s=""):
    if not s:
        return
    s = cleanSymbols(s=s)
    for publisher, props in publishers.items():
        if re.search(props["regexp"], s):
            return props["q"]
    return

def existsInWikidata(s=""):
    if not s:
        return []
    print("\nSearching in Wikidata", s)
    lang = "en"
    #searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=%s&format=xml' % (urllib.parse.quote(s), lang)
    searchitemurl = 'https://www.wikidata.org/w/index.php?go=Go&search=%s' % (urllib.parse.quote(s))
    raw = getURL(url=searchitemurl)
    candidates = []
    if 'There were no results' in raw:
        print("Not found in Wikidata")
        return candidates
    else:
        candidates = re.findall(r'/wiki/(Q\d+)"', raw)
        numcandidates = len(candidates)
        print("Found %s candidates" % (numcandidates))
        return candidates

def addBNERef(repo='', claim='', bneid=''):
    #el bneid puede ser una obra, un libro o un autor
    if repo and claim and bneid:
        itembne = pywikibot.ItemPage(repo, "Q50358336")
        today = datetime.date.today()
        year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    
        refstatedinclaim = pywikibot.Claim(repo, 'P248')
        refstatedinclaim.setTarget(itembne)
        refretrieveddateclaim = pywikibot.Claim(repo, 'P813')
        refretrieveddateclaim.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
        refbneidclaim = pywikibot.Claim(repo, 'P950')
        refbneidclaim.setTarget(bneid)
        claim.addSources([refstatedinclaim, refretrieveddateclaim, refbneidclaim], summary='BOT - Adding 1 reference')

def addGoodReadsRef(repo='', claim=''):
    if repo and claim:
        itemgoodreads = pywikibot.ItemPage(repo, "Q2359213")
        today = datetime.date.today()
        year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    
        refstatedinclaim = pywikibot.Claim(repo, 'P248')
        refstatedinclaim.setTarget(itemgoodreads)
        refretrieveddateclaim = pywikibot.Claim(repo, 'P813')
        refretrieveddateclaim.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
        claim.addSources([refstatedinclaim, refretrieveddateclaim], summary='BOT - Adding 1 reference')

def addOpenLibraryRef(repo='', claim=''):
    if repo and claim:
        itemopenlibrary = pywikibot.ItemPage(repo, "Q1201876")
        today = datetime.date.today()
        year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    
        refstatedinclaim = pywikibot.Claim(repo, 'P248')
        refstatedinclaim.setTarget(itemopenlibrary)
        refretrieveddateclaim = pywikibot.Claim(repo, 'P813')
        refretrieveddateclaim.setTarget(pywikibot.WbTime(year=year, month=month, day=day))
        claim.addSources([refstatedinclaim, refretrieveddateclaim], summary='BOT - Adding 1 reference')

def improveItem(p31="", item="", repo="", props={}):
    if p31 and item and repo and props:
        site = pywikibot.Site('wikidata', 'wikidata')
        itempage = pywikibot.Page(site, item)
        history = itempage.getVersionHistoryTable(reverse=True, total=1)
        #print(history)
        if not "Emijrpbot" in history:
            print("No creado por mi bot, saltando...")
            return
    return createItem(p31=p31, item=item, repo=repo, props=props)

def createItem(p31="", item="", repo="", props={}):
    #https://www.wikidata.org/wiki/Wikidata:WikiProject_Books#Work_item_properties
    #https://www.wikidata.org/wiki/Wikidata:WikiProject_Books#Edition_item_properties
    if not p31 or not repo or not props:
        return
    lang = "es"
    today = datetime.date.today()
    year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    if item:
        workitem = pywikibot.ItemPage(repo, item)
    else:
        workitemlabels = { lang: props["fulltitle"] }
        workitem = pywikibot.ItemPage(repo)
        workitem.editLabels(labels=workitemlabels, summary="BOT - Creating item")
    workitem.get()
    #labels
    if not lang in workitem.labels:
        print("Añadiendo labels")
        labels = workitem.labels
        labels[lang] = props["fulltitle"]
        workitem.editLabels(labels=labels, summary="BOT - Adding labels (1 languages): %s" % (lang))
    else:
        print("Ya tiene labels")
    #descs
    if not lang in workitem.descriptions or not "en" in workitem.descriptions or not "fr" in workitem.descriptions or not "ca" in workitem.descriptions or not "gl" in workitem.descriptions:
        authoritem = pywikibot.ItemPage(repo, props["authorq"])
        authoritem.get()
        authorname = lang in authoritem.labels and authoritem.labels[lang] or ""
        authornameen = "en" in authoritem.labels and authoritem.labels["en"] or authorname
        authornamefr = "fr" in authoritem.labels and authoritem.labels["fr"] or authornameen
        authornameca = "ca" in authoritem.labels and authoritem.labels["ca"] or authornameen
        authornamegl = "gl" in authoritem.labels and authoritem.labels["gl"] or authornameen
        if p31 == "work":
            print("Añadiendo descripciones")
            descriptions = workitem.descriptions
            descriptions[lang] = "obra escrita" + (authorname and " por %s" % (authorname) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): %s" % (lang))
            descriptions["en"] = "written work" + (authornameen and " by %s" % (authornameen) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): en")
            descriptions["fr"] = "ouvrage écrit" + (authornamefr and " par %s" % (authornamefr) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): fr")
            descriptions["ca"] = "obra escrita" + (authornameca and " per %s" % (authornameca) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): ca")
            descriptions["gl"] = "obra escrita" + (authornamegl and " por %s" % (authornamegl) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): gl")
        if p31 == "edition":
            print("Añadiendo descripciones")
            descriptions = workitem.descriptions
            descriptions[lang] = "edición" + (props["publicationdate"] and " publicada en %s" % (props["publicationdate"])) + (authorname and " de la obra escrita por %s" % (authorname) or "") 
            descriptions["en"] = (props["publicationdate"] and "%s " % (props["publicationdate"])) + "edition" + (authornameen and " of written work by %s" % (authornameen) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): %s" % (lang))
    else:
        print("Ya tiene descripciones")
    #aliases
    if props["alternatetitles"]:
        for alternatetitle in props["alternatetitles"]:
            if alternatetitle != props["title"]:
                if lang in workitem.aliases and not alternatetitle in workitem.aliases[lang]:
                    aliases = workitem.aliases
                    aliases[lang].append(alternatetitle)
                    workitem.editAliases(aliases=aliases, summary="BOT - Adding 1 aliases (%s): %s" % (lang, alternatetitle))
                if not lang in workitem.aliases:
                    aliases = workitem.aliases
                    aliases[lang] = [alternatetitle]
                    workitem.editAliases(aliases=aliases, summary="BOT - Adding 1 aliases (%s): %s" % (lang, alternatetitle))
    else:
        print("No conocemos titulo alternativo o es igual al titulo")
    #P31 = Q47461344 written work
    if p31 == "work":
        if not "P31" in workitem.claims:
            print("Añadiendo P31")
            claim = pywikibot.Claim(repo, 'P31')
            target = pywikibot.ItemPage(repo, 'Q47461344')
            claim.setTarget(target)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
        else:
            print("Ya tiene P31")
    #P31 = Q3331189 edition
    if p31 == "edition":
        if not "P31" in workitem.claims:
            print("Añadiendo P31")
            claim = pywikibot.Claim(repo, 'P31')
            target = pywikibot.ItemPage(repo, 'Q3331189')
            claim.setTarget(target)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
        else:
            print("Ya tiene P31")
    #P50 = authorq
    if p31:
        if not "P50" in workitem.claims:
            print("Añadiendo P50")
            claim = pywikibot.Claim(repo, 'P50')
            target = pywikibot.ItemPage(repo, props["authorq"])
            claim.setTarget(target)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
        else:
            print("Ya tiene P50")
        
    #P767 = contributor (not the main author)
    if p31 == "edition":
        if props["contributorsq"]:
            for contributor in props["contributorsq"]:
                if contributor == props["authorq"] or contributor in props["traductorsq"] or contributor in props["forewordsq"]:
                    #no meter al autor, traductor, prologador como contributor de nuevo
                    continue
                if not "P767" in workitem.claims or not contributor in [x.getTarget().title() for x in workitem.claims["P767"]]:
                    print("Añadiendo P767")
                    claim = pywikibot.Claim(repo, 'P767')
                    target = pywikibot.ItemPage(repo, contributor)
                    claim.setTarget(target)
                    workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                    addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
                else:
                    print("Ya tiene P767")
        
    #P2679 = author of foreword
    if p31 == "edition":
        if props["forewordsq"]:
            for foreword in props["forewordsq"]:
                #if contributor == props["authorq"]: #un autor puede prologar su propia obra
                #    continue
                if not "P2679" in workitem.claims:
                    print("Añadiendo P2679")
                    claim = pywikibot.Claim(repo, 'P2679')
                    target = pywikibot.ItemPage(repo, foreword)
                    claim.setTarget(target)
                    workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                    addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
                else:
                    print("Ya tiene P2679")
    
    #P1476 = title
    if p31:
        if not "P1476" in workitem.claims:
            print("Añadiendo P1476")
            claim = pywikibot.Claim(repo, 'P1476')
            target = pywikibot.WbMonolingualText(text=props["fulltitle"], language=lang)
            claim.setTarget(target)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
        else:
            print("Ya tiene P1476")
    #P407 = language of work
    if p31:
        if not "P407" in workitem.claims:
            print("Añadiendo P407")
            claim = pywikibot.Claim(repo, 'P407')
            target = pywikibot.ItemPage(repo, languages[lang])
            claim.setTarget(target)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
        else:
            print("Ya tiene P407")
    #P123 = publisher
    if p31 == "edition":
        if props["publisher"]:
            if not "P123" in workitem.claims:
                print("Añadiendo P123")
                claim = pywikibot.Claim(repo, 'P123')
                target = pywikibot.ItemPage(repo, props["publisher"])
                claim.setTarget(target)
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P123")
    #P291 = place of publication
    if p31 == "edition":
        if props["publicationlocation"]:
            if not "P291" in workitem.claims:
                print("Añadiendo P291")
                claim = pywikibot.Claim(repo, 'P291')
                target = pywikibot.ItemPage(repo, props["publicationlocation"])
                claim.setTarget(target)
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P291")
    #P577 = publication date
    if props["publicationdate"]:
        if not "P577" in workitem.claims:
            print("Añadiendo P577")
            claim = pywikibot.Claim(repo, 'P577')
            claim.setTarget(pywikibot.WbTime(year=props["publicationdate"]))
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
        else:
            print("Ya tiene P407")
    #P1104 = number of pages
    if p31 == "edition":
        if props["pages"]:
            if not "P1104" in workitem.claims:
                print("Añadiendo P1104")
                claim = pywikibot.Claim(repo, 'P1104')
                claim.setTarget(pywikibot.WbQuantity(amount=props["pages"]))
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P1104")
    
    #P8383 = goodreads work id
    if p31 == "work":
        if props["goodreadsworkid"]:
            if not "P8383" in workitem.claims:
                print("Añadiendo P8383")
                claim = pywikibot.Claim(repo, 'P8383')
                claim.setTarget(props["goodreadsworkid"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addGoodReadsRef(repo=repo, claim=claim)
            else:
                print("Ya tiene P8383")
    #P648 = openlibrary work id
    if p31 == "work":
        if props["openlibraryworkid"]:
            if not "P648" in workitem.claims:
                print("Añadiendo P648")
                claim = pywikibot.Claim(repo, 'P648')
                claim.setTarget(props["openlibraryworkid"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addOpenLibraryRef(repo=repo, claim=claim)
            else:
                print("Ya tiene P648")
    
    #P2969 = goodreads edition id
    if p31 == "edition":
        if props["goodreadseditionid"]:
            if not "P2969" in workitem.claims:
                print("Añadiendo P2969")
                claim = pywikibot.Claim(repo, 'P2969')
                claim.setTarget(props["goodreadseditionid"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addGoodReadsRef(repo=repo, claim=claim)
            else:
                print("Ya tiene P2969")
    #P648 = openlibrary edition id
    if p31 == "edition":
        if props["openlibraryeditionid"]:
            if not "P648" in workitem.claims:
                print("Añadiendo P648")
                claim = pywikibot.Claim(repo, 'P648')
                claim.setTarget(props["openlibraryeditionid"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addOpenLibraryRef(repo=repo, claim=claim)
            else:
                print("Ya tiene P648")
    
    #P957 = isbn10
    if p31 == "edition":
        if props["isbn10"]:
            if not "P957" in workitem.claims:
                print("Añadiendo P957")
                claim = pywikibot.Claim(repo, 'P957')
                claim.setTarget(props["isbn10"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P957")
    #P212 = isbn13
    if p31 == "edition":
        if props["isbn13"]:
            if not "P212" in workitem.claims:
                print("Añadiendo P212")
                claim = pywikibot.Claim(repo, 'P212')
                claim.setTarget(props["isbn13"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P212")
    #P6164 = depósito legal
    if p31 == "edition":
        if props["legaldeposit"]:
            if not "P6164" in workitem.claims:
                print("Añadiendo P6164")
                claim = pywikibot.Claim(repo, 'P6164')
                claim.setTarget(props["legaldeposit"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P6164")
    #P950 = bne id
    if p31 == "edition":
        if props["resourceid"]:
            if not "P950" in workitem.claims:
                print("Añadiendo P950")
                claim = pywikibot.Claim(repo, 'P950')
                claim.setTarget(props["resourceid"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P950")
    
    #more ideas
    #country of origin	P495
    #contributor to the creative work or subject	P767, mejor no, puede variar con la edición (los que prologan, etc)

def getGoodReadsWorkId(title="", isbn10="", isbn13=""):
    #<a class="DiscussionCard" href="https://www.goodreads.com/work/quotes/97295167">
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = ""
    isbn10 = isbn10.replace("-", "")
    isbn13 = isbn13.replace("-", "")
    if isbn10:
        busqueda = isbn10
    if isbn13:
        busqueda = isbn13
    url = "https://www.goodreads.com/search?q=" + urllib.parse.quote_plus(busqueda)
    raw = getURL(url=url)
    goodreadsworkid = ""
    if '"isbn":"%s"' % (isbn10) in raw or '"isbn13":"%s"' % (isbn13) in raw:
        goodreadsworkid = "https://www.goodreads.com/work/quotes/" in raw and re.findall(r"(?im)href=\"https://www\.goodreads\.com/work/quotes/(\d+)\">", raw)[0] or ""
    return goodreadsworkid
            
def getGoodReadsEditionId(title="", isbn10="", isbn13=""):
    #href="https://www.goodreads.com/es/book/show/61688544"
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = ""
    isbn10 = isbn10.replace("-", "")
    isbn13 = isbn13.replace("-", "")
    if isbn10:
        busqueda = isbn10
    if isbn13:
        busqueda = isbn13
    url = "https://www.goodreads.com/search?q=" + urllib.parse.quote_plus(busqueda)
    raw = getURL(url=url)
    goodreadseditionid = ""
    if '"isbn":"%s"' % (isbn10) in raw or '"isbn13":"%s"' % (isbn13) in raw:
        goodreadseditionid = "https://www.goodreads.com/es/book/show/" in raw and re.findall(r"(?im)href=\"https://www\.goodreads\.com/es/book/show/(\d+)\"", raw)[0] or ""
    return goodreadseditionid
            
def getOpenLibraryWorkId(title="", isbn10="", isbn13=""):
    #<input type="hidden" name="work_id" value="/works/OL28180208W"/>
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = ""
    isbn10 = isbn10.replace("-", "")
    isbn13 = isbn13.replace("-", "")
    if isbn10:
        busqueda = isbn10
    if isbn13:
        busqueda = isbn13
    url = "https://openlibrary.org/search?q=" + urllib.parse.quote_plus(busqueda)
    raw = getURL(url=url)
    openlibraryworkid = ""
    if re.search(r'(?im)itemprop="isbn">\s*%s\s*</dd>' % (isbn10), raw) or re.search(r'(?im)itemprop="isbn">\s*%s\s*</dd>' % (isbn13), raw):
        openlibraryworkid = 'name="work_id" value="/works/' in raw and re.findall(r'(?im)<input type="hidden" name="work_id" value="/works/([^<>]+?)"/>', raw)[0] or ""
    return openlibraryworkid

def getOpenLibraryEditionId(title="", isbn10="", isbn13=""):
    #<input type="hidden" name="edition_id" value="/books/OL38578288M"/>
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = ""
    isbn10 = isbn10.replace("-", "")
    isbn13 = isbn13.replace("-", "")
    if isbn10:
        busqueda = isbn10
    if isbn13:
        busqueda = isbn13
    url = "https://openlibrary.org/search?q=" + urllib.parse.quote_plus(busqueda)
    raw = getURL(url=url)
    openlibraryeditionid = ""
    if re.search(r'(?im)itemprop="isbn">\s*%s\s*</dd>' % (isbn10), raw) or re.search(r'(?im)itemprop="isbn">\s*%s\s*</dd>' % (isbn13), raw):
        openlibraryeditionid = 'name="edition_id" value="/books/' in raw and re.findall(r'(?im)<input type="hidden" name="edition_id" value="/books/([^<>]+?)"/>', raw)[0] or ""
    return openlibraryeditionid

def unquote(s=""):
    s = urllib.parse.unquote_plus(s)
    s = html.unescape(s)
    return s

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    qlist = ["Q93433647"] #eusebio
    qlist = ["Q5865630"] #paco espinosa
    
    for authorq in qlist:
        time.sleep(1)
        print('\n== %s ==' % (authorq))
        print('https://www.wikidata.org/wiki/%s' % (authorq))
        item = pywikibot.ItemPage(repo, authorq)
        try: #to detect Redirect because .isRedirectPage fails
            item.get()
        except:
            print('Error while .get()')
            continue
        
        authorbneid = getBNEid(item=item)
        if not authorbneid:
            print("No BNE id, skiping")
            continue
        if not authorbneid.startswith("XX"):
            print("BNE ID not starts with XX, skiping")
            continue
        
        url = "https://datos.bne.es/resource/" + authorbneid
        raw = getURL(url=url)
        if "página no encontrada, pero no estás perdido" in raw:
            print("Error bneid")
            continue
        
        #propiedades del rdf
        #viaf isni etc tb lo ponen como <owl:sameAs rdf:resource="..."/>
        urlrdf = "https://datos.bne.es/resource/%s.rdf" % (authorbneid)
        rawrdf = getURL(url=urlrdf)
        m = re.findall(r"(?im)<rdfs:label>([^<>]*?)</rdfs:label>", rawrdf)
        label = m and unquote(s=m[0]) or ""
        m = re.findall(r"(?im)<ns\d:P50116>(Masculino|Femenino)</ns\d:P50116>", rawrdf)
        gender = m and genders[m[0].lower()] or ""
        m = re.findall(r"(?im)<ns\d:P5024>https?://isni\.org/isni/(\d+)/?</ns\d:P5024>", rawrdf)
        isniid = m and m[0] or ""
        m = re.findall(r"(?im)<ns\d:P5024>https?://viaf\.org/viaf/(\d+)/?</ns\d:P5024>", rawrdf)
        viafid = m and m[0] or ""
        m = re.findall(r"(?im)<ns\d:P50102>(Español|Inglés)</ns\d:P50102>", rawrdf)
        language = m and languages[unquote(s=m[0]).lower()] or ""
        m = re.findall(r"(?im)<ns\d:P50119>([^<>]*?)</ns\d:P50119>", rawrdf)
        birthplace = m and unquote(s=m[0]) or ""
        m = re.findall(r"(?im)<ns\d:P5010>(\d{4})</ns\d:P5010>", rawrdf)
        birthdate = m and int(m[0]) or ""
        m = re.findall(r"(?im)<ns\d:P5011>(\d{4})</ns\d:P5011>", rawrdf)
        deathdate = m and int(m[0]) or ""
        
        print(label)
        print(gender, language, birthplace)
        print(birthdate, deathdate)
        print(isniid, viafid)
        
        if (not birthdate and not deathdate) or (birthdate and birthdate < 1900) or (deathdate and deathdate < 1980):
            print("Autor antiguo, saltamos")
            continue
        
        #obras, el rdf no es completo? mejor parsearlo así por html
        obras = ""
        if '<section id="obras" class="container">' in raw:
            obras = raw.split('<section id="obras" class="container">')[1].split('</section>')[0]
        #cuidado distinguir entre obra, libro, dvd, recurso electrónico, etc
        for obra in obras.split("</li>"):
            time.sleep(0.1)
            resourceid = "/resource/" in obra and re.findall(r"(?im)href=\"/resource/([^<>\"]+?)\"", obra)[0] or ""
            titletruncated = "item-link" in obra and unquote(re.findall(r"(?im)class=\"item-link\">([^<>]+?)</a>", obra)[0]) or ""
            urlresource = "https://datos.bne.es/resource/%s.rdf" % (resourceid)
            if not resourceid:
                continue
            print('\n== %s ==' % (resourceid))
            print(titletruncated)
            print(urlresource)
            if not '<div class="text-center">Libro</div>' in obra:
                print("Por ahora solo libros. Saltando obras tb")
                continue
            rawresource = getURL(url=urlresource)
            
            m = re.findall(r"(?im)<ns\d:P3002>([^<>]+?)</ns\d:P3002>", rawresource)
            title = m and unquote(m[0]) or ""
            m = re.findall(r"(?im)<ns\d:P3014>([^<>]+?)</ns\d:P3014>", rawresource)
            subtitle = m and unquote(m[0]) or ""
            alternatetitle = title + " " + subtitle
            alternatetitle2 = alternatetitle.replace(" : ", ": ")
            alternatetitle3 = alternatetitle.replace(" : ", ", ")
            alternatetitle4 = alternatetitle.replace(" : ", " ")
            alternatetitles = list(set([alternatetitle, alternatetitle2, alternatetitle3, alternatetitle4]))
            fulltitle = getFullTitle(title=title, subtitle=subtitle)
            
            m = re.findall(r"(?im)<ns\d:P3008>([^<>]+?)</ns\d:P3008>", rawresource)
            contributors = m and unquote(m[0]) or ""
            if not contributors:
                print("No info de contributor, saltamos")
                continue
            #if ',' in contributors.split(';')[0] or ' y ' in contributors.split(';')[0]:
            #    print("Mas de un contributor, saltamos")
            #    continue
            contributorsbneids = re.findall(r"(?im)<ns\d:OP3006 rdf:resource=\"https://datos\.bne\.es/resource/([^<>]+?)\"\s*/>", rawresource)
            contributorsq = getContributors(repo=repo, contributorsbneids=contributorsbneids, s=contributors)
            forewordsq = getForewords(repo=repo, contributorsbneids=contributorsbneids, s=contributors)
            translatorsq = getTranslators(repo=repo, contributorsbneids=contributorsbneids, s=contributors)
            
            m = re.findall(r"(?im)<ns\d:P3001>([^<>]+?)</ns\d:P3001>", rawresource)
            publisher = m and getPublisher(s=unquote(m[0])) or ""
            m = re.findall(r"(?im)<ns\d:P3003>([^<>]+?)</ns\d:P3003>", rawresource)
            publicationlocation = m and getPublicationLocation(s=unquote(m[0])) or ""
            m = re.findall(r"(?im)<ns\d:P3006>([^<>]+?)</ns\d:P3006>", rawresource)
            publicationdate = m and getPublicationDate(s=unquote(m[0])) or ""
            if not publicationdate:
                print("No se encontro anyo, es necesario para distinguir entre ediciones, saltamos")
                continue
            if publicationdate and ((birthdate and publicationdate < birthdate) or (deathdate and publicationdate > deathdate)):
                print("La obra fue publicada antes del nacimiento o despues de la muerte, saltamos")
                continue
            m = re.findall(r"(?im)<ns\d:P3017>([^<>]+?)</ns\d:P3017>", rawresource)
            edition = m and unquote(m[0]) or ""
            m = re.findall(r"(?im)<ns\d:P3004>([^<>]+?)</ns\d:P3004>", rawresource)
            extension = m and unquote(m[0]) or ""
            pages = getExtensionInPages(s=extension)
            if pages < 100 or pages > 500:
                print("Numero de paginas raro, saltamos", pages)
                continue
            m = re.findall(r"(?im)<ns\d:P3013>([^<>]+?)</ns\d:P3013>", rawresource)
            isbn = m and unquote(m[0]) or ""
            isbnplain = isbn and isbn.replace("-", "") or ""
            isbn10 = ""
            isbn13 = ""
            if len(isbnplain) == 10:
                isbn10 = isbn
            elif len(isbnplain) == 13:
                isbn13 = isbn
            else:
                isbn = ""
                isbnplain = ""
            if not isbn:
                print("ISBN valido no encontrado, saltamos")
                continue
            m = re.findall(r"(?im)<ns\d:P3009>([^<>]+?)</ns\d:P3009>", rawresource)
            legaldeposit = m and getLegalDeposit(s=unquote(m[0])) or ""
            m = re.findall(r"(?im)<ns\d:P3062>([^<>]+?)</ns\d:P3062>", rawresource)
            mediatype = m and unquote(m[0]) or ""
            if re.search(r"(?im)(e[ -]?book|elec|cd|dvd|disco|rom|dig|comp|ord|internet|web|recu|l[ií]nea|plano|foto|mapa|cartel|case|nega|partitura|mina|hoja|online|micro|v[íi]deo|sono|carpe|carta|piano|rollo)", extension+mediatype):
                print("Extension/Medio no interesa, skiping", extension+mediatype)
                continue
            
            #external ids
            goodreadsworkid = getGoodReadsWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            openlibraryworkid = getOpenLibraryWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            
            goodreadseditionid = getGoodReadsEditionId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            openlibraryeditionid = getOpenLibraryEditionId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            
            props = {
                "title": title, 
                "subtitle": subtitle, 
                "alternatetitles": alternatetitles, 
                "fulltitle": fulltitle, 
                
                "authorq": authorq, 
                "authorbneid": authorbneid, 
                "contributorsq": contributorsq, 
                "forewordsq": forewordsq, 
                "translatorsq": translatorsq, 
                
                "resourceid": resourceid, 
                "pages": pages, 
                
                "publisher": publisher, 
                "publicationlocation": publicationlocation, 
                "publicationdate": publicationdate, 
                
                "isbn": isbn, 
                "isbnplain": isbnplain, 
                "isbn10": isbn10, 
                "isbn13": isbn13, 
                "isbnplain": isbnplain, 
                "legaldeposit": legaldeposit, 
                
                "goodreadsworkid": goodreadsworkid, 
                "openlibraryworkid": openlibraryworkid, 
                
                "goodreadseditionid": goodreadseditionid, 
                "openlibraryeditionid": openlibraryeditionid, 
            }
            print(props.items())
            
            donecandidates = []
            candidates = []
            candidates += existsInWikidata(s=isbn)
            candidates += existsInWikidata(s=isbnplain)
            candidates += existsInWikidata(s=isbn10)
            candidates += existsInWikidata(s=isbn13)
            candidates += existsInWikidata(s=resourceid)
            candidates += existsInWikidata(s=goodreadsworkid)
            candidates += existsInWikidata(s=openlibraryworkid)
            candidates += existsInWikidata(s=goodreadseditionid)
            candidates += existsInWikidata(s=openlibraryeditionid)
            candidates += existsInWikidata(s=fulltitle)
            candidates = list(set(candidates))
            candidates.sort()
            workcreated = []
            editionscreated = []
            for candidate in candidates:
                if candidate in donecandidates:
                    continue
                print("Encontrado candidato", candidate)
                donecandidates.append(candidate)
                candidateitem = pywikibot.ItemPage(repo, candidate)
                candidateitem.get()
                if "P31" in candidateitem.claims:
                    for candidateitemp31 in candidateitem.claims["P31"]:
                        if "Q47461344" in candidateitemp31.getTarget().title(): #work
                            improveItem(p31="work", item=candidate, repo=repo, props=props)
                            workcreated.append(candidate)
                        elif "Q3331189" in candidateitemp31.getTarget().title(): #edition
                            improveItem(p31="edition", item=candidate, repo=repo, props=props)
                            editionscreated.append(candidate)
            
            workq = ""
            editionq = ""
            if not workcreated:
                print("No se encontraron candidatos para el work, creamos")
                workq = createItem(p31="work", repo=repo, props=props)
            if not editionscreated:
                print("No se encontraron candidatos para la edition, creamos")
                editionq = createItem(p31="edition", repo=repo, props=props)
            if workq and editionq:
                linkWorkAndEdition(workq=workq, editionq=editionq)
            
            #if resourceid in ["a7153685", "a5311062"]:
            #    sys.exit()

if __name__ == "__main__":
    main()
