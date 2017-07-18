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
import sys
import urllib

import pywikibot
from pywikibot import pagegenerators

from wikidatafun import *

def addclaim(repo='', item='', p='', q='', s=''):
    target = ''
    if q:
        target = pywikibot.ItemPage(repo, q)
    elif s:
        target = s
    else:
        return
    if target:
        claim = pywikibot.Claim(repo, p)
        claim.setTarget(target)
        item.addClaim(claim, summary='BOT - Adding 1 claim')
        print('Adding %s = %s to %s' % (p, target.title(), item.title()))

def main():
    wikimedia = {
        'Wikinews': {
            'dbsuffix': 'wikinews', 
            'domain': 'wikinews.org', 
            'familyq': 'Q20671729', 
            'tablepage': 'Wikinews/Table', 
        }, 
    }
    a = {
        'Wikibooks': {
            'dbsuffix': 'wikibooks', 
            'domain': 'wikibooks.org', 
            'familyq': 'Q22001316', 
            'tablepage': 'Wikibooks/Table', 
        }, 
        'Wiktionary': {
            'dbsuffix': 'wiktionary', 
            'dbsuffix2': 'wikt', 
            'domain': 'wiktionary.org', 
            'familyq': 'Q22001389', 
            'tablepage': 'Wiktionary/Table', 
        }, 
    }
    wikisite = pywikibot.Site('meta', 'meta')
    enwpsite = pywikibot.Site('en', 'wikipedia')
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    repo = wdsite.data_repository()
    
    #available projects in wikidata
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%20%3FitemLabel%20%3Fdb%0AWHERE%20%7B%0A%20%20%20%20%23%3Fitem%20wdt%3AP31%20wd%3AQ22001389.%0A%20%20%20%20%3Fitem%20wdt%3AP1800%20%3Fdb.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%2Cen%22.%20%7D%0A%7D'
    url = '%s&format=json' % (url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)
    projects = {}
    for result in json1['results']['bindings']:
        #print(result)
        q = result['item']['value'].split('/entity/')[1]
        label = result['itemLabel']['value']
        db = result['db']['value']
        projects[db] = {'q':q, 'db':db, 'label':label}
    print('Loaded %d projects' % (len(projects.items())))
    
    for projname, projprops in wikimedia.items():
        metapage = pywikibot.Page(wikisite, projprops['tablepage'])
        metatable = metapage.text
        m = re.findall(r'(?im)\[\[w:([^\[\]]+? language)\|([^\[\]]+?)\]\]\s*\|\s*\[\[w:[^\[\]]+? language\|([^\[\]]+?)\]\]\s*\|\s*\[//([^\.]+)\.[^\.]+\.org/wiki/ ([^\[\]]+)\]', metatable)
        for i in m:
            lang_art = i[0]
            lang_en = i[1]
            lang_orig = i[2]
            lang_iso = i[3]
            db_ = '%s%s' % (re.sub('-', '_', lang_iso), projprops['dbsuffix'])
            if 'dbsuffix2' in projprops:
                db2_ = '%s%s' % (re.sub('-', '_', lang_iso), projprops['dbsuffix2'])
            else:
                db2_ = ''
            domain = '%s.%s' % (lang_iso, projprops['domain'])
            item = ''
            if db_ in projects:
                print('%s is in Wikidata' % (db_))
                item = pywikibot.ItemPage(site=repo, title=projects[db_]['q'])
                try:
                    item.get()
                except:
                    print('Error en %s' % (projects[db_].items()))
            else:
                newitemlabels = { 'en': '%s %s' % (lang_en, projname) }
                item = pywikibot.ItemPage(repo)
                item.editLabels(labels=newitemlabels, summary="BOT - Creating item for %s project" % (projname))
                item.get()
            
            aliases = item.aliases
            if not 'en' in aliases:
                aliases['en'] = []
            aliasesnum = 0
            if 'en' in aliases:
                if db_ and not db_ in aliases['en']:
                    aliases['en'].append(db_)
                    aliasesnum += 1
                if db2_ and not db2_ in aliases['en']:
                    aliases['en'].append(db2_)
                    aliasesnum += 1
                if domain and not domain in aliases['en']:
                    aliases['en'].append(domain)
                    aliasesnum += 1
                if aliasesnum:
                    data = { 'aliases': aliases }
                    item.editEntity(data, summary="BOT - Adding %s aliases" % (aliasesnum))
            
            try:
                langpage = pywikibot.Page(enwpsite, lang_art)
                if langpage.isRedirectPage():
                    langpage = langpage.getRedirectTarget()
                langq = pywikibot.ItemPage.fromPage(langpage)
            except:
                continue
            
            claims = item.claims
            if not claims or not 'P31' in item.claims:
                addclaim(repo=repo, item=item, p='P31', q=projprops['familyq']) #project
            if not claims or not 'P407' in item.claims:
                addclaim(repo=repo, item=item, p='P407', q=langq.title()) #lang
            if not claims or not 'P127' in item.claims:
                addclaim(repo=repo, item=item, p='P127', q='Q180') #owner
            if not claims or not 'P424' in item.claims:
                addclaim(repo=repo, item=item, p='P424', s=lang_iso) #wm lang code
            if not claims or not 'P856' in item.claims:
                addclaim(repo=repo, item=item, p='P856', s='https://%s.%s/' % (lang_iso, projprops['domain'])) #website
            if not claims or not 'P1800' in item.claims:
                addclaim(repo=repo, item=item, p='P1800', s=db_) #db
            
            #print(lang_art, lang_en, lang_orig, lang_iso)

if __name__ == "__main__":
    main()

