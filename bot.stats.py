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

import datetime

import pwb
import pywikibot

def main():
    site = pywikibot.Site('wikidata', 'wikidata')
    stats = {}
    
    with open('bot.stats.txt') as f:
        raw = f.read()
    
    for l in raw.splitlines():
        x, y = l.strip().split('=')
        x = x.strip().lower()
        y = y.strip()
        stats[x] = y and int(y) or 0
    
    output = """{| class="wikitable sortable" style="text-align: center;"
|-
| '''Edits''' || [[Special:Contributions/Emijrpbot|{{formatnum:%s}}]]
|-
| '''[[Help:Label|Labels]]''' || {{formatnum:%s}}
|-
| '''[[Help:Description|Descriptions]]''' || {{formatnum:%s}}
|-
| '''[[Help:Aliases|Aliases]]''' || {{formatnum:%s}}
|-
| '''[[Help:Statements|Claims]]''' || {{formatnum:%s}}
|-
| '''[[Help:Sitelinks|Sitelinks]]''' || {{formatnum:%s}}
|-
| '''[[Help:Items|Items]]''' || {{formatnum:%s}}
|-
| colspan=2 | <small>Last update: %s</small>
|}""" % (stats['edits'], stats['labels'], stats['descriptions'], stats['aliases'], stats['claims'], stats['sitelinks'], stats['items'], datetime.datetime.now().strftime('%Y-%m-%d'))
    
    page = pywikibot.Page(site, 'User:Emijrpbot/stats')
    page.text = output
    page.save('BOT - Updating stats')

if __name__ == "__main__":
    main()
