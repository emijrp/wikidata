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
    
    "ar": "Q13955", 
    "ara": "Q13955", 
    "árabe": "Q13955", 
    
    "an": "Q8765", 
    "arg": "Q8765", 
    "aragonés": "Q8765", 
    
    "eu": "Q8752", 
    "baq": "Q8752", 
    "vasco": "Q8752", 
    "vascuence": "Q8752", 
    "euskera": "Q8752", 
    
    "ast": "Q29507", 
    "ast": "Q29507", 
    "asturiano": "Q29507", 
    
    "ca": "Q7026", 
    "cat": "Q7026", 
    "catalán": "Q7026", 
    
    "es": "Q1321", 
    "spa": "Q1321", 
    "español": "Q1321", 
    
    "en": "Q1860", 
    "eng": "Q1860", 
    "inglés": "Q1860", 
    
    "fr": "Q150", 
    "fre": "Q150", 
    "francés": "Q150", 
    
    "gl": "Q9307", 
    "glg": "Q9307", 
    "gallego": "Q9307", 
    
}
languages2iso = {
    "ara": "ar", 
    "arg": "an", 
    "ast": "ast", 
    "baq": "eu", 
    "cat": "ca", 
    "dut": "nl", 
    "eng": "en", 
    "fre": "fr", 
    "ger": "de", 
    "glg": "gl", 
    "ita": "it", 
    "lat": "la", 
    "pol": "pl", 
    "por": "pt", 
    "rum": "ro", 
    "spa": "es", 
    "rus": "ru", 
    #"mul": "", #multiple languages
    #"zxx": "", #no language
}
occupations = {
    "abogados": "Q40348",
    "arquitectos": "Q42973",
    "criticos literarios": "Q4263842",
    "críticos literarios": "Q4263842",
    "diplomaticos": "Q193391",
    "diplomáticos": "Q193391",
    "dramaturgos": "Q214917",
    "economistas": "Q188094",
    "ensayista": "Q11774202",
    "escritores": "Q36180",
    "filologos": "Q13418253",
    "filólogos": "Q13418253",
    "filosofos": "Q4964182",
    "filósofos": "Q4964182",
    "historiadores": "Q201788",
    "historiadores del arte": "Q1792450",
    "ilustradores": "Q644687",
    "linguistas": "Q14467526",
    "medicos": "Q39631",
    "médicos": "Q39631",
    "novelistas": "Q6625963",
    "periodistas": "Q1930187",
    "poetas": "Q49757",
    "politicos": "Q82955", #viene sin tilde a veces
    "políticos": "Q82955",
    "profesores universitarios": "Q1622272",
    "teologos": "Q1234713",
    "teólogos": "Q1234713",
    "traductores": "Q333634",
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
    "aconcagua": { "q": "Q124731301", "regexp": r"aconcagua" }, 
    "akal": { "q": "Q5817833", "regexp": r"akal" }, 
    "alfaguara": { "q": "Q3324371", "regexp": r"alfaguara" }, 
    "alianza editorial": { "q": "Q8195536", "regexp": r"alianza editorial" }, 
    "anagrama": { "q": "Q8772125", "regexp": r"anagrama" }, 
    "anaya": { "q": "Q5394209", "regexp": r"anaya" }, 
    "booket": { "q": "Q124796493", "regexp": r"booket" }, 
    "bruguera": { "q": "Q3275000", "regexp": r"bruguera" }, 
    "círculo de lectores": { "q": "Q45762085", "regexp": "c[íi]rculo de lectores" }, 
    "círculo rojo": { "q": "Q5818613", "regexp": "c[íi]rculo rojo" }, 
    "crítica": { "q": "Q5818611", "regexp": "cr[íi]tica" }, 
    "debolsillo": { "q": "Q30103625", "regexp": "de[ -]?bolsillo" }, 
    "destino": { "q": "Q8771933", "regexp": "destino" }, 
    "edaf": { "q": "Q124796404", "regexp": "edaf" }, 
    "edebe": { "q": "Q8771871", "regexp": "edeb[ée]" }, 
    "ediciones b": { "q": "Q3047577", "regexp": "ediciones b" }, 
    "espasa-calpe": { "q": "Q16912403", "regexp": "espasa[ -]calpe" }, 
    "everest": { "q": "Q28324222", "regexp": "everest" }, 
    "paraninfo": { "q": "Q21036714", "regexp": "paraninfo" }, 
    "planeta": { "q": "Q2339634", "regexp": "planeta" }, 
    "plaza & janes": { "q": "Q6079378", "regexp": "plaza ?[&y]? ?jan[ée]s" }, 
    "rba": { "q": "Q5687784", "regexp": "rba" }, 
    "santillana": { "q": "Q3118243", "regexp": "santillana" }, 
    "salvat": { "q": "Q3817619", "regexp": "salvat" }, 
}
for publisher, props in publishers.items():
    publishers[publisher]["regexp"] = r"(?im)^(?:ed\.?|editorial|ediciones|libros?|publicaciones)?[ \.\,]*(%s)[ \.\,]*(?:ed\.?|editorial|ediciones|libros?|publicaciones)?$" % (publishers[publisher]["regexp"])

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

