#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2022 emijrp <emijrp@gmail.com>
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

"""
SELECT ?itemDescBase (COUNT(?item) AS ?count)
WHERE {
  SERVICE bd:sample {
    ?item wdt:P31 wd:Q5 .
    bd:serviceParam bd:sample.limit 10000 .
    bd:serviceParam bd:sample.sampleType "RANDOM" .
  }
  ?item wdt:P21 wd:Q6581097.
  OPTIONAL { ?item schema:description ?itemDescBase. FILTER(LANG(?itemDescBase) = "%s").  }
  FILTER (BOUND(?itemDescBase))
  OPTIONAL { ?item schema:description ?itemDescTarget. FILTER(LANG(?itemDescTarget) = "%s").  }
  FILTER (!BOUND(?itemDescTarget))
}
GROUP BY ?itemDescBase
ORDER BY DESC(?count)
LIMIT 100
% (baselang, lang)
"""

def genDescs(gender=""):
    occupations = ["anthropologist", "archaeologist", "architect", "archivist", "astronomer", "biologist", "botanist", "cartographer", "chemist", "composer", "economist", "egyptologist", "engineer", "engraver", "entomologist", "ethnologist", "geologist", "geographer", "historian", "journalist", "librarian", "linguist", "mathematician", "mycologist", "painter", "philologist", "philosopher", "photographer", "physicist", "pianist", "playwright", "poet", "politician", "sculptor", "singer", "writer", "zoologist"]
    #other or rare: "anatomist", "academic", "alpine skier", "archer", "art historian", "artist", "association football player", "association football referee", "association football manager", "athlete", "athletics competitor", "basketball coach", "basketball player", "biathlete", "bicycle racer", "bishop", "archbishop", "boxer", "businessperson", "catholic priest", "Catholic priest", "caricaturist", "chef", "chess player", "children's writer", "choreographer", "comics artist", "cross-country skier", "cyclist", "dermatologist", "diplomat", "Esperantist", "essayist", "explorer", "fencer", "field hockey player", "film critic", "film director", "film producer", "flying ace", "footballer", "geneticist", "guitarist", "gymnast", "gynaecologist", "handball player", "ice hockey player", "illustrator", "judoka", "jurist", "lawyer", "legal historian", "literary critic", "lithographer", "medievalist", "mineralogist", "missionary", "motorcycle racer", "musician", "musicologist", "naturalist", "neurologist", "novelist", "oncologist", "opera singer", "ophthalmologist", "organist", "orientalist", "ornithologist", "pathologist", "pharmacist", "pharmacologist", "physician", "physiologist", "political scientist", "psychiatrist", "psychoanalyst", "psychologist", "publisher", "rabbi", "racing driver", "radiologist", "rally driver", "rapper", "rower", "rugby union player", "saxophonist", "scientist", "screenwriter", "singer-songwriter", "ski jumper", "snowboarder", "sociologist", "soldier", "speleologist", "sport cyclist", "spy", "surgeon", "swimmer", "tennis player", "theatre director", "theologian", "trade unionist", "troubadour", "university teacher", "veterinarian", "violinist", "virologist", "volleyball player", "water polo player", "skier", "educator", "translator", "model", "violinist", "cellist", "bassist", "geographer", "theologian"
    descs = []
    if gender:
        if gender == "male":
            descs += genDescByNationality(occupation="actor")
        if gender == "female":
            descs += genDescByNationality(occupation="actress")
        
        for occupation in occupations:
            descs += genDescByNationality(occupation=occupation)
    return descs

