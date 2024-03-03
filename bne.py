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
publishers = {
    "aconcagua": "Q124731301",
    "crítica": "Q5818611",
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
    pages = ""
    if re.search(r"(?im)(\d+) (?:pg?s?|p[aá]gs?|páginas?)\.?", s):
        pages = re.findall(r"(?im)(\d+) (?:pg?s?|p[aá]gs?|páginas?)\.?", s)[0]
    return pages

def getPublicationDate(s=""):
    if not s:
        return 
    for i in range(20):
        s = s.strip()
        s = s.strip(",")
        s = s.strip(" ")
        s = s.strip("[")
        s = s.strip("]")
        s = s.strip(".")
    if len(s) != 4 or not re.search(r"(?im)^[12]", s):
        return 
    return int(s)

def getPublisher(s=""):
    if not s:
        return
    for i in range(20):
        s = s.strip()
        s = s.strip(",")
        s = s.strip(" ")
        s = s.strip("[")
        s = s.strip("]")
        s = s.strip(".")
    if re.search(r"(?im)^(ed\.?|editorial)? ?(cr[íi]tica)$", s):
        return "crítica"
    elif re.search(r"(?im)^(ed\.?|editorial)? ?(aconcagua) ?(libros?)?$", s):
        return "aconcagua"
    return

def existsInWikidata(s=""):
    if not s:
        return
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

def improveWork(item="", repo="", title="", alternatetitles=[], authorq="", publicationdate="", authorbneid="", goodreadsworkid="", openlibraryworkid=""):
    if item:
        site = pywikibot.Site('wikidata', 'wikidata')
        itempage = pywikibot.Page(site, item)
        history = itempage.getVersionHistoryTable(reverse=True, total=1)
        #print(history)
        if not "Emijrpbot" in history:
            print("No creado por mi bot, saltando...")
            return
    return createWork(item=item, repo=repo, title=title, alternatetitles=alternatetitles, authorq=authorq, publicationdate=publicationdate, authorbneid=authorbneid, goodreadsworkid=goodreadsworkid, openlibraryworkid=openlibraryworkid)

def createWork(item="", repo="", title="", alternatetitles=[], authorq="", publicationdate="", authorbneid="", goodreadsworkid="", openlibraryworkid=""):
    if not repo or not title or not authorq or not authorbneid:
        return
    lang = "es"
    today = datetime.date.today()
    year, month, day = [int(today.strftime("%Y")), int(today.strftime("%m")), int(today.strftime("%d"))]
    if item:
        workitem = pywikibot.ItemPage(repo, item)
    else:
        workitemlabels = { lang: title }
        workitem = pywikibot.ItemPage(repo)
        workitem.editLabels(labels=workitemlabels, summary="BOT - Creating item")
    workitem.get()
    #labels
    if not lang in workitem.labels:
        print("Añadiendo labels")
        labels = workitem.labels
        labels[lang] = title
        workitem.editLabels(labels=labels, summary="BOT - Adding labels (1 languages): %s" % (lang))
    else:
        print("Ya tiene labels")
    #descs
    if not lang in workitem.descriptions or not "en" in workitem.descriptions or not "fr" in workitem.descriptions or not "ca" in workitem.descriptions or not "gl" in workitem.descriptions:
        authoritem = pywikibot.ItemPage(repo, authorq)
        authoritem.get()
        authorname = lang in authoritem.labels and authoritem.labels[lang] or ""
        authornameen = "en" in authoritem.labels and authoritem.labels["en"] or authorname
        authornamefr = "fr" in authoritem.labels and authoritem.labels["fr"] or authornameen
        authornameca = "ca" in authoritem.labels and authoritem.labels["ca"] or authornameen
        authornamegl = "gl" in authoritem.labels and authoritem.labels["gl"] or authornameen
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
    else:
        print("Ya tiene descripciones")
    #aliases
    if alternatetitles:
        for alternatetitle in alternatetitles:
            if alternatetitle != title:
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
    if not "P31" in workitem.claims:
        print("Añadiendo P31")
        claim = pywikibot.Claim(repo, 'P31')
        target = pywikibot.ItemPage(repo, 'Q47461344')
        claim.setTarget(target)
        workitem.addClaim(claim, summary='BOT - Adding 1 claim')
        addBNERef(repo=repo, claim=claim, bneid=authorbneid)
    else:
        print("Ya tiene P31")
    #P50 = authorq
    if not "P50" in workitem.claims:
        print("Añadiendo P50")
        claim = pywikibot.Claim(repo, 'P50')
        target = pywikibot.ItemPage(repo, authorq)
        claim.setTarget(target)
        workitem.addClaim(claim, summary='BOT - Adding 1 claim')
        addBNERef(repo=repo, claim=claim, bneid=authorbneid)
    else:
        print("Ya tiene P50")
    #P1476 = title
    if not "P1476" in workitem.claims:
        print("Añadiendo P1476")
        claim = pywikibot.Claim(repo, 'P1476')
        target = pywikibot.WbMonolingualText(text=title, language=lang)
        claim.setTarget(target)
        workitem.addClaim(claim, summary='BOT - Adding 1 claim')
        addBNERef(repo=repo, claim=claim, bneid=authorbneid)
    else:
        print("Ya tiene P1476")
    #P407 = language of work
    if not "P407" in workitem.claims:
        print("Añadiendo P407")
        claim = pywikibot.Claim(repo, 'P407')
        target = pywikibot.ItemPage(repo, languages[lang])
        claim.setTarget(target)
        workitem.addClaim(claim, summary='BOT - Adding 1 claim')
        addBNERef(repo=repo, claim=claim, bneid=authorbneid)
    else:
        print("Ya tiene P407")
    #P577 = publication date
    if publicationdate > 1950 and publicationdate <= year and not "P577" in workitem.claims:
        print("Añadiendo P577")
        claim = pywikibot.Claim(repo, 'P577')
        claim.setTarget(pywikibot.WbTime(year=publicationdate))
        workitem.addClaim(claim, summary='BOT - Adding 1 claim')
        addBNERef(repo=repo, claim=claim, bneid=authorbneid)
    else:
        print("Ya tiene P407")
    
    #more ideas
    #country of origin	P495
    #contributor to the creative work or subject	P767, mejor no, puede variar con la edición (los que prologan, etc)
    
    #P8383 = goodreads work id
    if goodreadsworkid:
        if not "P8383" in workitem.claims:
            print("Añadiendo P8383")
            claim = pywikibot.Claim(repo, 'P8383')
            claim.setTarget(goodreadsworkid)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addGoodReadsRef(repo=repo, claim=claim)
        else:
            print("Ya tiene P8383")
    
    #P648 = openlibrary work id
    if openlibraryworkid:
        if not "P648" in workitem.claims:
            print("Añadiendo P648")
            claim = pywikibot.Claim(repo, 'P648')
            claim.setTarget(openlibraryworkid)
            workitem.addClaim(claim, summary='BOT - Adding 1 claim')
            addOpenLibraryRef(repo=repo, claim=claim)
        else:
            print("Ya tiene P648")

def getGoodReadsWorkId(title="", isbn10="", isbn13=""):
    #<a class="DiscussionCard" href="https://www.goodreads.com/work/quotes/97295167">
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = ""
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
            
def getOpenLibraryWorkId(title="", isbn10="", isbn13=""):
    #<input type="hidden" name="work_id" value="/works/OL28180208W"/>
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = ""
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

def unquote(s=""):
    s = urllib.parse.unquote_plus(s)
    s = html.unescape(s)
    return s

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    qlist = ["Q93433647"]
    qlist = ["Q5865630"]
    
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
        label = m and m[0] or ""
        m = re.findall(r"(?im)<ns\d:P50116>(Masculino|Femenino)</ns\d:P50116>", rawrdf)
        gender = m and genders[m[0].lower()] or ""
        m = re.findall(r"(?im)<ns\d:P5024>https?://isni\.org/isni/(\d+)/?</ns\d:P5024>", rawrdf)
        isniid = m and m[0] or ""
        m = re.findall(r"(?im)<ns\d:P5024>https?://viaf\.org/viaf/(\d+)/?</ns\d:P5024>", rawrdf)
        viafid = m and m[0] or ""
        m = re.findall(r"(?im)<ns\d:P50102>(Español|Inglés)</ns\d:P50102>", rawrdf)
        language = m and languages[m[0].lower()] or ""
        m = re.findall(r"(?im)<ns\d:P50119>([^<>]*?)</ns\d:P50119>", rawrdf)
        birthplace = m and m[0] or ""
        
        print(label)
        print(gender, language, birthplace)
        print(isniid, viafid)
        
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
            
            m = re.findall(r"(?im)<ns\d:P3001>([^<>]+?)</ns\d:P3001>", rawresource)
            publisher = m and getPublisher(s=unquote(m[0])) or ""
            m = re.findall(r"(?im)<ns\d:P3006>([^<>]+?)</ns\d:P3006>", rawresource)
            publicationdate = m and getPublicationDate(s=unquote(m[0])) or ""
            m = re.findall(r"(?im)<ns\d:P3017>([^<>]+?)</ns\d:P3017>", rawresource)
            edition = m and unquote(m[0]) or ""
            m = re.findall(r"(?im)<ns\d:P3004>([^<>]+?)</ns\d:P3004>", rawresource)
            extension = m and unquote(m[0]) or ""
            pages = getExtensionInPages(s=extension)
            m = re.findall(r"(?im)<ns\d:P3013>([^<>]+?)</ns\d:P3013>", rawresource)
            isbn = m and unquote(m[0]) or ""
            isbnplain = isbn and isbn.replace("-", "") or ""
            isbn10 = ""
            isbn13 = ""
            if len(isbnplain) == 10:
                isbn10 = isbnplain
            if len(isbnplain) == 13:
                isbn13 = isbnplain
            m = re.findall(r"(?im)<ns\d:P3009>([^<>]+?)</ns\d:P3009>", rawresource)
            legaldeposit = m and getLegalDeposit(s=unquote(m[0])) or ""
            m = re.findall(r"(?im)<ns\d:P3062>([^<>]+?)</ns\d:P3062>", rawresource)
            mediatype = m and unquote(m[0]) or ""
            if re.search(r"(?im)(elec|cd|dvd|rom|dig|comp|ord|internet|web|recu|l[ií]nea)", edition+extension+mediatype):
                print("Edicion/Extension/Medio electrónico, skiping", edition+extension+mediatype)
                continue
            
            #external ids
            #<a class="DiscussionCard" href="https://www.goodreads.com/work/quotes/97295167">
            goodreadsworkid = getGoodReadsWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            openlibraryworkid = getOpenLibraryWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
            
            print("title", title)
            print("subtitle", subtitle)
            print("alternatetitle", alternatetitle)
            print("fulltitle", fulltitle)
            print("pages", pages)
            print("publisher", publisher)
            print("publicationdate", publicationdate)
            print("isbn", isbn)
            print("isbnplain", isbnplain)
            print("legaldeposit", legaldeposit)
            print("goodreadsworkid", goodreadsworkid)
            print("openlibraryworkid", openlibraryworkid)
            
            for method in ["isbn", "isbn10", "isbn13", "goodreadsworkid", "openlibraryworkid", "fulltitle"]:
                candidates = ""
                if method == "isbn":
                    candidates = existsInWikidata(s=isbn)
                elif method == "isbn10":
                    candidates = existsInWikidata(s=isbn10)
                elif method == "isbn13":
                    candidates = existsInWikidata(s=isbn13)
                elif method == "goodreadsworkid":
                    candidates = existsInWikidata(s=goodreadsworkid)
                elif method == "openlibraryworkid":
                    candidates = existsInWikidata(s=openlibraryworkid)
                elif method == "fulltitle":
                    candidates = existsInWikidata(s=fulltitle)
                if candidates:
                    #comprobar si lo cree yo y es una edicion o un work, entonces mejorar
                    for candidate in candidates:
                        print("Encontrado candidato, ", candidate)
                        candidateitem = pywikibot.ItemPage(repo, candidate)
                        candidateitem.get()
                        if "P31" in candidateitem.claims:
                            for candidateitemp31 in candidateitem.claims["P31"]:
                                if "Q47461344" in candidateitemp31.getTarget().title(): #work
                                    improveWork(item=candidates[0], repo=repo, title=fulltitle, alternatetitles=alternatetitles, authorq=authorq, publicationdate=publicationdate, authorbneid=authorbneid, goodreadsworkid=goodreadsworkid, openlibraryworkid=openlibraryworkid)
                                elif "Q3331189" in candidateitemp31.getTarget().title(): #edition
                                    pass
                    break
                
            if not candidates:
                print("No se encontraron candidatos, saltamos")
                #crear ya que no existe
                #workq = createWork(repo=repo, title=fulltitle, alternatetitles=alternatetitles, authorq=authorq, publicationdate=publicationdate, authorbneid=authorbneid, goodreadsworkid=goodreadsworkid, openlibraryworkid=openlibraryworkid)
                #editionq = createEdition(repo=repo, title=fulltitle, alternatetitles=alternatetitles, authorq=authorq, publicationdate=publicationdate, authorbneid=authorbneid, publisher=publisher, publicationdate=publicationdate, pages=pages, isbn10=isbn10, isbn13=isbn13, legaldeposit=legaldeposit)
                #linkWorkAndEdition(workq=workq, editionq=editionq)
                sys.exit()

if __name__ == "__main__":
    main()
