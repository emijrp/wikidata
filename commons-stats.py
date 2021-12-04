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

import datetime
import re
import time
import urllib

import pywikibot
from pywikibot import pagegenerators

#stats de mis fotos subidas en base a la plantilla /credit y sus parametros
#ciudades a las que he ido, q año, cuantos dias distintos
#mayor numero de fotos en un día, en una ciudad, etc
#en que categorias estan mis fotos (Collections of museum of...)

cities2catname = {
    "Alcala de Henares": "Alcalá de Henares", 
    "Avila": "Ávila", 
    "Benalup Casas Viejas": "Benalup-Casas Viejas", 
    "Caceres": "Cáceres", 
    "Cadiz": "Cádiz", 
    "Cordoba": "Córdoba", 
    "El Puerto de Santa Maria": "El Puerto de Santa María", 
    "Jerez": "Jerez de la Frontera", 
    "Malaga": "Málaga", 
    "Medina Sidonia": "Medina-Sidonia", 
    "Sanlucar de Barrameda": "Sanlúcar de Barrameda", 
    "Sevilla": "Seville", 
    "Vejer": "Vejer de la Frontera", 
    "Villar de Domingo Garcia": "Villar de Domingo García", 
    "Unknown": "other places", 
}
devices2catname = {
    "X-3,C-60Z": "Olympus X-3 / C-60Z", 
    "u5000": "Olympus u5000", 
    "NIKON D3100": "NIKON D3100", #"Nikon D3100", 
    "TASSVE": "mobile phones", #"Samsung Galaxy Mini", 
    "LG-X220": "mobile phones", #"LG K5", 
    "OPPO A9 2020": "mobile phones", #"Oppo A9 2020", 
    "Jiusion Digital Microscope": "microscopes", 
    "Unknown": "unknown",
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
    total = 0
    for page in gen:
        print('==', page.title(), '==')
        wtext = page.text
        
        #params in credit template
        m = re.findall(r'(?im){{User:Emijrp/credit([^\{\}]*?)}}', wtext)
        if not m:
            continue
        total += 1
        params = m[0].split('|')
        date = ""
        device = "Unknown"
        city = "Unknown"
        for param in params:
            if '=' not in param:
                continue
            print(param)
            key = param.split('=')[0].lower()
            value = param.split('=')[1]
            #print(key, value)
            if key == "date":
                date = value
            elif key == "device":
                device = value
            elif key == "city":
                city = value
            else:
                pass
        
        if date:
            year = date.split('-')[0]
            if year in years:
                years[year]["total"] += 1
                if city in years[year]:
                    years[year][city] += 1
                else:
                    years[year][city] = 1
            else:
                years[year] = { "total": 1, city: 1 }
            month = date.split('-')[1]
            if month in months:
                months[month] += 1
            else:
                months[month] = 1
        if device:
            device = device in devices2catname.keys() and devices2catname[device] or device
            if device in devices:
                devices[device] += 1
            else:
                devices[device] = 1
        if city:
            if city in cities:
                cities[city] += 1
            else:
                cities[city] = 1
        
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
        
        if total >= 50000: #test
            break
    
    categories_list = []
    institutions_list = []
    for k, v in categories.items():
        categories_list.append([v, k])
        if k.startswith('Collections of the '):
            institutions_list.append(k.split('Collections of the ')[1])
        elif k.startswith('Interior of the '):
            institutions_list.append(k.split('Interior of the ')[1])
        elif k.startswith('Exterior of the '):
            institutions_list.append(k.split('Exterior of the ')[1])
        elif k.startswith('Archivo ') or k.startswith('Biblioteca ') or k.startswith('Centro Cultural ') or k.startswith('Museo ') or k.startswith('Museum '):
            institutions_list.append(k)
        else:
            pass
    categories_list.sort(reverse=True)
    institutions_list.sort()
    catstable = ""
    c = 1
    for freq, category in categories_list[:100]:
        if freq < 10:
            break
        catstable += "\n|-\n| %s || [[:Category:%s|%s]] || %s" % (c, category, category, freq)
        c += 1
    catstable = """{| id="Categories" class="wikitable sortable" width="400px"\n! # !! Category !! Files%s\n|}""" % (catstable)
    institutionstable = ", ".join(["{{[[Institution:%s|%s]]}}" % (institution, institution) for institution in institutions_list])
    
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
    citiestable = """{| id="Cities" class="wikitable sortable" width="400px"\n! # !! City !! Files%s\n|}""" % (citiestable)
    
    years_list = []
    for k, v in years.items():
        years_list.append([k, v["total"]])
    years_list.sort()
    yearsx = [str(k) for k, v in years_list]
    yearsy = [str(v) for k, v in years_list]
    yearscities = []
    for k, v in years_list:
        yearcities = []
        for city in years[k].keys():
            if city != 'total':
                yearcities.append([city, years[k][city]])
        yearcities.sort()
        yearscities.append(', '.join(["[[:Category:Images of %s by User:Emijrp|%s]] (%s)" % (x in cities2catname and cities2catname[x] or x, x in cities2catname and cities2catname[x] or x, y) for x, y in yearcities]))
    
    months_list = []
    for k, v in months.items():
        months_list.append([k, v])
    months_list.sort()
    monthsx = [monthnum2monthname[str(k)] for k, v in months_list]
    monthsy = [str(v) for k, v in months_list]
    
    devices_list = []
    for k, v in devices.items():
        devices_list.append([k, v])
    devices_list.sort()
    devicesx = [str(k) for k, v in devices_list]
    devicesy = [str(v) for k, v in devices_list]
    
    page = pywikibot.Page(commons, "User:Emijrp/Statistics")
    lastupdate = datetime.datetime.now().strftime('%Y-%m-%d')
    #https://glamtools.toolforge.org/glamorous.php?doit=1&category=Files+by+User%3AEmijrp&use_globalusage=1&ns0=1&format=xml
    usage = """"""
    filesbyyeargraph = "{{Graph:Chart|width=800|height=300|xAxisTitle=Year|yAxisTitle=Files|type=rect|x=%s|y=%s}}" % (','.join(yearsx), ','.join(yearsy))
    filesbyyeartable = """{| class="wikitable sortable" style="text-align: center;"\n! Year !! Files !! Cities\n%s\n|}""" % ('\n'.join(["|-\n| [[:Category:Images by User:Emijrp taken in %s|%s]] || data-sort-value=%s | %s || %s" % (yearsx[i], yearsx[i], yearsy[i], yearsy[i], yearscities[i]) for i in range(len(yearsx))]))
    filesbymonthgraph = "{{Graph:Chart|width=800|height=300|xAxisTitle=Month|yAxisTitle=Files|type=rect|x=%s|y=%s}}" % (','.join(monthsx), ','.join(monthsy))
    filesbymonthtable = """{| class="wikitable sortable" style="text-align: center;"\n! Month !! Files\n%s\n|}""" % ('\n'.join(["|-\n| [[:Category:Images by User:Emijrp taken in %s|%s]] || data-sort-value=%s | %s" % (monthsx[i], monthsx[i], monthsy[i], monthsy[i]) for i in range(len(monthsx))]))
    filesbydevicegraph = "{{Graph:Chart|width=100|height=100|type=pie|legend=Legend|x=%s|y1=%s|showValues=}}" % (','.join(devicesx), ','.join(devicesy))
    filesbydevicetable = """{| class="wikitable sortable" style="text-align: center;"\n! Device !! Files\n%s\n|}""" % ('\n'.join(["|-\n| [[:Category:Images by User:Emijrp taken with %s|%s]] || data-sort-value=%s | %s" % (devicesx[i], devicesx[i], devicesy[i], devicesy[i]) for i in range(len(devicesx))]))
    formatdict = { "total": total, "totaldevices": len(devices_list), "totalcities": len(cities_list), "totalyears": len(years_list), "totalinstitutions": len(institutions_list), "lastupdate": lastupdate, "usage": usage, "filesbyyeargraph": filesbyyeargraph, "filesbyyeartable": filesbyyeartable, "filesbymonthgraph": filesbymonthgraph, "filesbymonthtable": filesbymonthtable, "filesbydevicegraph": filesbydevicegraph, "filesbydevicetable": filesbydevicetable, "catstable": catstable, "citiestable": citiestable, "institutionstable": institutionstable }  
    newtext = """'''Statistics''' for '''{{{{formatnum:{total}}}}} files''' from [[:Category:Files by User:Emijrp]]. The files, mostly images, were taken with [[#By device|{totaldevices} different devices]] in [[#Cities|{totalcities} cities]] spanning [[#By year|{totalyears} years]]. Among the visited places, there are over [[#Institutions|{totalinstitutions} cultural institutions]].
\nLast update: {lastupdate}.
{usage}
== Files ==
=== By year ===
{{|
| valign=top | \n{filesbyyeargraph}
| valign=top | \n{filesbyyeartable}
|}}
=== By month ===
{{|
| valign=top | \n{filesbymonthgraph}
| valign=top | \n{filesbymonthtable}
|}}
=== By device ===
{{|
| valign=top | \n{filesbydevicegraph}
| valign=top | \n{filesbydevicetable}
|}}

== Most frequent ==
{{| style="text-align: center;"
| valign=top | \n{catstable}
| valign=top | \n{citiestable}
|}}

== Institutions ==
{institutionstable}

{{{{Template:User:Emijrp}}}}""".format(**formatdict)
    if newtext != page.text:
        pywikibot.showDiff(page.text, newtext)
        page.text = newtext
        page.save('BOT - Updating stats')

if __name__ == '__main__':
    main()