def genDescByNationality(occupation=""):
    nationalities = ["Afghan", "Albanian", "Algerian", "American", "Andorran", "Angolan", "Argentine", "Argentinean", "Armenian", "Argentinian", "Australian", "Austrian", "Azerbaijani", "Bahamian", "Bahraini", "Bangladeshi", "Barbadian", "Belarusian", "Belgian", "Belizean", "Beninese", "Beninois", "Bermudan", "Bermudian", "Bhutanese", "Bolivian", "Bosnian", "Botswanan", "Brazilian", "British", "Bruneian", "Bulgarian", "Burmese", "Burundian", "Cambodian", "Cameroonian", "Canadian", "Chadian", "Chilean", "Chinese", "Colombian", "Congolese", "Croatian", "Cuban", "Cypriot", "Czech", "Danish", "Djiboutian", "Dutch", "Ecuadorian", "Egyptian", "Eritrean", "Estonian", "Ethiopian", "Fijian", "Filipino", "Finnish", "French", "Gabonese", "Gambian", "Georgian", "German", "Ghanaian", "Greek", "Greenlandic", "Grenadian", "Guatemalan", "Guinean", "Guyanese", "Haitian", "Herzegovinian", "Honduran", "Hungarian", "Icelandic", "Indian", "Indonesian", "Iranian", "Iraqi", "Irish", "Israeli", "Italian", "Ivorian", "Jamaican", "Japanese", "Jordanian", "Kenyan", "Kiribati", "Kuwaiti", "Latvian", "Lebanese", "Liberian", "Libyan", "Liechtensteiner", "Lithuanian", "Luxembourg", "Luxembourgish", "Macanese", "Macedonian", "Malagasy", "Malawian", "Malaysian", "Maldivian", "Malian", "Maltese", "Mauritanian", "Mauritian", "Mexican", "Moldovan", "Monacan", "Monégasque", "Mongolian", "Montenegrin", "Moroccan", "Mozambican", "Namibian", "Nauruan", "New Zealand", "Nicaraguan", "North Korean", "Norwegian", "Omani", "Pakistani", "Palauan", "Palestinian", "Panamanian", "Paraguayan", "Peruvian", "Philippine", "Polish", "Portuguese", "Qatari", "Romanian", "Russian", "Rwandan", "Salvadoran", "Sammarinese", "Samoan", "Senegalese", "Serbian", "Seychellois", "Slovak", "Somali", "Spanish", "Sudanese", "Surinamese", "Swedish", "Swiss", "Syrian", "Tajikistani", "Tanzanian", "Thai", "Timorese", "Togolese", "Tongan", "Tunisian", "Tuvaluan", "Ugandan", "Ukrainian", "Uruguayan", "Uzbek", "Uzbekistani", "Vanuatuan", "Vatican", "Venezuelan", "Vietnamese", "Yemeni", "Zambian", "Zimbabwean"]
    #other or rare "Bissau-Guinean", "Burkinabe", "Burkinabé", "Cabo Verdean",  "Comoran", "Comorian", "Costa Rican", "Emirati", "Emiri", "Emirian", "Equatoguinean", "Equatorial Guinean", "I-Kiribati", "Kazakh", "Kazakhstani", "Kirghiz", "Kirgiz", "Kosovan", "Kosovar", "Kyrgyz", "Kyrgyzstani", "Lao", "Laotian", "Mosotho", "Nepalese", "Nepali", "Ni-Vanuatu", "Nigerian", "Nigerien", "Papua New Guinean", "Papuan", "Puerto Rican", "São Toméan", "Saudi", "Saudi Arabian", "Sierra Leonean", "Singapore", "Singaporean", "Slovene", "Slovenian", "South African", "South Korean", "Sri Lankan", "Trinidadian", "Tobagonian", "Turkish", "Turkmen", "UK", "U.K.", "United States",  "US", "U.S.", 
    descs = []
    if occupation and len(occupation) > 3:
        for nationality in nationalities:
            descs.append("%s %s" % (nationality, occupation))
    return descs

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    basedescsdict = {
        "?item wdt:P31 wd:Q5. ?item wdt:P21 wd:Q6581097.": { #human male
            "en": genDescs(gender="male"), 
        }, 
        "?item wdt:P31 wd:Q5. ?item wdt:P21 wd:Q6581072.": { #human female
            "en": genDescs(gender="female"), 
        }, 
    }
    targetlangs = ["ast", "ca", "es", "eu", "fr", "gl", "it", "pl", "pt", "ro", "sq"]
    targetlangs += ["an", "da", "et", "ext", "nn", "no", "oc", "sk", "sv", "tr"]
    targetlangs += ["eo", "ar", "he", "hu", "bn", "el", "fi", "cs", "ru", "bg", "fa", "af"]
    targetlangs = list(set(targetlangs))
    mincount = 25 #cuidado, esto define la calidad de las traducciones, no bajar de 25 o puede escoger malas traducciones
    for wdt, v in basedescsdict.items():
        for baselang, basedescs in v.items():
            basedescsshuffle = basedescs
            random.shuffle(basedescsshuffle)
            for basedesc in basedescsshuffle:
                print(" | ".join([wdt, baselang, basedesc]))
                time.sleep(0.1)
                query0 = """
SELECT (COUNT(?item) AS ?count)
WHERE {
%s
?item schema:description "%s"@%s.
}
""" % (wdt, basedesc, baselang)
                url0 = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query0))
                url0 = '%s&format=json' % (url0)
                #print("Loading...", url0)
                sparql0 = getURL(url=url0)
                json0 = loadSPARQL(sparql=sparql0)
                for result0 in json0['results']['bindings']:
                    #print(result0)
                    count = 'count' in result0 and int(result0['count']['value']) or 0
                if count < mincount:
                    print("Not enought results, skiping...")
                    continue
                
                for targetlang in targetlangs:
                    print(" | ".join([wdt, baselang, basedesc, targetlang]))
                    time.sleep(0.1)
                    query1 = """
SELECT ?itemDescTargetLang (COUNT(?item) AS ?count)
WHERE {
    %s
    ?item schema:description "%s"@%s.
    OPTIONAL { ?item schema:description ?itemDescTargetLang. FILTER(LANG(?itemDescTargetLang) = "%s"). }
    FILTER (BOUND(?itemDescTargetLang))
}
GROUP BY ?itemDescTargetLang
ORDER BY DESC(?count)
""" % (wdt, basedesc, baselang, targetlang)
                    url1 = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query1))
                    url1 = '%s&format=json' % (url1)
                    #print("Loading...", url1)
                    sparql1 = getURL(url=url1)
                    json1 = loadSPARQL(sparql=sparql1)
                    
                    c = 1
                    desctargetlang1 = ""
                    desctargetlang1c = 0
                    desctargetlang2 = ""
                    desctargetlang2c = 0
                    for result1 in json1['results']['bindings']:
                        #print(result1)
                        desctargetlang = 'itemDescTargetLang' in result1 and result1['itemDescTargetLang']['value'] or ''
                        count = 'count' in result1 and int(result1['count']['value']) or 0
                        print(desctargetlang, count)
                        if c == 1:
                            desctargetlang1 = desctargetlang
                            desctargetlang1c = count
                        if c == 2:
                            desctargetlang2 = desctargetlang
                            desctargetlang2c = count
                            break
                        c += 1
                    
                    if desctargetlang1c < mincount or desctargetlang1c < desctargetlang2c * 5 or len(desctargetlang1.split(' ')) != len(basedesc.split(' ')) or re.search(r"(?i)[0-9\(\)]", desctargetlang1):
                        print("Skiping description, good candidate not found")
                        continue
                    else:
                        print("Good candidate found: %s (%s uses)" % (desctargetlang1, desctargetlang1c))
                    
                    query2 = """
SELECT ?item
WHERE {
    %s
    ?item schema:description "%s"@%s.
    OPTIONAL { ?item schema:description ?itemDescTargetLang. FILTER(LANG(?itemDescTargetLang) = "%s"). }
    FILTER (!BOUND(?itemDescTargetLang))
}
""" % (wdt, basedesc, baselang, targetlang)
                    url2 = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query2))
                    url2 = '%s&format=json' % (url2)
                    #print("Loading...", url2)
                    sparql2 = getURL(url=url2)
                    json2 = loadSPARQL(sparql=sparql2)
                    for result2 in json2['results']['bindings']:
                        time.sleep(0.5)
                        #print(result2)
                        q = 'item' in result2 and result2['item']['value'].split('/entity/')[1] or ''
                        if not q:
                            continue
                        item = pywikibot.ItemPage(repo, q)
                        try: #to detect Redirect because .isRedirectPage fails
                            item.get()
                        except:
                            print('Error while .get()')
                            continue
                        
                        itemdesc = item.descriptions
                        if not targetlang in itemdesc.keys():
                            itemdesc[targetlang] = desctargetlang1
                            data = { 'descriptions': itemdesc }
                            summary = 'BOT - Adding descriptions (1 languages): %s' % (targetlang)
                            print(q, summary)
                            cronstop()
                            try:
                                item.editEntity(data, summary=summary)
                                #break
                            except:
                                print('Error while saving')
                                continue
    print("Finished successfully")

if __name__ == "__main__":
    main()
