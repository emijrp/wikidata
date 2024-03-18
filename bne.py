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
import random
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

usedisbns = []
usedlegaldeposits = []
usedlabelsdescspairs = []
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
    "alemania": { "q": "Q183" }, 
    "argentina": { "q": "Q414" }, 
    "españa": { "q": "Q29" }, 
    "estados unidos": { "q": "Q30" }, 
    "francia": { "q": "Q142" }, 
    "italia": { "q": "Q220" }, 
    "méxico": { "q": "Q96" }, 
    "portugal": { "q": "Q45" }, 
    "reino unido": { "q": "Q145" }, 
    "venezuela": { "q": "Q717" }, 
}
locations = {
    
    "alemania": { "q": countries["alemania"]["q"], "country": countries["alemania"]["q"], "regexp": r"(alemania|germany)" }, 
        "leipzig": { "q": "Q2079", "country": countries["alemania"]["q"], "regexp": r"leipzig" }, 
    
    "argentina": { "q": countries["argentina"]["q"], "country": countries["argentina"]["q"], "regexp": r"argentina" }, 
        "buenos aires": { "q": "Q1486", "country": countries["argentina"]["q"], "regexp": r"buenos aires" }, 
    
    "españa": { "q": countries["españa"]["q"], "country": countries["españa"]["q"], "regexp": r"españa" }, 
        "a coruna": { "q": "Q8757", "country": countries["españa"]["q"], "regexp": r"l?a coru[ñn]a" }, 
        "albacete": { "q": "Q15095", "country": countries["españa"]["q"], "regexp": r"albacete" }, 
        "alicante": { "q": "Q11959", "country": countries["españa"]["q"], "regexp": r"alicante" }, 
        "almeria": { "q": "Q10400", "country": countries["españa"]["q"], "regexp": r"almer[íi]a" }, 
        "avila": { "q": "Q15688", "country": countries["españa"]["q"], "regexp": r"[áa]vila" }, 
        "badajoz": { "q": "Q15679", "country": countries["españa"]["q"], "regexp": r"badajoz" }, 
        "barcelona": { "q": "Q1492", "country": countries["españa"]["q"], "regexp": r"barcelona" }, 
        "bilbao": { "q": "Q8692", "country": countries["españa"]["q"], "regexp": r"bilbao" }, 
        "burgos": { "q": "Q9580", "country": countries["españa"]["q"], "regexp": r"burgos" }, 
        "caceres": { "q": "Q15678", "country": countries["españa"]["q"], "regexp": r"c[áa]ceres" }, 
        "cadiz": { "q": "Q15682", "country": countries["españa"]["q"], "regexp": r"c[áa]diz" }, 
        "castellon de la plana": { "q": "Q15092", "country": countries["españa"]["q"], "regexp": r"castell[óo]n de la plana" }, 
        "ciudad real": { "q": "Q15093", "country": countries["españa"]["q"], "regexp": r"ciudad real" }, 
        "cordoba": { "q": "Q5818", "country": countries["españa"]["q"], "regexp": r"c[óo]rdoba" }, 
        "cuenca": { "q": "Q15098", "country": countries["españa"]["q"], "regexp": r"cuenca" }, 
        "el ejido": { "q": "Q493933", "country": countries["españa"]["q"], "regexp": r"El Ejido" }, 
        "el puerto de santa maria": { "q": "Q203040", "country": countries["españa"]["q"], "regexp": r"((El )?Puerto de Santa Mar[íi]a)(, C[áa]diz)?" }, 
        "girona": { "q": "Q7038", "country": countries["españa"]["q"], "regexp": r"g[ie]rona" }, 
        "granada": { "q": "Q8810", "country": countries["españa"]["q"], "regexp": r"granada" }, 
        "guadalajara": { "q": "Q11953", "country": countries["españa"]["q"], "regexp": r"guadalajara" }, 
        "huelva": { "q": "Q12246", "country": countries["españa"]["q"], "regexp": r"huelva" }, 
        "huesca": { "q": "Q11967", "country": countries["españa"]["q"], "regexp": r"huesca" }, 
        "humanes de madrid": { "q": "Q281632", "country": countries["españa"]["q"], "regexp": r"Humanes de Madrid" }, 
        "jaen": { "q": "Q15681", "country": countries["españa"]["q"], "regexp": r"ja[ée]n" }, 
        "las palmas de gran canaria": { "q": "Q11974", "country": countries["españa"]["q"], "regexp": r"(Las )?Palmas de Gran Canaria" }, 
        "leon": { "q": "Q15699", "country": countries["españa"]["q"], "regexp": r"le[óo]n" }, 
        "lleida": { "q": "Q15090", "country": countries["españa"]["q"], "regexp": r"(lleida|l[ée]rida)" }, 
        "logrono": { "q": "Q14325", "country": countries["españa"]["q"], "regexp": r"logro[ñn]o" }, 
        "lugo": { "q": "Q11125", "country": countries["españa"]["q"], "regexp": r"lugo" }, 
        "malaga": { "q": "Q8851", "country": countries["españa"]["q"], "regexp": r"m[áa]laga" }, 
        "murcia": { "q": "Q12225", "country": countries["españa"]["q"], "regexp": r"murcia" }, 
        "ourense": { "q": "Q99151", "country": countries["españa"]["q"], "regexp": r"ou?rense" }, 
        "oviedo": { "q": "Q14317", "country": countries["españa"]["q"], "regexp": r"oviedo" }, 
        "palencia": { "q": "Q8378", "country": countries["españa"]["q"], "regexp": r"palencia" }, 
        "palma de mallorca": { "q": "Q8826", "country": countries["españa"]["q"], "regexp": r"Palma de Mallorca" }, 
        "pamplona": { "q": "Q10282", "country": countries["españa"]["q"], "regexp": r"pamplona" }, 
        "pontevedra": { "q": "Q12411", "country": countries["españa"]["q"], "regexp": r"pontevedra" }, 
        "roquetas de mar": { "q": "Q499184", "country": countries["españa"]["q"], "regexp": r"Roquetas de Mar" }, 
        "rota": { "q": "Q15907", "country": countries["españa"]["q"], "regexp": r"(rota)(, C[áa]diz)?" }, 
        "salamanca": { "q": "Q15695", "country": countries["españa"]["q"], "regexp": r"salamanca" }, 
        "santander": { "q": "Q12233", "country": countries["españa"]["q"], "regexp": r"santander" }, 
        "san sebastian": { "q": "Q10313", "country": countries["españa"]["q"], "regexp": r"san sebasti[áa]n" }, 
        "santa cruz de tenerife": { "q": "Q14328", "country": countries["españa"]["q"], "regexp": r"santa cruz de tenerife" }, 
        "santiago de compostela": { "q": "Q14314", "country": countries["españa"]["q"], "regexp": r"Santiago de Compostela" }, 
        "segovia": { "q": "Q15684", "country": countries["españa"]["q"], "regexp": r"segovia" }, 
        "sevilla": { "q": "Q8717", "country": countries["españa"]["q"], "regexp": r"sevilla" }, 
        "soria": { "q": "Q12155", "country": countries["españa"]["q"], "regexp": r"soria" }, 
        "tarragona": { "q": "Q15088", "country": countries["españa"]["q"], "regexp": r"tarragona" }, 
        "teruel": { "q": "Q14336", "country": countries["españa"]["q"], "regexp": r"teruel" }, 
        "toledo": { "q": "Q5836", "country": countries["españa"]["q"], "regexp": r"toledo" }, 
        "valencia": { "q": "Q8818", "country": countries["españa"]["q"], "regexp": r"val[èe]ncia" }, 
        "valladolid": { "q": "Q8356", "country": countries["españa"]["q"], "regexp": r"valladolid" }, 
        "vigo": { "q": "Q8745", "country": countries["españa"]["q"], "regexp": r"vigo" }, 
        "vitoria": { "q": "Q14318", "country": countries["españa"]["q"], "regexp": r"vitoria(-?gasteiz)?" }, 
        "zamora": { "q": "Q15696", "country": countries["españa"]["q"], "regexp": r"zamora" }, 
        "zaragoza": { "q": "Q10305", "country": countries["españa"]["q"], "regexp": r"zaragoza" }, 
    
    "estados unidos": { "q": countries["estados unidos"]["q"], "country": countries["estados unidos"]["q"], "regexp": r"(estados unidos|united states)" },
        "nueva york": { "q": "Q60", "country": countries["estados unidos"]["q"], "regexp": r"(new york|nueva york)" },
     
    "francia": { "q": countries["francia"]["q"], "country": countries["francia"]["q"], "regexp": r"(francia|france)" }, 
        "parís": { "q": "Q90", "country": countries["francia"]["q"], "regexp": r"par[íi]s" }, 
    
    "italia": { "q": countries["italia"]["q"], "country": countries["italia"]["q"], "regexp": r"(italia|italy)" }, 
        "roma": { "q": "Q220", "country": countries["italia"]["q"], "regexp": r"rom[ae]" }, 
    
    "méxico": { "q": countries["méxico"]["q"], "country": countries["méxico"]["q"], "regexp": r"m[ée][xj]ico" }, 
    
    "portugal": { "q": countries["portugal"]["q"], "country": countries["portugal"]["q"], "regexp": r"portugal" }, 
        "lisboa": { "q": "Q597", "country": countries["portugal"]["q"], "regexp": r"lisboa" }, 
    
    "reino unido": { "q": countries["reino unido"]["q"], "country": countries["reino unido"]["q"], "regexp": r"reino unido" }, 
        "londres": { "q": "Q84", "country": countries["reino unido"]["q"], "regexp": r"(londres|london)" }, 
    
    "venezuela": { "q": countries["venezuela"]["q"], "country": countries["venezuela"]["q"], "regexp": r"venezuela" }, 
        "caracas": { "q": "Q1533", "country": countries["venezuela"]["q"], "regexp": r"caracas" }, 
    
}
for location, props in locations.items():
    locations[location]["regexp"] = r"(?im)^[ \.\,\[\]\(\)]*(?:en )?(%s)[ \.\,\[\]\(\)]*$" % (locations[location]["regexp"])