def getHeightInCM(s=""):
    if not s:
        return
    height = 0
    if re.search(r"(?im)^(\d+)\s*(?:cm|cent[íi]metros?)\.?$", s):
        height = re.findall(r"(?im)^[\.\,\;]*(\d+)\s*(?:cm|cent?[íi]?m?e?t?r?o?s?)[\.\,\;]*$", s)[0]
    height = int(height)
    return height

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
        persons = re.findall(r"(?im)(?:pr[óo]logo|prologado|introducci[óo]n|introducid[oa]|presentaci[óo]n|presentad[oa]),? ?(?:del?|por|por el|por la)? ([^;\[\]]{7,})", s)
    elif role == "translator":
        persons = re.findall(r"(?im)(?:traducci[óo]n|traducid[oa]|traductora?),? ?(?:del?|por|por el|por la)? ([^;\[\]]{7,})", s)
    else:
        return personsq
    
    candidates = [] #small cache for loop
    if persons:
        persons = cleanSymbols(s=persons[0])
        for person in persons.split(","):
            personq = ""
            person = cleanSymbols(s=person)
            if len(person) >= 7 and " " in person: #el espacio es para detectar q es "nombre apellido" al menos
                print("\nBuscando", person, "en", ", ".join(contributorsbneids))
                if not candidates: #check if search cache available
                    candidates = searchInWikidata(l=contributorsbneids)
                for candidate in candidates:
                    if personq:
                        break
                    q = pywikibot.ItemPage(repo, candidate)
                    q.get()
                    if not "P950" in q.claims or sum([contributorbneid in [x.getTarget() for x in q.claims["P950"]] for contributorbneid in contributorsbneids]) == 0:
                        #no tiene el bne id, aunque haya salido en la busqueda, no es este
                        continue
                    for k, v in q.aliases.items():
                        for x in v:
                            #print(person, x)
                            if len(v) >= 7 and (person.lower() == x.lower() or person.lower() in x.lower() or x.lower() in person.lower()):
                                personq = q.title()
                    for k, v in q.labels.items():
                        #print(person, v)
                        if len(v) >= 7 and (person.lower() == v.lower() or person.lower() in v.lower() or v.lower() in person.lower()):
                            personq = q.title()
            if personq and not personq in personsq:
                personsq.append(personq)
    personsq = list(set(personsq))
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

