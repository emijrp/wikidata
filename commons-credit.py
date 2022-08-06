#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2022 emijrp <emijrp@gmail.com>
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

import reverse_geocoder as rg
import pywikibot
from pywikibot import pagegenerators

cc2country = { 'ES': 'Spain' }
fixcities = {
    '41.38022,2.17319,Ciutat Vella': 'Barcelona',
    '41.37263,2.1546,Sants-Montjuic': 'Barcelona',
    
    '37.85,-4.9,Villarrubia': 'Córdoba',
    
    '40.66677,-3.19914,Marchamalo': 'Guadalajara',
    
    '40.40021,-3.69618,Arganzuela': 'Madrid',
    '40.43893,-3.61537,San Blas': 'Madrid',
    '40.38897,-3.74569,Latina': 'Madrid',
    '40.38866,-3.70035,Usera': 'Madrid',
    '40.42972,-3.67975,Salamanca': 'Madrid',
    '40.43404,-3.70379,Chamberi': 'Madrid',
    '40.39094,-3.7242,Carabanchel': 'Madrid',
    '40.41831,-3.70275,City Center': 'Madrid',
    '40.41317,-3.68307,Retiro': 'Madrid',
    '40.41667,-3.65,Moratalaz': 'Madrid',
    '40.43547,-3.7317,Moncloa-Aravaca': 'Madrid',
}
cachedlocations = {}

def getCountry(result={}):
    country = result['cc']
    country = country in cc2country and cc2country[country] or ''
    return country

def getCity(result={}):
    city = result['name']
    key = '%s,%s,%s' % (result['lat'], result['lon'], result['name'])
    if key in fixcities:
        city = fixcities[key]
    return city