publishers = {
    "aconcagua": { "q": "Q124731301", "regexp": r"aconcagua" }, 
    "akal": { "q": "Q5817833", "regexp": r"akal" }, 
    "alfaguara": { "q": "Q3324371", "regexp": r"alfaguara" }, 
    "alianza editorial": { "q": "Q8195536", "regexp": r"alianza editorial" }, 
    "altaya": { "q": "Q124796624", "regexp": r"altaya" }, 
    "anagrama": { "q": "Q8772125", "regexp": r"anagrama" }, 
    "anaya": { "q": "Q5394209", "regexp": r"anaya" }, 
    "atrapasueños": { "q": "Q124898383", "regexp": r"atrapasue[ñn]os" }, 
    "booket": { "q": "Q124796493", "regexp": r"booket" }, 
    "bruguera": { "q": "Q3275000", "regexp": r"bruguera" }, 
    "catedra": { "q": "Q3009634", "regexp": r"c[áa]tedra" }, 
    "círculo de lectores": { "q": "Q45762085", "regexp": "c[íi]rculo de lectores" }, 
    "círculo rojo": { "q": "Q5818613", "regexp": "c[íi]rculo rojo" }, 
    "crítica": { "q": "Q5818611", "regexp": "cr[íi]tica" }, 
    "debolsillo": { "q": "Q30103625", "regexp": "de[ -]?bolsillo" }, 
    "destino": { "q": "Q8771933", "regexp": "destino" }, 
    "deusto": { "q": "Q124796614", "regexp": "deusto" }, 
    "edaf": { "q": "Q124796404", "regexp": "edaf" }, 
    "edebe": { "q": "Q8771871", "regexp": "edeb[ée]" }, 
    "ediciones b": { "q": "Q3047577", "regexp": "ediciones b" }, 
    "el boletín": { "q": "Q56703484", "regexp": "el[ -]?bolet[íi]n" }, 
    "espasa-calpe": { "q": "Q16912403", "regexp": "espasa[ -]calpe" }, 
    "everest": { "q": "Q28324222", "regexp": "everest" }, 
    "gredos": { "q": "Q3047666", "regexp": "gredos" }, 
    "paraninfo": { "q": "Q21036714", "regexp": "paraninfo" }, 
    "península": { "q": "Q124872671", "regexp": "pen[íi]nsula" }, 
    "planeta": { "q": "Q2339634", "regexp": "planeta" }, 
    "planeta-deagostini": { "q": "Q2526307", "regexp": "planeta[ -]?de[ -]?agostini" }, 
    "plaza & janes": { "q": "Q6079378", "regexp": "plaza ?[&y]? ?jan[ée]s" }, 
    "rba": { "q": "Q5687784", "regexp": "rba" }, 
    "santillana": { "q": "Q3118243", "regexp": "santillana" }, 
    "salvat": { "q": "Q3817619", "regexp": "salvat" }, 
    "suroeste": { "q": "Q124799804", "regexp": "suroeste" }, 
    "uned": { "q": "Q124796632", "regexp": "(uned|Universidad Nacional de Educaci[óo]n a Distancia)" }, 
    
    "universidad-autonoma-barcelona": { "q": "Q16630691", "regexp": "(Publicacione?s de la Universi[td]a[td] Aut[óòo]noma de Barcelona|Servicio de Publicaciones de la Universi[td]a[td] Aut[óòo]noma de Barcelona)" },
    "universidad-complutense-madrid": { "q": "Q613189", "regexp": "(Editorial de la Universidad Complutense|Servicio de Publicaciones de la Universidad Complutense de Madrid)" },
}
for publisher, props in publishers.items():
    publishers[publisher]["regexp"] = r"(?im)^(?:ed\.?|editorial|ediciones|libros?|publicaciones)?[ \.\,]*(%s)[ \.\,]*(?:ed\.?|editorial|ediciones|libros?|publicaciones|S\.A\.|SA|S\.L\.|SL)?$" % (publishers[publisher]["regexp"])

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
    titlefull = title.strip(".").strip(" ").strip(".").strip(":").strip(" ") + (subtitle.startswith("(") and " " or ". ") + subtitle[0].upper()+subtitle[1:]
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
    if re.search(r"(?im)^\s*[a-z\,\.]*\s*(\d+)\s*(?:pg?s?|p[aá]gs?|páginas?)\.?", s):
        pages = re.findall(r"(?im)^\s*[a-z\,\.]*\s*(\d+)\s*(?:pg?s?|p[aá]gs?|páginas?)\.?", s)[0]
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

