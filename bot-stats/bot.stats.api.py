#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2023 emijrp <emijrp@gmail.com>
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

import csv
import datetime
import json
import os
import re
import sys
import time
import urllib
import urllib.request

import pywikibot

diffs2langs = {}
regexps = {
    'aliases': re.compile(r"(?i)BOT - Adding ([0-9]+) alias"), 
    'claims': re.compile(r"(?i)BOT - Adding ([0-9]+) claim"), 
    'descriptions': re.compile(r"(?i)BOT - Adding descriptions? \(([0-9]+) languages?\)"), 
    'labels': re.compile(r"(?i)BOT - Adding labels? \(([0-9]+) languages?\)"), 
    'references': re.compile(r"(?i)BOT - Adding ([0-9]+) reference"), 
    'sitelinks': re.compile(r"(?i)BOT - Adding ([0-9]+) sitelink"), 
    'items': re.compile(r"(?i)BOT - Creating item"), 
}
regexps2 = {
    'difflangs': re.compile(r'(?im) ([a-z-]+?) / </td></tr><tr><td colspan="2">&nbsp;</td><td class="diff-marker" data-marker="+">'), 
}

def loadNewestEditId(nick='', path=''):
    newesteditid = 0
    newesteditdate = 0
    if nick and path and os.path.exists('%s/%s-edits.csv' % (path, nick)):
        with open('%s/%s-edits.csv' % (path, nick), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                #print(', '.join(row))
                if int(row[0]) > newesteditid:
                    newesteditid = int(row[0])
                    newesteditdate = row[1]
    return newesteditid, newesteditdate

def loadOldestEditId(nick='', path=''):
    oldesteditid = 99999999999999
    oldesteditdate = 99999999999999
    if nick and path and os.path.exists('%s/%s-edits.csv' % (path, nick)):
        with open('%s/%s-edits.csv' % (path, nick), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                #print(', '.join(row))
                if int(row[0]) < oldesteditid:
                    oldesteditid = int(row[0])
                    oldesteditdate = row[1]
    return oldesteditid, oldesteditdate

def saveEdits(nick='', path='', edits=''):
    if nick and path and edits:
        with open('%s/%s-edits.csv' % (path, nick), 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar ='"')
            csvwriter.writerows(edits)

def calculateTopDay(days={}):
    dayslist = [[v, k] for k, v in days.items()]
    dayslist.sort(reverse=True)
    return [dayslist[0][1], dayslist[0][0]]

def getLanguagesFromDiff(revid='', comment=''):
    #https://www.wikidata.org/w/index.php?diff=prev&oldid=1521460418
    #https://www.wikidata.org/w/index.php?diff=prev&oldid=1521456307 tt-latn, ur / Fixing descriptions (1 languages): uk
    global diffs2langs
    global regexps
    global regexps2
    
    langsfromdiff = []
    if revid and comment:
        nlangs = re.findall(r'(?im)\((\d+?) languages\)', comment)
        nlangs = nlangs and nlangs[0] or 0
        if comment in diffs2langs:
            langsfromdiff = diffs2langs[comment]
        else:
            diffurl = 'https://www.wikidata.org/w/index.php?oldid=%s&diff=prev' % (revid)
            raw = urllib.request.urlopen(diffurl).read().decode('utf-8')
            m = regexps2['difflangs'].findall(raw)
            for lang in m:
                lang = lang.strip()
                if len(lang) >= 2 and not '.' in lang:
                    langsfromdiff.append(lang)
            if nlangs and len(langsfromdiff) == nlangs:
                diffs2langs[comment] = langsfromdiff
    return langsfromdiff

def main():
    global regexps
    global regexps2
    
    path = '.'
    nick = 'Emijrpbot'
    nick_ = re.sub(' ', '_', nick)
    #load saved edits
    newesteditid, newesteditdate = loadNewestEditId(nick=nick, path=path)
    oldesteditid, oldesteditdate = loadOldestEditId(nick=nick, path=path)
    print('%d newest edit id, %s' % (newesteditid, newesteditdate))
    print('%d oldest edit id, %s' % (oldesteditid, oldesteditdate))
    
    #load missing edits
    api = 'https://www.wikidata.org/w/api.php'
    apiqueries = []
    apiqueries.append('?action=query&list=usercontribs&ucuser=%s&uclimit=500&ucprop=timestamp|title|comment|ids&format=json' % (nick))
    if oldesteditid > 442787986:
        #complete csv if oldestedit isn't <= 2017-02-06 or <= 442787986
        #https://www.wikidata.org/w/index.php?title=Special:Contributions/Emijrpbot&target=Emijrpbot&dir=prev
        apiqueries.append('?action=query&list=usercontribs&ucuser=%s&uclimit=500&ucstart=%s&ucprop=timestamp|title|comment|ids&format=json' % (nick, oldesteditdate))
    
    for apiquery in apiqueries:
        uccontinue = True
        uccontinue_name = 'uccontinue'
        total = 0
        edits = []
        while uccontinue:
            if len(edits) >= 10000:
                saveEdits(nick=nick, path=path, edits=edits)
                edits = []
            if uccontinue == True:
                json_data = urllib.request.urlopen(api+apiquery)
            else:
                try:
                    json_data = urllib.request.urlopen(api+apiquery+'&'+uccontinue_name+'='+uccontinue)
                except:
                    time.sleep(10)
                    try:
                        json_data = urllib.request.urlopen(api+apiquery+'&'+uccontinue_name+'='+uccontinue)
                    except:
                        uccontinue = ''
                        break
            data = json.loads(json_data.read().decode('utf-8'))
            for edit in data['query']['usercontribs']:
                if edit['revid'] == newesteditid:# no hace falta una comparacion como esta con oldesteditit pq terminará de cargar cuando la api no le devuelva más
                    uccontinue = ''
                    break
                d = datetime.datetime.strptime(edit['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
                #d = datetime.datetime.strptime(edit['timestamp'].split('T')[0], "%Y-%m-%d")
                unixtime = d.strftime('%s')
                if 'revid' in edit and 'timestamp' in edit and 'comment' in edit: #si han ocultado el comentario en el historial por ej. fallaría sin este if
                    edits.append([edit['revid'], edit['timestamp'], edit['comment'].encode('utf-8')])
                    total += 1
            json_data.close()
            if uccontinue:
                if 'query-continue' in data:
                    if not uccontinue_name in data['query-continue']['usercontribs']:
                        uccontinue_name = 'ucstart'
                    uccontinue = data['query-continue']['usercontribs'][uccontinue_name]
                elif 'continue' in data:
                    uccontinue = data['continue'][uccontinue_name]
                else:
                    uccontinue = ''
            print('%s edits' % (total))
        print('%s edits. Finished' % (total))
        if edits:
            saveEdits(nick=nick, path=path, edits=edits)
        edits = []
    
    stats = { 'edits': 0, 'aliases': 0, 'claims': 0, 'descriptions': 0, 'labels': 0, 'references': 0, 'sitelinks': 0, 'items': 0 }
    statsbyday = { 'edits': {}, 'aliases': {}, 'claims': {}, 'descriptions': {}, 'labels': {}, 'references': {}, 'sitelinks': {}, 'items': {}, 'total': {} }
    statsprev = { 'edits': 0, 'aliases': 0, 'claims': 0, 'descriptions': 0, 'labels': 0, 'references': 0, 'sitelinks': 0, 'items': 0 }
    statsbylang = {}
    site = pywikibot.Site('wikidata', 'wikidata')
    statspage = pywikibot.Page(site, 'User:Emijrpbot/stats')
    statsbylangpage = pywikibot.Page(site, 'User:Emijrpbot/statsbylang')
    for statsprop in statsprev.keys():
        statsprev[statsprop] = int(re.findall(r"(?im)%s[^\n\{]+?{{formatnum:(\d+)}}" % (statsprop), statspage.text)[0])
    
    #848135050,2019-02-01T10:14:31Z,"/* wbeditentity-update:0| */ BOT - Adding descriptions (57 languages): ar, ast, bg, bn, ca, cs, da, de, el, eo, es, et, fa, fi, fr, gl, he, hu, hy, it, ja, ka, ko, lt, nan, nb, nn, oc, pl, pt, pt-br, ro, ru, sk, sq, sr, sr-ec, sr-el, sv, tg, tg-cyrl, th, tl, tr, ur, vi, wuu, yue, zh, zh-cn, zh-hans, zh-hant, zh-hk, zh-mo, zh-my, zh-sg, zh-tw"
    if os.path.exists('%s/%s-edits.csv' % (path, nick)):
        with open('%s/%s-edits.csv' % (path, nick), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                revid = row[0]
                timestamp = row[1]
                comment = row[2]
                
                day = timestamp.split('T')[0]
                for statsbydayprop in statsbyday.keys():
                    if not day in statsbyday[statsbydayprop]:
                        statsbyday[statsbydayprop][day] = 0
                
                langsincomment = []
                if 'languages):' in comment:
                    langsincomment = comment.split('languages):')[1].split('/')[0]
                    langsincomment = langsincomment.split(',')
                    #comentado hasta que optimice lo del diff
                    #if '...' in comment:
                    #    langsfromdiff = getLanguagesFromDiff(revid=revid, comment=comment)
                    #    if len(langsfromdiff) > 0:
                    #        langsincomment = langsfromdiff
                elif 'aliases (' in comment:
                    langsincomment = [comment.split('aliases (')[1].split(')')[0]]
                langsincomment2 = []
                for langincomment in langsincomment:
                    langincomment = langincomment.strip(' ').strip("'").strip(' ').strip("'")
                    if not '.' in langincomment: #evitar idiomas cortados por el límite del resumen en-c...
                        langsincomment2.append(langincomment)
                langsincomment = langsincomment2
                
                for regexpname, regexp in regexps.items():
                    m = regexp.findall(comment)
                    if regexpname == 'items':
                        stats[regexpname] += m and 1 or 0
                        statsbyday[regexpname][day] += m and 1 or 0
                        statsbyday['total'][day] += m and 1 or 0
                    else:
                        stats[regexpname] += m and int(m[0]) or 0
                        statsbyday[regexpname][day] += m and int(m[0]) or 0
                        statsbyday['total'][day] += m and int(m[0]) or 0
                    if m and regexpname in ['aliases', 'descriptions', 'labels']:
                        for langincomment in langsincomment:
                            if not langincomment in statsbylang:
                                statsbylang[langincomment] = { 'aliases': 0, 'descriptions': 0, 'labels': 0 }
                            if regexpname == 'aliases':
                                naliases = re.findall(r'(?im) (\d+?) aliases', comment)
                                naliases = naliases and int(naliases[0]) or 1
                                statsbylang[langincomment][regexpname] += naliases
                            else:
                                statsbylang[langincomment][regexpname] += 1
                
                stats['edits'] += 1
                statsbyday['edits'][day] += 1
                if stats['edits'] % 100000 == 0:
                    print('%s edits analysed' % (stats['edits']))
                    #break
    
    formatdict = { 'total': 0, 'difftotal': 0 }
    for k, v in stats.items():
        formatdict[k] = v
        if k in ['aliases', 'claims', 'descriptions', 'items', 'labels', 'references', 'sitelinks']:
            formatdict['total'] += v
        formatdict['diff'+k] = v - statsprev[k]
        formatdict['difftotal'] += formatdict['diff'+k]
        topday = calculateTopDay(days=statsbyday[k])
        formatdict['topday'+k+'day'] = topday[0]
        formatdict['topday'+k+'value'] = topday[1]
    topday = calculateTopDay(days=statsbyday['total'])
    formatdict['topdaytotalday'] = topday[0]
    formatdict['topdaytotalvalue'] = topday[1]
    formatdict['nick'] = nick
    formatdict['nick_'] = nick_
    formatdict['lastupdate'] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    output = """{{| class="wikitable sortable plainlinks" style="text-align: center;"
! colspan=5 | Statistics for [[User:{nick}|{nick}]] by data
|-
! rowspan=2 | Data
! colspan=2 | Values added
! colspan=2 | TOP days
|-
! Total
! Today
! Values added
! Date
|-
| '''[[Help:Label|Labels]]''' || data-sort-value={labels} | {{{{formatnum:{labels}}}}}
| data-sort-value={difflabels} | +{{{{formatnum:{difflabels}}}}}
| data-sort-value={topdaylabelsvalue} | +{{{{formatnum:{topdaylabelsvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdaylabelsday}&limit=100&title=Special:Contributions {topdaylabelsday}]
|-
| '''[[Help:Description|Descriptions]]''' || data-sort-value={descriptions} | {{{{formatnum:{descriptions}}}}}
| data-sort-value={diffdescriptions} | +{{{{formatnum:{diffdescriptions}}}}}
| data-sort-value={topdaydescriptionsvalue} | +{{{{formatnum:{topdaydescriptionsvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdaydescriptionsday}&limit=100&title=Special:Contributions {topdaydescriptionsday}]
|-
| '''[[Help:Aliases|Aliases]]''' || data-sort-value={aliases} | {{{{formatnum:{aliases}}}}}
| data-sort-value={diffaliases} | +{{{{formatnum:{diffaliases}}}}}
| data-sort-value={topdayaliasesvalue} | +{{{{formatnum:{topdayaliasesvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdayaliasesday}&limit=100&title=Special:Contributions {topdayaliasesday}]
|-
| '''[[Help:Statements|Claims]]''' || data-sort-value={claims} | {{{{formatnum:{claims}}}}}
| data-sort-value={diffclaims} | +{{{{formatnum:{diffclaims}}}}}
| data-sort-value={topdayclaimsvalue} | +{{{{formatnum:{topdayclaimsvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdayclaimsday}&limit=100&title=Special:Contributions {topdayclaimsday}]
|-
| '''[[Help:Sitelinks|Sitelinks]]''' || data-sort-value={sitelinks} | {{{{formatnum:{sitelinks}}}}}
| data-sort-value={diffsitelinks} | +{{{{formatnum:{diffsitelinks}}}}}
| data-sort-value={topdaysitelinksvalue} | +{{{{formatnum:{topdaysitelinksvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdaysitelinksday}&limit=100&title=Special:Contributions {topdaysitelinksday}]
|-
| '''[[Help:Items|Items]]''' || data-sort-value={items} | [https://www.wikidata.org/w/index.php?title=Special:NewPages&namespace=0&username={nick_} {{{{formatnum:{items}}}}}]
| data-sort-value={diffitems} | +{{{{formatnum:{diffitems}}}}}
| data-sort-value={topdayitemsvalue} | +{{{{formatnum:{topdayitemsvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=1&start=&end={topdayitemsday}&limit=100&title=Special:Contributions {topdayitemsday}]
|-
| '''[[Help:Sources|References]]''' || data-sort-value={references} | {{{{formatnum:{references}}}}}
| data-sort-value={diffreferences} | +{{{{formatnum:{diffreferences}}}}}
| data-sort-value={topdayreferencesvalue} | +{{{{formatnum:{topdayreferencesvalue}}}}}
| [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdayreferencesday}&limit=100&title=Special:Contributions {topdayreferencesday}]
|-
! '''Total''' !! data-sort-value={total} | {{{{formatnum:{total}}}}}
! data-sort-value={difftotal} | +{{{{formatnum:{difftotal}}}}}
! data-sort-value={topdaytotalvalue} | +{{{{formatnum:{topdaytotalvalue}}}}}
! [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdaytotalday}&limit=100&title=Special:Contributions {topdaytotalday}]
|-
! '''Edits''' !! data-sort-value={edits} | [[Special:Contributions/Emijrpbot|{{{{formatnum:{edits}}}}}]]
! data-sort-value={diffedits} | +{{{{formatnum:{diffedits}}}}}
! data-sort-value={topdayeditsvalue} | +{{{{formatnum:{topdayeditsvalue}}}}}
! [https://www.wikidata.org/w/index.php?target={nick_}&namespace=all&tagfilter=&newOnly=0&start=&end={topdayeditsday}&limit=100&title=Special:Contributions {topdayeditsday}]
|-
! colspan=5 | Last update: {lastupdate}
|}}""".format(**formatdict)
    summary = "BOT - Updating stats: Edits (+{diffedits}), Labels (+{difflabels}), Descriptions (+{diffdescriptions}), Aliases (+{diffaliases}), Claims (+{diffclaims}), Sitelinks (+{diffsitelinks}), Items (+{diffitems}), References (+{diffreferences})".format(**formatdict)
    print(output)
    statspage.text = output
    statspage.save(summary)
    
    statsbylanglist = []
    for lang, langprops in statsbylang.items():
        langtotal = langprops['labels'] + langprops['descriptions'] + langprops['aliases']
        langstats = [langtotal, lang, langprops['labels'], langprops['descriptions'], langprops['aliases']]
        statsbylanglist.append(langstats)
    statsbylanglist.sort(reverse=True)
    
    statsbylangtable = ''
    formatdictbylang = {
        'labels': formatdict['labels'], 'descriptions': formatdict['descriptions'], 'aliases': formatdict['aliases'], 'total': formatdict['total'], 
        'subtotallabels': 0, 'subtotaldescriptions': 0, 'subtotalaliases': 0, 'subtotaltotal': 0, 
    }
    for langtotal, lang, langlabels, langdescriptions, langaliases in statsbylanglist:
        formatdictlang = { 'langlabels': langlabels, 'lang': lang, 'lang_': lang.split('-')[0], 'langdescriptions': langdescriptions, 'langaliases': langaliases, 'langtotal': langtotal }
        formatdictbylang['subtotallabels'] += langlabels
        formatdictbylang['subtotaldescriptions'] += langdescriptions
        formatdictbylang['subtotalaliases'] += langaliases
        formatdictbylang['subtotaltotal'] += langtotal
        statsbylangtable += """
| data-sort-value={lang} | [[:{lang_}:|{{{{#language:{lang}|en}}}}]] ({lang})
| data-sort-value={langlabels} | {{{{formatnum:{langlabels}}}}}
| data-sort-value={langdescriptions} | {{{{formatnum:{langdescriptions}}}}}
| data-sort-value={langaliases} | {{{{formatnum:{langaliases}}}}}
| data-sort-value={langtotal} | {{{{formatnum:{langtotal}}}}}
|-""".format(**formatdictlang)
    
    formatdictbylang['nick'] = formatdict['nick']
    formatdictbylang['nick_'] = formatdict['nick_']
    formatdictbylang['lastupdate'] = formatdict['lastupdate']
    formatdictbylang['statsbylangtable'] = statsbylangtable
    formatdictbylang['numberoflangs'] = len(statsbylang.keys())
    outputbylang = """{{| class="wikitable sortable plainlinks" style="text-align: center;"
! colspan=5 | Statistics for [[User:{nick}|{nick}]] by language
|-
! width=140px | Language
! [[Help:Label|Labels]]
! [[Help:Description|Descriptions]]
! [[Help:Aliases|Aliases]]
! Total
|-{statsbylangtable}
! '''Subtotal ({numberoflangs} langs)''' !! data-sort-value={subtotallabels} | {{{{formatnum:{subtotallabels}}}}}
! data-sort-value={subtotaldescriptions} | {{{{formatnum:{subtotaldescriptions}}}}}
! data-sort-value={subtotalaliases} | {{{{formatnum:{subtotalaliases}}}}}
! data-sort-value={subtotaltotal} | {{{{formatnum:{subtotaltotal}}}}}
|-
! '''Total ({numberoflangs} langs)''' !! data-sort-value={labels} | {{{{formatnum:{labels}}}}}
! data-sort-value={descriptions} | {{{{formatnum:{descriptions}}}}}
! data-sort-value={aliases} | {{{{formatnum:{aliases}}}}}
! data-sort-value={total} | {{{{formatnum:{total}}}}}
|-
! colspan=5 | Last update: {lastupdate}
|}}""".format(**formatdictbylang)
    summarybylang = "BOT - Updating stats by language"
    print(outputbylang)
    statsbylangpage.text = outputbylang
    statsbylangpage.save(summarybylang)

if __name__ == "__main__":
    main()