def addMetadata(newtext='', pagelink=''):
    if re.search(r'(?im)\{\{\s*Quality\s*Image', newtext):
        #las quality images las actualizamos siempre
        pass
    else:
        #esto solo analiza las q le haya puesto coordenadas y no haya sido procesada antes
        #comentar cuando quiera que recorra todas mis fotos
        pass
        """
        if re.search(r'(?im)\{\{\s*Location\s*\|', newtext):
            if re.search(r'(?im)\|location-longitude=', newtext):
                return newtext
        else:
            return newtext
        """
    
    newtext = re.sub(r'(?im){{User:Emijrp/credit[^\{\}]*?}}', r'{{User:Emijrp/credit}}', newtext)
    #date
    m = re.findall(r'(?im)^\|\s*date\s*=\s*(?:\{\{(?:according ?to ?exif ?data|taken ?on)\s*\|\s*(?:1=)?)?\s*(\d\d\d\d-\d\d-\d\d( \d\d:\d\d(:\d\d)?)?)', newtext)
    if m:
        print(m)
        newtext = re.sub(r'(?im){{User:Emijrp/credit[^\{\}]*?}}', r'{{User:Emijrp/credit|date=%s}}' % (m[0][0]), newtext)
    
    #camera
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?device=', newtext):
    try:
        req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        time.sleep(60)
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
    elif re.search(r'(?im)microscope', pagelink) and re.search(r'(?im)data-file-width="640" data-file-height="480"', raw):
        model = 'Jiusion Digital Microscope'
        newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|device=%s}}' % (model), newtext)
    else:
        print("Modelo no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un modelo de camara")
    
    #exposuretime
    #https://commons.wikimedia.org/wiki/Category:Photographs_by_exposure_time
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?exposuretime=', newtext):
    #<tr class="exif-exposuretime"><th>Tiempo de exposición</th><td>1/333 seg (0,003003003003003)</td></tr>
    exposuretime = re.findall(r'(?im)<tr class="exif-exposuretime"><th>[^<>]*?</th><td>(.*?)</td></tr>', raw)
    if exposuretime:
        exposuretime = exposuretime[0].split('s')[0].strip() #le quitamos la unidad seg para poder hacer calculos en la plantilla
        exposuretime = re.sub(r'&#160;', r'', exposuretime)
        exposuretime = re.sub(r',', r'', exposuretime)
        print(exposuretime)
        if exposuretime:
            newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|exposure-time=%s}}' % (exposuretime), newtext)
    else:
        print("Tiempo de exposicion no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un tiempo de exposicion")
    
    #iso
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?iso=', newtext):
    #<tr class="exif-isospeedratings"><th>Calificación de velocidad ISO</th><td>3200</td></tr>
    iso = re.findall(r'(?im)<tr class="exif-isospeedratings"><th>[^<>]*?</th><td>(.*?)</td></tr>', raw)
    if iso:
        iso = iso[0].strip()
        iso = re.sub(r',', r'', iso)
        print(iso)
        if iso:
            newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|iso=%s}}' % (iso), newtext)
    else:
        print("ISO no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un ISO")
    
    #focal length
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?focal-length=', newtext):
    #<tr class="exif-focallength"><th>Longitud focal de la lente</th><td>34 mm</td></tr>
    focallength = re.findall(r'(?im)<tr class="exif-focallength"><th>[^<>]*?</th><td>(.*?)</td></tr>', raw)
    if focallength:
        focallength = focallength[0].strip()
        focallength = re.sub(r' mm', r'', focallength) # le quitamos el mm para poder hacer calculos en la plantilla
        focallength = focallength.strip()
        print(focallength)
        if focallength:
            newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|focal-length=%s}}' % (focallength), newtext)
    else:
        print("Focal length no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un focal length")
    
    #fnumber
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?f-number=', newtext):
    #<tr class="exif-fnumber"><th>Número F</th><td>f/1,8</td></tr>
    fnumber = re.findall(r'(?im)<tr class="exif-fnumber"><th>.*?</th><td>(.*?)</td></tr>', raw)
    #en el raw html inglés sale <th><a href="https://en.wikipedia.org/wiki/F-number" class="extiw" title="wikipedia:F-number">F-number</a></th>
    if fnumber:
        fnumber = fnumber[0].strip()
        #fnumber = re.sub(r'f/', r'', fnumber) #le dejamos la f mejor, y no hace falta quitar ',' porque no las hay, mantenemos los '.' decimales
        fnumber = fnumber.strip()
        print(fnumber)
        if fnumber:
            newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|f-number=%s}}' % (fnumber), newtext)
    else:
        print("f-number no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un f-number")
    
    #{{QualityImage}}
    qualityimage = re.findall(r'(?im)\{\{\s*Quality\s*Image', newtext)
    if qualityimage:
        newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|quality-image=yes}}', newtext)
    else:
        print("{{QualityImage}} no encontrado")
    #else:
    #    print("La plantilla credit ya tiene un quality-image")
    
    #location (coordinates) https://commons.wikimedia.org/wiki/Template:Location
    #puede estar en coordenadas decimales o grados/minutos/segundos, parsear solo las {{Location|1=|2=}} para evitar lios
    #country, city, se puede hacer con github reverse-geocoder tirando de las coordenadas metidas con toolforge locator-tool
    #https://github.com/thampiman/reverse-geocoder
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?location=', newtext):
    #tambien existe Object-location por ej aquí lo puse https://commons.wikimedia.org/wiki/File:La_Muralla_en_enero_(39784771451).jpg
    #https://commons.wikimedia.org/wiki/File:Estrecho_de_Gibraltar_(9834504944).jpg
    for locregexp, locparam in [["Location", "location"], ["Object location", "object"]]:
        location = re.findall(r'(?im)\{\{\s*%s ?(?:dec|decimal)?\s*\|\s*(?:1=)?\s*([0-9\.\-\+]+)\s*\|\s*(?:2=)?\s*([0-9\.\-\+]+)\s*\}\}' % (locregexp), newtext)
        if location:
            print(location)
            lat = location[0][0]
            lon = location[0][1]
            latlon = '%s,%s' % (lat, lon)
            city = ''
            country = ''
            results = ''
            if latlon in cachedlocations:
                results = cachedlocations[latlon]
                print('Loaded cached location')
            else:
                results = rg.search((float(lat), float(lon)))
                cachedlocations[latlon] = results
            print(results)
            if results and len(results) == 1 and 'cc' in results[0] and 'name' in results[0]:
                """
                [{'name': 'Mountain View', 
                'cc': 'US', 
                'lat': '37.38605',
                'lon': '-122.08385', 
                'admin1': 'California', 
                'admin2': 'Santa Clara County'}]
                """
                country = getCountry(result=results[0])
                city = getCity(result=results[0])
                if country and city:
                    print(country, city)
                    newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|%s-latitude=%s|%s-longitude=%s|%s-country=%s|%s-city=%s}}' % (locparam, lat, locparam, lon, locparam, country, locparam, city), newtext)
                    with open('commons-credit.geo', 'a') as f:
                        f.write('%s,%s,%s,%s,%s,%s,%s\n' % (results[0]['lat'], results[0]['lon'], results[0]['cc'], results[0]['admin1'], results[0]['admin2'], results[0]['name'], pagelink))
                else:
                    print('Error in country or city')
            else:
                print('Error doing reverse geocoding')
                newtext = re.sub(r'(?im)({{User:Emijrp/credit[^\{\}]*?)}}', r'\1|%s-latitude=%s|%s-longitude=%s}}' % (locparam, lat, locparam, lon), newtext)
        else:
            print("{{Location}} no encontrado")
        #else:
        #    print("La plantilla credit ya tiene location")
    
    #subjects
    #|subjects=museum si contiene la palabra museo en alguna parte (o solo el título?)
    subjects = {
        'animals': ['zoo', 'zoobotanico', 'zoologico', 'ave', 'gato', 'perro', ], 
        'astronomy': ['astronomy', 'astronomia', "iridium"], 
        'buildings': ['edificio', ], 
        'buildings-lighthouses': ['faro', ], 
        'buildings-religion': ['iglesia', 'catedral', 'concatedral', 'ermita', 'parroquia', 'edificios religiosos', 'mezquita', ], 
        'buildings-towers': ['torre', ], 
        'events-carnival': ['carnaval', 'carrusel de coros', 'chirigota', ], 
        'events-culture': ['charla', 'conferencia', 'debate', 'exposicion', 'teatro', 'concierto', 'jornadas', 'mesa redonda', 'presentacion', ], 
        'events-demonstrations': ['manifestacion', 'marcha contra', '19jmani', ], 
        'events-disasters': ['temporal', 'tornado', 'accidente', 'humo', 'incendio', ], 
        'events-religion': ['semana santa', 'lunes santo', 'martes santo', 'miercoles santo', 'jueves santo', 'viernes santo', 'sabado santo', 'domingo de resurreccion', ], 
        'events-sports': ['futbol', 'triatlon', ], 
        'events-other': ['dia de', 'dia del', 'dia de la', 'dia local', 'dia nacional', 'dia internacional', 'festividad', 'fiesta', 'feria', 'homenaje', ], 
        'libraries': ['biblioteca', 'library', 'libraries', ], 
        'maps': ['plano', 'mapa', ], 
        'memoria-historica': ['memoria historica', 'memoria democratica', 'represion franquista', 'memorial republicano', 'bandera republicana', '13 rosas', 'trece rosas', 'guerra civil espanola', ], 
        'monuments': ['alcazar', 'castillo', 'casa', 'torreon', ], 
        'museums': ['museo', 'museum', ], 
        'nature-gardens': ['jardin', 'jardines', 'orchidarium', 'arbol', ], 
        'streets': ['calle', 'callejeando', 'avenida', 'plaza', ], 
        'transport-aviation': ['avion' ,'helicoptero', ], 
        'transport-road': ['autobus', 'carretera', 'coche', ], 
        'transport-ship': ['barco', 'catamaran', 'crucero', 'vaporcito', ], 
        'views': ['vista', 'vistas', 'mirador', 'miradores', ], 
        'water-rivers': ['rio', 'arroyo', 'afluente', ], 
        'water-sea': ['mar', 'oceano', 'playa', ], 
        'water-body': ['embalse', 'pantano', 'laguna', ], 
    }
    return newtext

