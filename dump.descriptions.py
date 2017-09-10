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

import bz2
import json
import sys
import time

import pywikibot

def getP31(json1={}):
    p31 = []
    if 'claims' in json1:
        if 'P31' in json1['claims']:
            for x in json1['claims']['P31']:
                if 'mainsnak' in x and \
                   'datavalue' in x['mainsnak'] and \
                   'value' in x['mainsnak']['datavalue'] and \
                   'id' in x['mainsnak']['datavalue']['value']:
                    p31.append(x['mainsnak']['datavalue']['value']['id'])
    return p31

def main():
    wdsite = pywikibot.Site('wikidata', 'wikidata')
    descriptions = {}
    dumpdate = sys.argv[1]
    f = bz2.open('/public/dumps/public/wikidatawiki/entities/%s/wikidata-%s-all.json.bz2' % (dumpdate, dumpdate), 'r')
    c = 0
    for line in f:
        c += 1
        line = line.decode('utf-8')
        line = line.strip('\n').strip(',')
        if line.startswith('{') and line.endswith('}'):
            json1 = json.loads(line)
            q = json1['id']
            p31 = getP31(json1=json1)
            if len(p31) != 1:
                continue
            p31 = p31[0]
            if 'descriptions' in json1:
                if 'en' in json1['descriptions']:
                    descen = '%s\t%s' % (p31, json1['descriptions']['en']['value'])
                    if len(descen.split(' ')) > 3:
                        continue
                    desces = ''
                    if 'es' in json1['descriptions']:
                        desces = json1['descriptions']['es']['value']
                    if descen in descriptions:
                        if desces in descriptions[descen]:
                            descriptions[descen][desces] += 1
                        else:
                            descriptions[descen][desces] = 1
                    else:
                        if desces == '':
                            descriptions[descen] = {desces: 1}
                        else:
                            descriptions[descen] = {desces: 1, '': 0}
        #if c > 15000:
        #    break
    
    candidates = []
    for descen, translations in descriptions.items():
        translations_list = []
        for k, v in translations.items():
            if k != '':
                translations_list.append([v, k])
        if translations_list:
            translations_list.sort(reverse=True)
            if translations_list[0][0] > 10 and \
                translations_list[0][0] > sum([i[0] for i in translations_list[1:]])*9:
                candidates.append([translations[''], descen, translations_list[0][1], translations_list[0][0], translations['']])
    candidates.sort(reverse=True)
    output = '\n'.join(['\t'.join([str(x) for x in candidate[1:]]) for candidate in candidates[:40]])
    with open('dump.descriptions.txt', 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == '__main__':
    main()