def getTopicQ(topicbneid=""):
    if not topicbneid:
        return
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    candidates = searchInWikidata(s=topicbneid)
    for candidate in candidates:
        item = pywikibot.ItemPage(repo, candidate)
        item.get()
        if "P950" in item.claims and topicbneid in [x.getTarget() for x in item.claims["P950"]]:
            print("Found https://www.wikidata.org/wiki/%s for topic https://datos.bne.es/resource/%s" % (candidate, topicbneid))
            return candidate
    return 

def getTopics(s=""):
    if not s:
        return
    #print(s)
    topics = []
    m = re.findall(r"(?im)/resource/([^<>]+?)\"", s)
    m = list(set(m))
    topicsbneids = []
    for mm in m:
        topicsurl = "https://datos.bne.es/resource/" + mm
        topicraw = getURL(url=topicsurl)
        topicsbneids += re.findall(r"(?im)resource/([^<>]+?)\"[^<>]*?semanticRelation", topicraw)
    topicsbneids = list(set(topicsbneids))
    #print(topicsbneids)
    for topicbneid in topicsbneids:
        topicq = getTopicQ(topicbneid=topicbneid)
        if topicq and not topicq in topics:
            topics.append(topicq)
    return topics

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
    s = re.sub(r"(?im)^D\s*\.?\s*L\s*\.?\s*", "", s)
    s = s.strip()
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
    if 'were no results' in raw:
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