def searchInWikidata(s="", l=[]):
    candidates = []
    if not s and not l:
        return candidates
    lang = "en"
    #searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=%s&format=xml' % (urllib.parse.quote(s), lang)
    if s:
        print("\nSearching in Wikidata", s)
        searchitemurl = 'https://www.wikidata.org/w/index.php?go=Go&search=%s' % (urllib.parse.quote(s))
    elif l:
        l2 = []
        for ll in l:
            if ll:
                l2.append(ll)
        l = l2
        ss = " OR ".join(['"%s"' % (x) for x in l])
        print("\nSearching in Wikidata", ss)
        searchitemurl = 'https://www.wikidata.org/w/index.php?go=Go&search=%s' % (urllib.parse.quote(ss))
    else:
        return candidates
    print(searchitemurl)
    raw = getURL(url=searchitemurl)
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
    today = datetime.date.today()
    year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    overwrite = False
    overwritelabels = overwrite
    overwritedescriptions = overwrite
    overwritealiases = overwrite
    if item:
        workitem = pywikibot.ItemPage(repo, item)
    else:
        workitemlabels = { props["lang"]: props["fulltitle"] }
        workitem = pywikibot.ItemPage(repo)
        workitem.editLabels(labels=workitemlabels, summary="BOT - Creating item")
    workitem.get()
    #labels
    if overwritelabels or not props["lang"] in workitem.labels or not "en" in workitem.labels:
        print("Añadiendo labels")
        labels = workitem.labels
        labels[props["lang"]] = props["fulltitle"]
        workitem.editLabels(labels=labels, summary="BOT - Adding labels (1 languages): %s" % (props["lang"]))
        if props["lang"] != "en":
            labels["en"] = props["fulltitle"]
            workitem.editLabels(labels=labels, summary="BOT - Adding labels (1 languages): en")
    else:
        print("Ya tiene labels")
    #descs
    if overwritedescriptions or not props["lang"] in workitem.descriptions or not "en" in workitem.descriptions or not "fr" in workitem.descriptions or not "ca" in workitem.descriptions or not "gl" in workitem.descriptions:
        print("Añadiendo descripciones")
        authoritem = pywikibot.ItemPage(repo, props["authorq"])
        authoritem.get()
        authornamees = "es" in authoritem.labels and authoritem.labels["es"] or props["authorname"]
        authornameen = "en" in authoritem.labels and authoritem.labels["en"] or authornamees
        authornamefr = "fr" in authoritem.labels and authoritem.labels["fr"] or authornamees
        authornameca = "ca" in authoritem.labels and authoritem.labels["ca"] or authornamees
        authornamegl = "gl" in authoritem.labels and authoritem.labels["gl"] or authornamees
        if p31 == "work":
            descriptions = workitem.descriptions
            descriptions["es"] = "obra escrita" + (authornamees and " por %s" % (authornamees) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): es")
            descriptions["en"] = "written work" + (authornameen and " by %s" % (authornameen) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): en")
            descriptions["fr"] = "ouvrage écrit" + (authornamefr and " par %s" % (authornamefr) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): fr")
            descriptions["ca"] = "obra escrita" + (authornameca and " per %s" % (authornameca) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): ca")
            descriptions["gl"] = "obra escrita" + (authornamegl and " por %s" % (authornamegl) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): gl")
        if p31 == "edition":
            descriptions = workitem.descriptions
            descriptions["es"] = "edición" + (props["publicationdate"] and " publicada en %s" % (props["publicationdate"])) + (authornamees and " de la obra escrita por %s" % (authornamees) or "")
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): es")
            descriptions["en"] = (props["publicationdate"] and "%s " % (props["publicationdate"])) + "edition" + (authornameen and " of written work by %s" % (authornameen) or "") 
            workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): en")
    else:
        print("Ya tiene descripciones")
    #aliases
    if props["alternatetitles"]:
        if overwritealiases:
            workitem.aliases = {}
        for alternatetitle in props["alternatetitles"]:
            if alternatetitle != props["title"]:
                if "es" in workitem.aliases and not alternatetitle in workitem.aliases["es"]:
                    aliases = workitem.aliases
                    aliases["es"].append(alternatetitle)
                    workitem.editAliases(aliases=aliases, summary="BOT - Adding 1 aliases (es): %s" % (alternatetitle))
                if not "es" in workitem.aliases:
                    aliases = workitem.aliases
                    aliases["es"] = [alternatetitle]
                    workitem.editAliases(aliases=aliases, summary="BOT - Adding 1 aliases (es): %s" % (alternatetitle))
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
    if p31: #los contributor los metemos en work y en edition
        if props["contributorsq"]:
            for contributorq in props["contributorsq"]:
                if contributorq == props["authorq"] or contributorq in props["translatorsq"] or contributorq in props["forewordsq"]:
                    #no meter al autor, traductor, prologador como contributor de nuevo
                    continue
                if not "P767" in workitem.claims or not contributorq in [x.getTarget().title() for x in workitem.claims["P767"]]:
                    print("Añadiendo P767")
                    claim = pywikibot.Claim(repo, 'P767')
                    target = pywikibot.ItemPage(repo, contributorq)
                    claim.setTarget(target)
                    workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                    addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
                else:
                    print("Ya tiene P767")
        
    #P655 = translator
    if p31 == "edition": #el traductor depende de la edicion
        if props["translatorsq"]:
            for translatorq in props["translatorsq"]:
                if not "P655" in workitem.claims or not translatorq in [x.getTarget().title() for x in workitem.claims["P655"]]:
                    print("Añadiendo P655")
                    claim = pywikibot.Claim(repo, 'P655')
                    target = pywikibot.ItemPage(repo, translatorq)
                    claim.setTarget(target)
                    workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                    addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
                else:
                    print("Ya tiene P655")
        
    #P2679 = author of foreword
    if p31 == "edition": #el prologo depende de la edicion
        if props["forewordsq"]:
            for forewordq in props["forewordsq"]:
                #if contributorq == props["authorq"]: #un autor puede prologar su propia obra, no descartar con este if
                #    continue
                if not "P2679" in workitem.claims or not forewordq in [x.getTarget().title() for x in workitem.claims["P2679"]]:
                    print("Añadiendo P2679")
                    claim = pywikibot.Claim(repo, 'P2679')
                    target = pywikibot.ItemPage(repo, forewordq)
                    claim.setTarget(target)
                    workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                    addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
                else:
                    print("Ya tiene P2679")
    
    #P1476 = title
    if p31:
        if props["title"]:
            if not "P1476" in workitem.claims:
                print("Añadiendo P1476")
                claim = pywikibot.Claim(repo, 'P1476')
                target = pywikibot.WbMonolingualText(text=props["title"], language=props["lang"])
                claim.setTarget(target)
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P1476")
    #P1680 = subtitle
    if p31:
        if props["subtitle"]:
            if not "P1680" in workitem.claims:
                print("Añadiendo P1680")
                claim = pywikibot.Claim(repo, 'P1680')
                target = pywikibot.WbMonolingualText(text=props["subtitle"], language=props["lang"])
                claim.setTarget(target)
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P1680")
    #P407 = language of work
    if p31 == "edition": #en las ediciones si te indica el idioma, pero en las obras no, no podemos presuponer q siempre será español o q coincidirá con el idioma de la edición, además cuál edición? en todo caso la primera por fecha...
        if props["lang"]:
            if not "P407" in workitem.claims:
                print("Añadiendo P407")
                claim = pywikibot.Claim(repo, 'P407')
                target = pywikibot.ItemPage(repo, languages[props["lang"]])
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
    #P2048 = height
    if p31 == "edition":
        if props["height"]:
            if not "P2048" in workitem.claims:
                print("Añadiendo P2048")
                claim = pywikibot.Claim(repo, 'P2048')
                unit = pywikibot.ItemPage(repo, "Q174728")
                claim.setTarget(pywikibot.WbQuantity(amount=props["height"], unit=unit)) #Q174728 cm
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P2048")
    #P437 = distribution format
    if p31 == "edition":
        if props["distributionformat"]:
            if not "P437" in workitem.claims:
                print("Añadiendo P437")
                claim = pywikibot.Claim(repo, 'P437')
                target = pywikibot.ItemPage(repo, props["distributionformat"])
                claim.setTarget(target)
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P437")
    
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

