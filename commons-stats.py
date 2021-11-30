#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 emijrp <emijrp@gmail.com>
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
import time
import urllib

import pywikibot
from pywikibot import pagegenerators

#stats de mis fotos subidas en base a la plantilla /credit y sus parametros
#ciudades a las que he ido, q año, cuantos dias distintos
#mayor numero de fotos en un día, en una ciudad, etc
#en que categorias estan mis fotos (Collections of museum of...)
#volcar todo eso en una pagina resumen User:Emijrp/Statistics

cities2catname = {
    "Alcala de Henares": "Alcalá de Henares", 
    "Aranjuez": "Aranjuez",
    "Avila": "Ávila", 
    "Barcelona": "Barcelona", 
    "Benalup Casas Viejas": "Benalup-Casas Viejas", 
    "Burgos": "Burgos", 
    "Caceres": "Cáceres", 
    "Cadiz": "Cádiz", 
    "Chipiona": "Chipiona", 
    "El Puerto de Santa Maria": "El Puerto de Santa María", 
    "Espera": "Espera", 
    "Estepona": "Estepona", 
    "Guadalajara": "Guadalajara", 
    "Jerez": "Jerez de la Frontera", 
    "Madrid": "Madrid", 
    "Malaga": "Málaga", 
    "Medina Sidonia": "Medina-Sidonia", 
    "Puerto Real": "Puerto Real", 
    "Rota": "Rota", 
    "Salamanca": "Salamanca", 
    "Sanlucar de Barrameda": "Sanlúcar de Barrameda", 
    "Segovia": "Segovia", 
    "Sevilla": "Sevilla", 
    "Seville": "Sevilla", 
    "Toledo": "Toledo", 
    "Valladolid": "Valladolid", 
    "Vejer": "Vejer de la Frontera", 
    "Vejer de la Frontera": "Vejer de la Frontera", 
}
monthnum2monthname = { '01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December' }
categories = {}
cities = {}
devices = {}
months = {}
years = {}

def main():
    commons = pywikibot.Site('commons', 'commons')
    category = pywikibot.Category(commons, 'Files by User:Emijrp')
    gen = pagegenerators.CategorizedPageGenerator(category)
    c = 0
    for page in gen:
        c += 1
        print('==', page.title(), '==')
        wtext = page.text
        
        #categories
        m = re.findall(r'(?im)\[\[\s*Category\s*\:\s*([^\[\]\|]*?)\s*[\|\]]', wtext)
        for category in m:
            if len(category) > 1:
                category = category[0].upper() + category[1:]
            else:
                category = category.upper()
            if category in categories.keys():
                categories[category] += 1
            else:
                categories[category] = 1
        
        #params in credit template
        m = re.findall(r'(?im){{User:Emijrp/credit([^\{\}]*?)}}', wtext)
        if not m:
            continue
        params = m[0].split('|')
        for param in params:
            print(param)
            if '=' not in param:
                continue
            key = param.split('=')[0]
            value = param.split('=')[1]
            #print(key, value)
            if key == "date":
                year = value.split('-')[0]
                if year in years.keys():
                    years[year] += 1
                else:
                    years[year] = 1
                month = value.split('-')[1]
                if month in months.keys():
                    months[month] += 1
                else:
                    months[month] = 1
            elif key == "device":
                if value in devices.keys():
                    devices[value] += 1
                else:
                    devices[value] = 1
            elif key == "city":
                if value in cities.keys():
                    cities[value] += 1
                else:
                    cities[value] = 1
            else:
                pass
        
        if c > 500: #test
            break
    
    categories_list = []
    for k, v in categories.items():
        categories_list.append([v, k])
    categories_list.sort(reverse=True)
    catstable = ""
    c = 1
    for freq, category in categories_list[:100]:
        if freq < 10:
            break
        catstable += "\n|-\n| %s || [[:Category:%s|%s]] || %s" % (c, category, category, freq)
        c += 1
    
    cities_list = []
    for k, v in cities.items():
        cities_list.append([v, k])
    cities_list.sort(reverse=True)
    citiestable = ""
    c = 1
    for freq, city in cities_list:
        city_ = city in cities2catname and cities2catname[city] or city
        citiestable += "\n|-\n| %s || [[:Category:Images of %s by User:Emijrp|%s]] ([[:en:%s|en]]) || %s" % (c, city_, city_, city_, freq)
        c += 1
    
    years_list = []
    for k, v in years.items():
        years_list.append([k, v])
    years_list.sort()
    yearsx = ','.join([str(k) for k, v in years_list])
    yearsy = ','.join([str(v) for k, v in years_list])
    
    months_list = []
    for k, v in months.items():
        months_list.append([k, v])
    months_list.sort()
    monthsx = ','.join([monthnum2monthname[str(k)] for k, v in months_list])
    monthsy = ','.join([str(v) for k, v in months_list])
    
    devices_list = []
    for k, v in devices.items():
        devices_list.append([k, v])
    devices_list.sort()
    devicesx = ','.join([str(k) for k, v in devices_list])
    devicesy = ','.join([str(v) for k, v in devices_list])
    
    #https://glamtools.toolforge.org/glamorous.php?doit=1&category=Files+by+User%3AEmijrp&use_globalusage=1&ns0=1&format=xml
    usage = """"""
    
    page = pywikibot.Page(commons, "User:Emijrp/Statistics")
    newtext = """
'''Statistics''' for [[:Category:Files by User:Emijrp]].
%s
== Files ==
=== By year ===
{{Graph:Chart|width=800|height=200|xAxisTitle=Year|yAxisTitle=Files|type=rect|x=%s|y=%s}}
=== By month ===
{{Graph:Chart|width=800|height=200|xAxisTitle=Month|yAxisTitle=Files|type=rect|x=%s|y=%s}}
=== By device ===
{{Graph:Chart|width=100|height=100|type=pie|legend=Legend|x=%s|y1=%s|showValues=}}

== Most frequent ==
{| style="text-align: center;"
| valign=top |
{| class="wikitable sortable" width="400px"
! # !! Category !! Files%s
|}
| valign=top |
{| class="wikitable sortable" width="400px"
! # !! City !! Files%s
|}
|}
""" % (usage, yearsx, yearsy, monthsx, monthsy, devicesx, devicesy, catstable, citiestable)
    if newtext != page.text:
        pywikibot.showDiff(page.text, newtext)
        page.text = newtext
        page.save('BOT - Updating stats')

if __name__ == '__main__':
    main()