def createdByMyBot(item=""):
    if not item:
        return
    site = pywikibot.Site('wikidata', 'wikidata')
    itempage = pywikibot.Page(site, item)
    history = itempage.getVersionHistoryTable(reverse=True, total=1)
    #print(history)
    return "Emijrpbot" in history

def improveItem(p31="", item="", repo="", props={}):
    if p31 and item and repo and props:
        if not createdByMyBot(item=item):
            print("No creado por mi bot, saltando...")
            return
    return createItem(p31=p31, item=item, repo=repo, props=props)

def createItem(p31="", item="", repo="", props={}):
    global usedlabelsdescspairs
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
        if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
            workitemlabels = { props["lang"]: props["fulltitle"] }
            workitem = pywikibot.ItemPage(repo)
            workitem.editLabels(labels=workitemlabels, summary="BOT - Creating item")
        else:
            return
    workitem.get()
    
    langs = ["es", "en", "fr", "ca", "gl"] #'es' first always
    #labels
    labels = workitem.labels #no quitar esta linea, se usa mas abajo para coger el label es
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
        if overwritelabels or not props["lang"] in workitem.labels or not "en" in workitem.labels:
            labels = workitem.labels
            if overwritelabels or not props["lang"] in labels:
                print("Añadiendo label", props["lang"])
                labels[props["lang"]] = props["fulltitle"]
                workitem.editLabels(labels=labels, summary="BOT - Adding labels (1 languages): %s" % (props["lang"]))
            labels = workitem.labels
            if overwritelabels or (props["lang"] != "en" and not "en" in labels):
                print("Añadiendo label en")
                labels["en"] = props["fulltitle"]
                workitem.editLabels(labels=labels, summary="BOT - Adding labels (1 languages): en")
        else:
            print("Ya tiene labels")
    #descs
    descriptions = workitem.descriptions
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
        if overwritedescriptions or sum([x not in workitem.descriptions for x in langs]):
            authoritem = pywikibot.ItemPage(repo, props["authorq"])
            authoritem.get()
            authornames = {}
            for langx in langs:
                if langx == "es":
                    authornames[langx] = langx in authoritem.labels and authoritem.labels[langx] or props["authorname"]
                else:
                    authornames[langx] = langx in authoritem.labels and authoritem.labels[langx] or authornames["es"]
            suffix = " (ISBN %s)" % (props["isbn"] and props["isbn"] or "???") #suffix for disambig editions in same year and same work, we use isbn
            if p31 == "work":
                descriptions = workitem.descriptions
                for langx in langs:
                    if overwritedescriptions or not langx in workitem.descriptions:
                        print("Añadiendo description", langx)
                        if langx == "es":
                            descriptions[langx] = "obra escrita" + (authornames[langx] and " por %s" % (authornames[langx]) or "")
                        elif langx == "en":
                            descriptions[langx] = "written work" + (authornames[langx] and " by %s" % (authornames[langx]) or "") 
                        elif langx == "fr":
                            descriptions[langx] = "ouvrage écrit" + (authornames[langx] and " par %s" % (authornames[langx]) or "")
                        elif langx == "ca":
                            descriptions[langx] = "obra escrita" + (authornames[langx] and " per %s" % (authornames[langx]) or "") 
                        elif langx == "gl":
                            descriptions[langx] = "obra escrita" + (authornames[langx] and " por %s" % (authornames[langx]) or "")
                        workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): %s" % (langx))
            if p31 == "edition":
                descriptions = workitem.descriptions
                for langx in langs:
                    if overwritedescriptions or not langx in workitem.descriptions:
                        print("Añadiendo description", langx)
                        if langx == "es":
                            descriptions[langx] = "edición" + (props["publicationdate"] and " publicada en %s" % (props["publicationdate"])) + (authornames[langx] and " de la obra escrita por %s" % (authornames[langx]) or "")
                        elif langx == "en":
                            descriptions[langx] = (props["publicationdate"] and "%s " % (props["publicationdate"])) + "edition" + (authornames[langx] and " of written work by %s" % (authornames[langx]) or "") 
                        elif langx == "fr":
                            descriptions[langx] = "édition" + (props["publicationdate"] and " publiée en %s" % (props["publicationdate"])) + (authornames[langx] and " de l'ouvrage écrit par %s" % (authornames[langx]) or "")
                        elif langx == "ca":
                            descriptions[langx] = "edició" + (props["publicationdate"] and " publicada en %s" % (props["publicationdate"])) + (authornames[langx] and " de l'obra escrita per %s" % (authornames[langx]) or "")
                        elif langx == "gl":
                            descriptions[langx] = "edición" + (props["publicationdate"] and " publicada en %s" % (props["publicationdate"])) + (authornames[langx] and " da obra escrita por %s" % (authornames[langx]) or "")
                        labeldescpair = labels["es"]+"#"+langx+"#"+descriptions[langx] #usar label es y desc langx, ya q no pongo label a todos los langx
                        if labeldescpair in usedlabelsdescspairs: #if desc already in other item, add isbn suffix
                            descriptions[langx] += suffix
                        usedlabelsdescspairs.append(labeldescpair)
                        workitem.editDescriptions(descriptions=descriptions, summary="BOT - Adding descriptions (1 languages): %s" % (langx))
        else:
            print("Ya tiene descripciones")
    #aliases
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
        if props["alternatetitles"]:
            if overwritealiases:
                workitem.aliases = {}
            for alternatetitle in props["alternatetitles"]:
                if alternatetitle != props["fulltitle"]:
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
    if p31 == "work" and props["resourceid"] == props["editionearliest"]:
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
    
    #metemos bne id enseguida tras crear el item (y habiendo definido el P31, q se usa en las busquedas para separar), por si falla algo poder usarlo en la búsqueda para reanudar
    #P950 = bne id (edition)
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
    #P950 = bne id (work)
    if p31 == "work" and props["resourceid"] == props["editionearliest"]:
        if props["workbneid"]:
            if not "P950" in workitem.claims:
                print("Añadiendo P950")
                claim = pywikibot.Claim(repo, 'P950')
                claim.setTarget(props["workbneid"])
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=props["workbneid"])
            else:
                print("Ya tiene P950")
    
    #P50 = authorq
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
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
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]): #los contributor los metemos en work y en edition
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
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
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
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
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
    if p31 == "edition" or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
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
    if p31 == "edition":# or (p31 == "work" and props["resourceid"] == props["editionearliest"]):
        if props["publicationdate"]:
            if not "P577" in workitem.claims:
                print("Añadiendo P577")
                claim = pywikibot.Claim(repo, 'P577')
                claim.setTarget(pywikibot.WbTime(year=props["publicationdate"]))
                workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
            else:
                print("Ya tiene P577")
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
    #P921 main subject
    if p31 == "work" and props["resourceid"] == props["editionearliest"]: #solo en works
        if props["topics"]:
            for topicq in props["topics"]:
                if not "P921" in workitem.claims or not topicq in [topicx.getTarget().title() for topicx in workitem.claims["P921"]]:
                    print("Añadiendo P921")
                    claim = pywikibot.Claim(repo, 'P921')
                    target = pywikibot.ItemPage(repo, topicq)
                    claim.setTarget(target)
                    workitem.addClaim(claim, summary='BOT - Adding 1 claim')
                    addBNERef(repo=repo, claim=claim, bneid=p31 == "work" and props["authorbneid"] or props["resourceid"])
                else:
                    print("Ya tiene P921")
    
    #P8383 = goodreads work id
    if p31 == "work" and props["resourceid"] == props["editionearliest"]:
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
    if p31 == "work" and props["resourceid"] == props["editionearliest"]:
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
    
    print("Creado/Modificado https://www.wikidata.org/wiki/%s" % (workitem.title()))
    return workitem.title() #para enlazar work/edition