def replaceAuthor(newtext=''):
    fieldnames = ["author", "photographer"]
    for fieldname in fieldnames:
        newtext = re.sub(r'(?im)(\|\s*%s\s*=\s*)\[\[User\:Emijrp\|Emijrp\]\]' % (fieldname), r'\1{{User:Emijrp/credit}}', newtext)
        newtext = re.sub(r'(?im)(\|\s*%s\s*=\s*)User\:Emijrp' % (fieldname), r'\1{{User:Emijrp/credit}}', newtext)
        newtext = re.sub(r'(?im)(\|\s*%s\s*=\s*)Usuario\:Emijrp' % (fieldname), r'\1{{User:Emijrp/credit}}', newtext)
        newtext = re.sub(r'(?im)(\|\s*%s\s*=\s*)Emijrp' % (fieldname), r'\1{{User:Emijrp/credit}}', newtext)
    return newtext

def replaceSource(newtext=''):
    if re.search(r'(?im)\|\s*author\s*=\s*{{User:Emijrp/credit', newtext):
        newtext = re.sub(r'(?im)(\|\s*source\s*=\s*){{User:Emijrp/credit}}', r'\1{{own work}}', newtext)
    return newtext

def creditByWhatlinkshere():
    purgeedit = False #force template cache purge
    skip = 'File:Viaje en tren Alicante-Murcia en julio de 2022 133.jpg'
    skip = 'File:Estrecho de Gibraltar (9834504944).jpg'
    skip = ''
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
        if newtext != page.text or purgeedit:
            pywikibot.showDiff(page.text, newtext)
            page.text = newtext
            page.save('BOT - Updating credit template')

def creditByCategory():
    commons = pywikibot.Site('commons', 'commons')
    category = pywikibot.Category(commons, '15-O Demonstrations, Cádiz')
    category = pywikibot.Category(commons, 'Paseo reflexivo Cádiz 21 de mayo de 2011')
    category = pywikibot.Category(commons, 'Playa de El Buzo')
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