def linkWorkAndEdition(repo="", workq="", editionq=""):
    if not repo or not workq or not editionq:
        return
    
    print("\nIntentando enlazar work", workq, "con edition", editionq)
    editionitem = pywikibot.ItemPage(repo, editionq)
    editionitem.get()
    resourceid = "" #use edition bneid for both properties P629 and P747
    resourcelang = ""
    resourceyear = ""
    if "P950" in editionitem.claims:
        resourceid = editionitem.claims["P950"][0].getTarget()
    else:
        return
    if "P407" in editionitem.claims:
        resourcelang = editionitem.claims["P407"][0].getTarget().title()
    else:
        return
    if "P577" in editionitem.claims:
        resourceyear = editionitem.claims["P577"][0].getTarget().year
    else:
        return
    workitem = pywikibot.ItemPage(repo, workq)
    workitem.get()
    
    #add work to edition
    if not "P629" in editionitem.claims:
        print("Añadiendo P629")
        claim = pywikibot.Claim(repo, 'P629')
        claim.setTarget(workitem)
        editionitem.addClaim(claim, summary='BOT - Adding 1 claim')
        addBNERef(repo=repo, claim=claim, bneid=resourceid)
    else:
        print("Ya tiene P629")
    
    #add edition to work
    if not "P747" in workitem.claims or not editionq in [x.getTarget().title() for x in workitem.claims["P747"]]:
        print("Añadiendo P747")
        claim = pywikibot.Claim(repo, 'P747')
        claim.setTarget(editionitem)
        workitem.addClaim(claim, summary='BOT - Adding 1 claim')
        
        qualifierlang = pywikibot.Claim(repo, "P407")
        qualifierlang.setTarget(pywikibot.ItemPage(repo, resourcelang))
        workitem.claims["P747"][-1].addQualifier(qualifierlang, summary="BOT - Adding 1 qualifier")
        
        qualifieryear = pywikibot.Claim(repo, "P577")
        qualifieryear.setTarget(pywikibot.WbTime(year=resourceyear))
        workitem.claims["P747"][-1].addQualifier(qualifieryear, summary="BOT - Adding 1 qualifier")
        
        addBNERef(repo=repo, claim=claim, bneid=resourceid)
    else:
        print("Ya tiene P747")
    
    return

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
        m = re.findall(r"(?im)<ns\d:P50102>(%s)</ns\d:P50102>" % ("|".join(languages.keys())), rawrdf)
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
        
        if (not birthdate and not deathdate) or (birthdate and birthdate < 1900) or (deathdate and deathdate < 1970):
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
            
            m = re.findall(r"(?im)<ns\d:language rdf:resource=\"https?://id\.loc\.gov/vocabulary/languages/([^<>]+?)\"\s*/>", rawresource)
            lang = m and unquote(m[0]) or ""
            if not lang in languages2iso:
                print("Idioma no entendido", lang, "saltamos")
                continue
            m = re.findall(r"(?im)<ns\d:P3002>([^<>]+?)</ns\d:P3002>", rawresource)
            title_ = m and unquote(m[0]) or "" #se usa para el fulltitle
            title_ = title_.replace(" : ", ": ")
            title = title_.strip(" ").strip(".").strip(":").strip(",").strip(" ") #no usar clearsymbols pq puede quitar (), solo quitar ,.: finales si hay
            m = re.findall(r"(?im)<ns\d:P3014>([^<>]+?)</ns\d:P3014>", rawresource)
            subtitle = m and unquote(m[0]) or ""
            subtitle = subtitle and (subtitle[0].upper() + subtitle[1:]) or ""
            subtitle = subtitle.replace(" : ", ": ")
            alternatetitle = title + " " + subtitle
            alternatetitle2 = alternatetitle.replace(" : ", ": ")
            alternatetitle3 = alternatetitle.replace(" : ", ", ")
            alternatetitle4 = alternatetitle.replace(" : ", " ")
            alternatetitles = list(set([alternatetitle, alternatetitle2, alternatetitle3, alternatetitle4]))
            fulltitle = getFullTitle(title=title_, subtitle=subtitle)
            
            m = re.findall(r"(?im)<ns\d:P3008>([^<>]+?)</ns\d:P3008>", rawresource)
            contributors = m and unquote(m[0]) or ""
            #if not contributors:
            #    print("No info de contributor, saltamos")
            #    continue
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
            if pages < 80 or pages > 999:
                print("Numero de paginas raro, saltamos", pages)
                continue
            m = re.findall(r"(?im)<ns\d:P3007>([^<>]+?)</ns\d:P3007>", rawresource)
            dimensions = m and unquote(m[0]) or ""
            height = getHeightInCM(s=dimensions)
            if height < 10 or height > 35:
                print("Altura extraña, saltamos", height)
                height = ""
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
            distributionformat = ""
            if re.search(r"(?im)(e[ -]?book|elec|cd|dvd|disco|rom|dig|comp|ord|internet|web|recu|l[ií]nea|plano|foto|mapa|cartel|case|nega|partitura|mina|hoja|online|micro|v[íi]deo|sono|carpe|carta|piano|rollo)", extension+mediatype):
                print("Extension/Medio no interesa, skiping", extension+mediatype)
                continue
            else:
                distributionformat = "Q11396303" #printed book
            
            #external ids
            goodreadsworkid = getGoodReadsWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            openlibraryworkid = getOpenLibraryWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            
            goodreadseditionid = getGoodReadsEditionId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            openlibraryeditionid = getOpenLibraryEditionId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            
            props = {
                "lang": languages2iso[lang], 
                "langq": languages[languages2iso[lang]], 
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
                "height": height, 
                "distributionformat": distributionformat,
                
                "publisher": publisher, 
                "publicationlocation": publicationlocation, 
                "publicationdate": publicationdate, 
                
                "isbn": isbn, 
                "isbnplain": isbnplain, 
                "isbn10": isbn10, 
                "isbn13": isbn13, 
                "legaldeposit": legaldeposit, 
                
                "goodreadsworkid": goodreadsworkid, 
                "openlibraryworkid": openlibraryworkid, 
                
                "goodreadseditionid": goodreadseditionid, 
                "openlibraryeditionid": openlibraryeditionid, 
            }
            print(props.items())
            
            donecandidates = []
            candidates = searchInWikidata(l=[isbn, isbnplain, isbn10, isbn13, resourceid, goodreadsworkid, openlibraryworkid, goodreadseditionid, openlibraryeditionid, fulltitle])
            candidates = list(set(candidates))
            candidates.sort()
            #print(candidates)
            
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
                linkWorkAndEdition(repo=repo, workq=workq, editionq=editionq)
                pass
            if len(workcreated) == 1 and len(editionscreated) >= 1:
                for editioncreated in editionscreated:
                    linkWorkAndEdition(repo=repo, workq=workcreated[0], editionq=editioncreated)
            
            #if resourceid in ["a7153685", "a5311062"]:
            #    sys.exit()

if __name__ == "__main__":
    main()