def getGoodReadsWorkId(title="", isbn10="", isbn13=""):
    #<a class="DiscussionCard" href="https://www.goodreads.com/work/quotes/97295167">
    if not title or (not isbn10 and not isbn13):
        return
    busqueda = " "*random.randint(1,20)
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
    busqueda = " "*random.randint(1,20)
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
        goodreadseditionid = "https://www.goodreads.com/review/edit/" in raw and re.findall(r"(?im)\"https://www\.goodreads\.com/review/edit/(\d+)\"", raw)[0] or ""
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
    
    if not createdByMyBot(item=workq) or not createdByMyBot(item=editionq):
        print("El work o la edition no fueron creadas por mi, saltando")
        return 
    
    print("\nIntentando enlazar work https://www.wikidata.org/wiki/%s con edition https://www.wikidata.org/wiki/%s" % (workq, editionq))
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

def getAuthorsByDate(month=0, day=0):
    authors = []
    if not month or not day or month < 1 or month > 12 or day < 1 or day > 31:
        today = datetime.date.today()
        month, day = today.month, today.day
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    queries = [
        """
        SELECT ?item
        WHERE {
          ?item wdt:P31 wd:Q5.
          ?item wdt:P569 ?birthdate.
          ?item wdt:P27 wd:Q29.
          ?item wdt:P106 wd:Q36180. #writer
          ?item wdt:P950 ?bne.
          FILTER (?birthdate >= "1900-01-01"^^xsd:dateTime && ?birthdate < "2000-01-01"^^xsd:dateTime).
          FILTER (MONTH(?birthdate) = %d && DAY(?birthdate) = %d).
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        ORDER BY ?birthdate
        """ % (month, day), 
    ]
    for query in queries:
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
        url = '%s&format=json' % (url)
        print("Loading...", url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            if not q:
                break
            #print('\n== %s ==' % (q))
            #print("https://www.wikidata.org/wiki/%s" % (q))
            item = pywikibot.ItemPage(repo, q)
            try: #to detect Redirect because .isRedirectPage fails
                item.get()
            except:
                print('Error while .get()')
                continue
            
            if item.claims:
                if 'P950' in item.claims and len(item.claims["P950"]) == 1:
                    authors.append(q)
    return authors

def main():
    global usedisbns
    global usedlegaldeposits
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    qlist = ["Q93433647"] #eusebio
    qlist += ["Q118122724"] #almisas
    qlist += ["Q5865630"] #paco espinosa
    qlist += ["Q124800393"] #fernando romero
    qlist += ["Q16300815"] #grimaldos
    qlist += ["Q63213321"] #demiguel
    qlist = ["Q5859788"] #Redonet
    qlist = getAuthorsByDate()
    
    print("\n".join(qlist))
    print("%d authors" % (len(qlist)))
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
        
        if not birthdate and not deathdate:
            print("Autor sin fecha de nacimiento ni falleciento conocida, saltamos")
            continue
        if (birthdate and birthdate < 1900) or (deathdate and deathdate < 1970):
            print("Autor antiguo, saltamos")
            continue
        
        #obras, el rdf no es completo? mejor parsearlo así por html
        #solo las que sean de su autoría, no las que haya participado o sean sobre esa persona (tema)
        obras = ""
        if '<section id="obras" class="container">' in raw:
            obras = raw.split('<section id="obras" class="container">')[1].split('</section>')[0]
        for obra in obras.split("</li>"):
            time.sleep(0.1)
            resourcesids = []
            resourceid = "/resource/" in obra and re.findall(r"(?im)href=\"/resource/([^<>\"]+?)\"", obra)[0] or ""
            titletruncated = "item-link" in obra and unquote(re.findall(r"(?im)class=\"item-link\">([^<>]+?)</a>", obra)[0]) or ""
            if not resourceid:
                continue
            print('\n== %s ==' % (resourceid))
            print("https://datos.bne.es/resource/%s" % (resourceid))
            print(titletruncated)
            
            #if resourceid != "XX5929043":
            #    continue
            
            workbneid = ""
            #coger la edición más temprana a partir de la cual se creará el work
            editionearliest = ""
            publicationdateearliest = ""
            if '<div class="text-center">Libro</div>' in obra:
                if resourceid:
                    resourcesids.append(resourceid)
                    editionearliest = resourceid
            elif '<div class="text-center">Obra</div>' in obra:
                #print("Saltando obras con más de 1 edición por ahora...")
                #continue
                workbneid = resourceid
                url2 = "https://datos.bne.es/resource/" + resourceid
                raw2 = getURL(url=url2)
                if "página no encontrada, pero no estás perdido" in raw2:
                    print("Error resourceid", resourceid)
                    continue
                if not "<h2>Español" in raw2:
                    print("No seccion en espanol", resourceid)
                    continue
                for edition in raw2.split('<div class="media-body">'):
                    resourceid = "/edicion/" in edition and re.findall(r"(?im)href=\"/edicion/([^<>\"]+?)\"", edition)[0] or ""
                    m = "Fecha de publicación" in edition and re.findall(r"(?im)<strong>\s*Fecha de publicación\s*</strong>\s*</td>\s*<td>([^<>]*?)</td>", edition)[0] or ""
                    publicationdate = m and getPublicationDate(s=unquote(m)) or ""
                    if resourceid and publicationdate:
                        if publicationdate and (not publicationdateearliest or publicationdateearliest > publicationdate):
                            publicationdateearliest = publicationdate
                            editionearliest = resourceid
                    if resourceid:
                        resourcesids.append(resourceid)
            else:
                print("Tipo de entidad no soportada, saltando")
                continue
            
            resourcesids.reverse() #invertimos orden para empezar a crear ediciones desde la más antigua, por si falla algo, q el written work quede hecho
            print("editionearliest", editionearliest)
            print("publicationdateearliest", publicationdateearliest)
            
            workscreated = []
            editionscreated = []
            editionsavailable2 = [] #2 es global a la obra, sin2 es dentro de la edicion
            #ediciones
            for resourceid in resourcesids:
                isdigital = False
                print('\n=== %s ===' % (resourceid))
                urlresource = "https://datos.bne.es/resource/%s.rdf" % (resourceid)
                urlresourcehtml = "https://datos.bne.es/resource/%s" % (resourceid)
                print(urlresource)
                print(urlresourcehtml)
                rawresource = getURL(url=urlresource)
                #esto era para los topics, pero salen demasiado genericos https://www.wikidata.org/w/index.php?title=Q124805629&diff=2098727818&oldid=2098641541
                #time.sleep(1)
                #rawresourcehtml = getURL(url=urlresourcehtml)
                m = re.findall(r"(?im)<ns\d:language rdf:resource=\"https?://id\.loc\.gov/vocabulary/languages/([^<>]+?)\"\s*/>", rawresource)
                lang = m and unquote(m[0]) or ""
                #if not lang in languages2iso:
                #    print("Idioma no entendido", lang, "saltamos")
                #    continue
                if lang != "spa":
                    print("De momento solo importamos en espanol, saltamos")
                    continue
                #title, subtitle, alternatetitles
                m = re.findall(r"(?im)<ns\d:P3002>([^<>]+?)</ns\d:P3002>", rawresource)
                title_ = m and unquote(m[0]) or "" #se usa para el fulltitle
                title_ = title_.replace(" : ", ": ")
                title = title_.strip(" ").strip(".").strip(":").strip(",").strip(" ") #no usar clearsymbols pq puede quitar (), solo quitar ,.: finales si hay
                m = re.findall(r"(?im)<ns\d:P3014>([^<>]+?)</ns\d:P3014>", rawresource)
                subtitle = m and unquote(m[0]) or ""
                subtitle = subtitle and (subtitle[0].upper() + subtitle[1:]) or ""
                subtitle = subtitle.replace(" : ", ": ")
                alternatetitle = title + " " + subtitle
                alternatetitle = alternatetitle.strip()
                alternatetitle2 = alternatetitle.replace(" : ", ": ").strip()
                alternatetitle3 = alternatetitle.replace(" : ", ", ").strip()
                alternatetitle4 = alternatetitle.replace(" : ", " ").strip()
                alternatetitles = list(set([alternatetitle, alternatetitle2, alternatetitle3, alternatetitle4]))
                fulltitle = getFullTitle(title=title_, subtitle=subtitle)
                if re.search(r"(?im)[\[\]]", fulltitle):
                    print("Caracteres extranos en titulo, saltamos", fulltitle)
                    continue
                if re.search(r"(?im)(expo|ed[oó]f|sex|asesi|erroris)", fulltitle):
                    print("Titulo no valido, saltamos", fulltitle)
                    continue
                
                #contributors
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
                
                #publisher, date, location
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
                #extension pages
                extension = m and unquote(m[0]) or ""
                pages = getExtensionInPages(s=extension)
                if pages and (pages < 50 or pages > 999): #si el numero de paginas es raro, lo blanqueamos y seguimos
                    #print("Numero de paginas raro, saltamos", pages)
                    pages = ""
                    #continue
                #dimensions height
                m = re.findall(r"(?im)<ns\d:P3007>([^<>]+?)</ns\d:P3007>", rawresource)
                dimensions = m and unquote(m[0]) or ""
                height = getHeightInCM(s=dimensions)
                if height and (height < 10 or height > 40): #si la altura es rara, la blanqueamos y seguimos
                    #print("Altura extraña, saltamos", height)
                    height = ""
                    #continue
                #topics
                #m = '<div class="temas">' in rawresourcehtml and rawresourcehtml.split('<div class="temas">')[1].split('</div>')[0] or ""
                #topics = getTopics(s=m)
                #isbn
                m = re.findall(r"(?im)<ns\d:P3013>([^<>]+?)</ns\d:P3013>", rawresource)
                isbn = ""
                isbnplain = ""
                isbn10 = ""
                isbn13 = ""
                for mm in m:
                    isbn = mm and unquote(mm) or ""
                    isbnplain = isbn and isbn.replace("-", "") or ""
                    if len(isbnplain) == 10:
                        isbn10 = isbn
                    elif len(isbnplain) == 13:
                        isbn13 = isbn
                if isbn13:
                    isbn = isbn13
                elif isbn10:
                    isbn = isbn10
                else:
                    isbn = ""
                isbnplain = isbn and isbn.replace("-", "") or ""
                if not isbn:
                    print("ISBN no encontrado, saltamos")
                    continue
                if isbn and isbn in usedisbns:
                    print("ISBN usado ya en otra edicion, saltamos", isbn)
                    continue
                usedisbns.append(isbn) #no meter isbn10 pq puede ser vacio y luego la comparacion dice q si siempre
                if isbn10 and not isbn10.startswith("84"):
                    print("ISBN10 no de Espana, saltamos", isbn10)
                    continue
                if isbn13 and not isbn13.startswith("978-84") and not isbn13.startswith("97884"):
                    print("ISBN13 no de Espana, saltamos", isbn13)
                    continue
                #legal deposit
                m = re.findall(r"(?im)<ns\d:P3009>([^<>]+?)</ns\d:P3009>", rawresource)
                legaldeposit = m and getLegalDeposit(s=unquote(m[0])) or ""
                if legaldeposit in usedlegaldeposits:
                    print("Legaldeposit usado ya en otra edicion, saltamos", legaldeposit)
                    continue
                usedlegaldeposits += [legaldeposit]
                #mediatype
                m = re.findall(r"(?im)<ns\d:P3062>([^<>]+?)</ns\d:P3062>", rawresource)
                mediatype = m and unquote(m[0]) or ""
                #distributionformat
                distributionformat = ""
                if re.search(r"(?im)(e[ -]?book|elec|cd|dvd|disco|rom|dig|comp|ord|internet|web|recu|l[ií]nea|case|nega|partitura|online|micro|v[íi]deo|sono|carpe|carta|piano|rollo)", extension+mediatype): #no poner lámina, hojas, etc pq entonces se deja ediciones válidas en papel https://datos.bne.es/edicion/a6503577.html
                    print("Extension/Medio no interesa, saltamos edicion pero no work", extension+mediatype)
                    isdigital = True
                else:
                    distributionformat = "Q11396303" #printed book
                
                #external ids
                goodreadsworkid = getGoodReadsWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
                openlibraryworkid = getOpenLibraryWorkId(title=fulltitle, isbn10=isbn10, isbn13=isbn13)
                if not workbneid and not goodreadsworkid and not openlibraryworkid:
                    print("BNE no tiene workid individual, ni lo hemos encontrado en GoodReads ni OpenLibrary, no creamos este libro, para evitar crear un written work sin IDs")
                    break
                
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
                    
                    "workbneid": workbneid, 
                    "resourceid": resourceid, 
                    "pages": pages, 
                    "height": height, 
                    "distributionformat": distributionformat,
                    "isdigital": isdigital,
                    
                    "publisher": publisher, 
                    "publicationlocation": publicationlocation, 
                    "publicationdate": publicationdate, 
                    
                    "editionearliest": editionearliest, 
                    "publicationdateearliest": publicationdateearliest, 
                    
                    "topics": [], #topics,
                    
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
                candidates = searchInWikidata(l=[isbn, isbnplain, isbn10, isbn13, resourceid, workbneid, goodreadsworkid, openlibraryworkid, goodreadseditionid, openlibraryeditionid]) #no poner fulltitle ni title
                candidates = list(set(candidates))
                candidates.sort()
                #print(candidates)
                
                worksavailable = []
                editionsavailable = []
                othersavailable = []
                for candidate in candidates:
                    if candidate in donecandidates:
                        continue
                    print("Analizando candidato", candidate)
                    donecandidates.append(candidate)
                    candidateitem = pywikibot.ItemPage(repo, candidate)
                    candidateitem.get()
                    if ("P957" in candidateitem.claims and isbn10 and isbn10 in [x.getTarget() for x in candidateitem.claims["P957"]]) or \
                       ("P212" in candidateitem.claims and isbn13 and isbn13 in [x.getTarget() for x in candidateitem.claims["P212"]]) or \
                       ("P957" in candidateitem.claims and isbnplain and isbnplain in [x.getTarget() for x in candidateitem.claims["P957"]]) or \
                       ("P212" in candidateitem.claims and isbnplain and isbnplain in [x.getTarget() for x in candidateitem.claims["P212"]]) or \
                       ("P950" in candidateitem.claims and workbneid and workbneid in [x.getTarget() for x in candidateitem.claims["P950"]]) or \
                       ("P950" in candidateitem.claims and resourceid and resourceid in [x.getTarget() for x in candidateitem.claims["P950"]]) or \
                       ("P648" in candidateitem.claims and openlibraryworkid and openlibraryworkid in [x.getTarget() for x in candidateitem.claims["P648"]]) or \
                       ("P648" in candidateitem.claims and openlibraryeditionid and openlibraryeditionid in [x.getTarget() for x in candidateitem.claims["P648"]]) or \
                       ("P8383" in candidateitem.claims and goodreadsworkid and goodreadsworkid in [x.getTarget() for x in candidateitem.claims["P8383"]]) or \
                       ("P2969" in candidateitem.claims and goodreadseditionid and goodreadseditionid in [x.getTarget() for x in candidateitem.claims["P2969"]]):
                        print("Candidato coincide algun ID")
                        if "P31" in candidateitem.claims:
                            for candidateitemp31 in candidateitem.claims["P31"]:
                                if "Q47461344" == candidateitemp31.getTarget().title(): #work
                                    improveItem(p31="work", item=candidate, repo=repo, props=props)
                                    worksavailable.append(candidate)
                                elif "Q3331189" == candidateitemp31.getTarget().title(): #edition
                                    if not isdigital:
                                        improveItem(p31="edition", item=candidate, repo=repo, props=props)
                                    editionsavailable.append(candidate)
                                    editionsavailable2.append(candidate)
                                else:
                                    othersavailable.append(candidate) #to avoid create when that isbn/goodreads/etc exists in an item
                                
                    else:
                        print("Candidato descartado, no coinciden IDs")
                
                workq = ""
                editionq = ""
                if not workscreated and not worksavailable and not othersavailable and editionearliest == resourceid: #no crear work si existen items relacionados (othersavailable) q no son ni written work ni editions, para evitar crear duplicados
                    print("\nNo se encontraron candidatos para el work, creamos")
                    workq = createItem(p31="work", repo=repo, props=props)
                    if workq:
                        workscreated.append(workq)
                if not isdigital and not editionsavailable and not othersavailable:
                    print("\nNo se encontraron candidatos para la edition, creamos")
                    editionq = createItem(p31="edition", repo=repo, props=props)
                    if editionq:
                        editionscreated.append(editionq)
                if workq and editionq:
                    linkWorkAndEdition(repo=repo, workq=workq, editionq=editionq)
                #repasa las editions por si alguna no esta enlazada al work y viceversa
                if len(workscreated+worksavailable) == 1 and len(editionscreated+editionsavailable2) >= 1:
                    workq = workscreated and workscreated[0] or worksavailable and worksavailable[0]
                    for editionq in editionscreated+editionsavailable2:
                        linkWorkAndEdition(repo=repo, workq=workq, editionq=editionq)
                
                #if resourceid in ["a7153685", "a5311062"]:
                #    sys.exit()

if __name__ == "__main__":
    main()
