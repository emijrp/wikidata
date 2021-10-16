#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2021 emijrp <emijrp@gmail.com>
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

def addMetadata(newtext='', pagelink=''):
    newtext = re.sub(r'(?im){{User:Emijrp/credit[^\{\}]*?}}', r'{{User:Emijrp/credit}}', newtext)
    #date
    m = re.findall(r'(?im)^\|\s*date\s*=\s*(?:\{\{according ?to ?exif ?data\s*\|\s*(?:1=)?)?\s*(\d\d\d\d-\d\d-\d\d( \d\d:\d\d(:\d\d)?)?)', newtext)
    if m:
        print(m)
        newtext = re.sub(r'(?im){{User:Emijrp/credit[^\{\}]*?}}', r'{{User:Emijrp/credit|date=%s}}' % (m[0][0]), newtext)
    
    #camera
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?device=', newtext):
    req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
    raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    #<tr class="exif-model"><th>Modelo de cámara</th><td>X-3,C-60Z       </td></tr>
    model = re.findall(r'(?im)<tr class="exif-model"><th>[^<>]*?</th><td>(.*?)</td></tr>', raw)
    if model:
        model = model[0]
        model = re.sub(r'(?im)<a[^<>]*?>', r'', model)
        model = re.sub(r'(?im)</a>', r'', model).strip()
        print(model)
        newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|device=%s}}' % (model), newtext)
    else:
        print("Modelo no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un modelo de camara")
    
    #exposuretime
    #https://commons.wikimedia.org/wiki/Category:Photographs_by_exposure_time
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?exposuretime=', newtext):
    req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
    raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    #<tr class="exif-exposuretime"><th>Tiempo de exposición</th><td>1/333 seg (0,003003003003003)</td></tr>
    exposuretime = re.findall(r'(?im)<tr class="exif-exposuretime"><th>[^<>]*?</th><td>(.*?)</td></tr>', raw)
    if exposuretime:
        exposuretime = exposuretime[0].split('s')[0].strip()
        exposuretime = re.sub(r'&#160;', r'', exposuretime)
        exposuretime = re.sub(r',', r'', exposuretime)
        print(exposuretime)
        if exposuretime:
            newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|exposure-time=%s}}' % (exposuretime), newtext)
    else:
        print("Tiempo de exposicion no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un tiempo de exposicion")
    
    #location (coordinates) https://commons.wikimedia.org/wiki/Template:Location
    #puede estar en coordenadas decimales o grados/minutos/segundos, parsear solo las {{Location|1=|2=}} para evitar lios
    #country, city, se puede hacer con github reverse-geocoder tirando de las coordenadas metidas con toolforge locator-tool
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?location=', newtext):
    location = re.findall(r'(?im)\{\{\s*Location\s*\|\s*(?:1=)?\s*([0-9\.\-\+]+)\s*\|\s*(?:2=)?\s*([0-9\.\-\+]+)\s*\}\}', newtext)
    if location:
        print(location)
        lat = location[0][0]
        lon = location[0][1]
        newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|location-latitude=%s|location-longitude=%s}}' % (lat, lon), newtext)
    else:
        print("{{Location}} no encontrado")
    #else:
    #    print("La plantilla credit ya tiene location")
    
    return newtext

def replaceAuthor(newtext=''):
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)\[\[User\:Emijrp\|Emijrp\]\]', r'\1{{User:Emijrp/credit}}', newtext)
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)User\:Emijrp', r'\1{{User:Emijrp/credit}}', newtext)
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)Usuario\:Emijrp', r'\1{{User:Emijrp/credit}}', newtext)
    newtext = re.sub(r'(?im)(\|\s*author\s*=\s*)Emijrp', r'\1{{User:Emijrp/credit}}', newtext)
    return newtext

def replaceSource(newtext=''):
    if re.search(r'(?im)\|\s*author\s*=\s*{{User:Emijrp/credit}}', newtext):
        newtext = re.sub(r'(?im)(\|\s*source\s*=\s*){{User:Emijrp/credit}}', r'\1{{own work}}', newtext)
    return newtext

def creditByWhatlinkshere():
    skip = ''
    #skip = 'File:Museo de Historia de Madrid en junio de 2021 46.jpg'
    commons = pywikibot.Site('commons', 'commons')
    userpage = pywikibot.Page(commons, 'User:Emijrp')
    gen = userpage.backlinks(namespaces=[6])
    for page in gen:
        print('==', page.title(), '==')
        if skip:
            if page.title() == skip:
                skip = ""
            else:
                continue
        
        newtext = page.text
        newtext = replaceAuthor(newtext=newtext)
        newtext = replaceSource(newtext=newtext)
        newtext = addMetadata(newtext=newtext, pagelink=page.full_url())
        if newtext != page.text:
            pywikibot.showDiff(page.text, newtext)
            page.text = newtext
            page.save('BOT - Updating credit template')

def creditByCategory():
    commons = pywikibot.Site('commons', 'commons')
    category = pywikibot.Category(commons, '15-O Demonstrations, Cádiz')
    category = pywikibot.Category(commons, 'Paseo reflexivo Cádiz 21 de mayo de 2011')
    gen = pagegenerators.CategorizedPageGenerator(category)
    for page in gen:
        print('==', page.title(), '==')
        newtext = page.text
        newtext = replaceAuthor(newtext=newtext)
        newtext = replaceSource(newtext=newtext)
        if newtext != page.text:
            pywikibot.showDiff(page.text, newtext)
            page.text = newtext
            page.save('BOT - Updating credit template')

def creditByFlickrUrl():
    commons = pywikibot.Site('commons', 'commons')
    flickrurls = [
        'http://flickr.com/people/96396586@N07',
        'http://www.flickr.com/people/96396586@N07',
        'https://flickr.com/people/96396586@N07',
        'https://www.flickr.com/people/96396586@N07',
    ]
    for flickrurl in flickrurls:
        images = ['hola']
        while images:
            linksearch = 'https://commons.wikimedia.org/w/index.php?target=%s&title=Special:LinkSearch' % (flickrurl)
            req = urllib.request.Request(linksearch, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
            raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
            images = re.findall(r'title="(File:[^<>]+?)">File:', raw)
            print(images)
            for image in images:
                page = pywikibot.Page(commons, image)
                text = page.text
                newtext = page.text
                newtext = re.sub(r'(\|\s*Author\s*=\s*)\[%s [^\]]*?\]\s*(de|from)?\s*(España|Spain)?' % (flickrurl), r'\1{{User:Emijrp/credit}}', newtext)
                if text != newtext:
                    pywikibot.showDiff(text, newtext)
                    page.text = newtext
                    page.save('BOT - Updating credit template')

def main():
    #creditByFlickrUrl()
    #creditByCategory()
    creditByWhatlinkshere()

if __name__ == '__main__':
    main()
