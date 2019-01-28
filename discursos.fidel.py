#!/usr/bin/env python
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

import re
import sys
import time
import urllib

import pwb
import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

def unquote(s=''):
    s = re.sub('&#8220;', '"', s)
    s = re.sub('&#8221;', '"', s)
    s = re.sub('&quot;', '"', s)
    s = re.sub('&quote;', '"', s)
    s = re.sub('&nbsp;', ' ', s)
    return s

def addReference(repo='', claim='', ref=''):
    if repo and claim and ref:
        refclaim = pywikibot.Claim(repo, 'P854') # dirección web de la referencia (P854) 
        refclaim.setTarget(ref)
        claim.addSource(refclaim, summary='BOT - Adding 1 reference')

def addClaim(repo='', item='', claim='', value='', valuelang='', ref=''):
    if repo and item and claim and value:
        print("Adding claim", claim, "value", value.encode('utf-8'))
        claimx = pywikibot.Claim(repo, claim)
        if re.search(r'\d\d\d\d-\d\d-\d\d', value):
            target = pywikibot.WbTime(year=int(value.split('-')[0]), month=int(value.split('-')[1]), day=int(value.split('-')[2]))
        elif value.startswith('Q'):
            target = pywikibot.ItemPage(repo, value)
        elif valuelang:
            target = pywikibot.WbMonolingualText(text=value, language=valuelang)
        else:
            target = value
        claimx.setTarget(target)
        item.addClaim(claimx, summary='BOT - Adding 1 claim')
        if ref:
            addReference(repo=repo, claim=claimx, ref=ref)

def main():
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    repo = wdsite.data_repository()
    url = 'https://web.archive.org/web/20190121103311/http://www.cuba.cu/gobierno/discursos/'
    raw = urllib.request.urlopen(url).read()
    raw = raw.decode('latin-1')
    raw = re.sub(r'(?im)\n', ' ', raw)
    discursos = re.findall(r'(?im)(Discurso\s+pronun[^<>]+).*?(\d\d\d\d/esp/[^"]+?\.html)"', raw)
    for discurso in discursos:
        titulo = re.sub(r'(?im)\s+', ' ', discurso[0]).strip().strip('(').strip().strip('.')
        titulo = unquote(s=titulo)
        titulo = titulo.strip().strip('.').strip()
        titulo = titulo[:250]
        enlace = discurso[1].strip()
        fecha = re.findall(r'(?im)(\d\d)(\d\d)(\d\d)', enlace.split('/')[2])[0]
        fecha = '%s-%s-%s' % (fecha[2], fecha[1], fecha[0])
        if int(fecha[:2]) >= 59 and int(fecha[:2]) <= 99:
            fecha = '19' + fecha
        else:
            fecha = '20' + fecha
        if fecha[:4] != sys.argv[1]:
            continue
        print(titulo.encode('utf-8'), enlace, fecha)
        
        searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=es&format=xml' % (urllib.parse.quote(titulo))
        raw = getURL(searchitemurl)
        print(searchitemurl.encode('utf-8'))
        if '<search />' in raw:
            print("No existe item, creamos")
            item = pywikibot.ItemPage(repo)
            data = {}
            data['labels'] = { 'es': titulo }
            data['descriptions'] = { 'es': 'discurso de Fidel Castro', 'en': 'speech by Fidel Castro' }
            summary = 'BOT - Creating item for Fidel Castro speech'
            item.editEntity(data, summary=summary)
            addClaim(repo=repo, item=item, claim='P31', value='Q861911', ref='http://www.cuba.cu/gobierno/discursos/')
            addClaim(repo=repo, item=item, claim='P1476', value=titulo, valuelang='es', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
            addClaim(repo=repo, item=item, claim='P50', value='Q11256', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
            addClaim(repo=repo, item=item, claim='P407', value='Q1321', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
            addClaim(repo=repo, item=item, claim='P577', value=fecha, ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
            addClaim(repo=repo, item=item, claim='P823', value='Q11256', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
            addClaim(repo=repo, item=item, claim='P953', value='http://www.cuba.cu/gobierno/discursos/' + enlace, ref='')
            #sys.exit()
        else:
            print("Existe item")
            m = re.findall(r'id="(Q\d+)"', raw)
            if len(m) != 1:
                print("Mas de 1 resultado, saltamos")
                continue
            for itemq in m:
                item = pywikibot.ItemPage(repo, itemq)
                item.get()
                if not 'P31' in item.claims:
                    addClaim(repo=repo, item=item, claim='P31', value='Q861911', ref='http://www.cuba.cu/gobierno/discursos/')
                if not 'P1476' in item.claims:
                    addClaim(repo=repo, item=item, claim='P1476', value=titulo, valuelang='es', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
                if not 'P50' in item.claims:
                    addClaim(repo=repo, item=item, claim='P50', value='Q11256', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
                if not 'P407' in item.claims:
                    addClaim(repo=repo, item=item, claim='P407', value='Q1321', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
                if not 'P577' in item.claims:
                    addClaim(repo=repo, item=item, claim='P577', value=fecha, ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
                if not 'P823' in item.claims:
                    addClaim(repo=repo, item=item, claim='P823', value='Q11256', ref='http://www.cuba.cu/gobierno/discursos/' + enlace)
                if not 'P953' in item.claims:
                    addClaim(repo=repo, item=item, claim='P953', value='http://www.cuba.cu/gobierno/discursos/' + enlace, ref='')
                #sys.exit()

if __name__ == "__main__":
    main()
