#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2023 emijrp <emijrp@gmail.com>
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
import os
import pickle
import re
import time
import unicodedata
import urllib.request

import reverse_geocoder as rg
import pywikibot
from pywikibot import pagegenerators

timeline = {}
cc2country = { 'ES': 'Spain' }
fixcities = {
    #acentos
    '36.16809,-5.34777,La Linea de la Concepcion': 'La Línea de la Concepción',
    
    #minor entities in cities
    '41.38022,2.17319,Ciutat Vella': 'Barcelona',
    '41.41849,2.1677,Horta-Guinardo': 'Barcelona',
    '41.37263,2.1546,Sants-Montjuic': 'Barcelona',
    '41.93012,2.25486,Vic': 'Barcelona',
    
    '37.85,-4.9,Villarrubia': 'Córdoba',
    
    '37.15994,-3.43863,Guejar-Sierra': 'Güéjar Sierra',
    
    '40.66677,-3.19914,Marchamalo': 'Guadalajara',
    
    '40.40021,-3.69618,Arganzuela': 'Madrid',
    '40.43893,-3.61537,San Blas': 'Madrid',
    '40.38897,-3.74569,Latina': 'Madrid',
    '40.38866,-3.70035,Usera': 'Madrid',
    '40.42972,-3.67975,Salamanca': 'Madrid',
    '40.46206,-3.6766,Chamartin': 'Madrid',
    '40.43404,-3.70379,Chamberi': 'Madrid',
    '40.39094,-3.7242,Carabanchel': 'Madrid',
    '40.41831,-3.70275,City Center': 'Madrid',
    '40.41317,-3.68307,Retiro': 'Madrid',
    '40.41667,-3.65,Moratalaz': 'Madrid',
    '40.43547,-3.7317,Moncloa-Aravaca': 'Madrid',
    '40.35,-3.7,Villaverde': 'Madrid',
    '40.15913,-3.62103,Ciempozuelos': 'Madrid',
    
    '40.6,-6.53333,Ciudad Rodrigo': 'Salamanca',
    
}
cachedlocations = {}
cachedpages = {}

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

def removeAccents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def removePunctuation(s):
    s = re.sub(r"(?im)[\"\'\!\¡\.\,\:\;\(\)\&\%\$\@\#\{\}\-]", " ", s)
    s = re.sub(r"(?im) +", " ", s)
    return s

def ocr(filename):
    import cv2
    import pytesseract
    
    if not os.path.exists(filename):
        print("El fichero no existe", filename)
        return ""
    try:
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 100))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        im2 = img.copy()
        text = ""
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped = im2[y:y + h, x:x + w]
            text += "\n" + pytesseract.image_to_string(cropped)
    except:
        return "" #probablemente SVG u otro formato no soportado
    
    return text

def timediff(time1="", time2=""):
    delta = time1-time2
    if delta.days:
        if delta.days >= 365:
            return "%d {{years}}" % (delta.days/365)
        elif delta.days >= 30:
            return "%d {{months (i18n)}}" % (delta.days/30)
        elif delta.days > 0:
            return "%d {{days}}" % (delta.days)
        else:
            return "{{Same day}}"
    elif delta.seconds >= 3600:
        return "%d {{hours}}" % (delta.seconds/3600)
    elif delta.seconds >= 60:
        return "%d {{minutes}}" % (delta.seconds/60)
    elif delta.seconds <= 60 and delta.seconds > 0:
        return "%d {{seconds}}" % (delta.seconds)
    else:
        return "{{Same day}}"

def parseTime(time=""):
    if len(time) == 19:
        time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    elif len(time) == 16:
        time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
    elif len(time) == 10:
        time = datetime.datetime.strptime(time, "%Y-%m-%d")
    return time

def generateTimelineGallery(pagetitle=''):
    global timeline
    
    timelinegallery = ""
    if not pagetitle:
        return timelinegallery
    
    timeline_list = [["%s-%s" % (v, k), v, k] for k, v in timeline.items()]
    timeline_list.sort()
    c = 0
    #timefilenameconcat es para ordenar ficheros temporalmente cuando la fecha no tiene resolucion de segundo, usa time+nombre fichero para ofrecer siempre el mismo orden en distintas ejecuciones del bot
    for timefilenameconcat, time, filename in timeline_list:
        time = parseTime(time=time)
        if not time:
            return timelinegallery
        if pagetitle == filename and c >= 2 and c <= len(timeline_list)-2:
            prev2pagetitle = timeline_list[c-2][2]
            prev2time = parseTime(time=timeline_list[c-2][1])
            prev2delta = timediff(time, prev2time)
            prev1pagetitle = timeline_list[c-1][2]
            prev1time = parseTime(time=timeline_list[c-1][1])
            prev1delta = timediff(time, prev1time)
            
            next1pagetitle = timeline_list[c+1][2]
            next1time = parseTime(time=timeline_list[c+1][1])
            next1delta = timediff(next1time, time)
            next2pagetitle = timeline_list[c+2][2]
            next2time = parseTime(time=timeline_list[c+2][1])
            next2delta = timediff(next2time, time)
            
            timelinegallery = """{{#tag:gallery|
%s{{!}}<< %s
%s{{!}}< %s
%s{{!}}{{This image}}
%s{{!}}%s >
%s{{!}}%s >>
|mode=packed-hover}}""" % (prev2pagetitle, prev2delta, prev1pagetitle, prev1delta, pagetitle, next1pagetitle, next1delta, next2pagetitle, next2delta)
            break
        c += 1
    
    return timelinegallery

def addMetadata(pagetitle='', newtext='', pagelink='', pagehtml='', filelink=''):
    filename = "file.jpg"
    if os.path.exists(filename):
        os.remove(filename)
    if re.search(r'(?im)\{\{\s*Quality\s*Image', newtext):
        #las quality images las actualizamos siempre
        pass
    else:
        #esto solo analiza las q le haya puesto coordenadas y no haya sido procesada antes
        #comentar cuando quiera que recorra todas mis fotos
        pass
        """if re.search(r'(?im)\{\{\s*Location\s*\|', newtext):
            if re.search(r'(?im)\|location-longitude=', newtext):
                return newtext
        else:
            return newtext"""
    
    creditend = "credit-end=}}" #no incluir el | al principio, pq en las regexp se lia y cree que es un OR y causa repeticiones
    regexpcredit = r'(?ims)({{User:Emijrp/credit.*?)\|%s' % (creditend)
    newtext = re.sub(r'(?ims){{User:Emijrp/credit.*?mode=packed-hover}}}}', r'{{User:Emijrp/credit|%s' % (creditend), newtext) #temp patch 8 abril 2023
    newtext = re.sub(r'(?ims){{User:Emijrp/credit.*?\|%s' % (creditend), r'{{User:Emijrp/credit|%s' % (creditend), newtext)
    newtext = re.sub(r'(?ims){{User:Emijrp/credit[^\{\}]*?}}', r'{{User:Emijrp/credit|%s' % (creditend), newtext)
    
    #date
    #el campo "photo date" es para la plantilla "Art photo" que me han puesto en esta y otras https://commons.wikimedia.org/w/index.php?title=File:Museo_de_Santa_Cruz_(27024254341).jpg&oldid=691638708
    m = re.findall(r'(?im)^\|\s*(?:date|photo date)\s*=\s*(?:\{\{(?:according ?to ?exif ?data|taken ?on)\s*\|\s*(?:1=)?)?\s*(\d\d\d\d-\d\d-\d\d( \d\d:\d\d(:\d\d)?)?)', newtext)
    if m:
        date = m[0][0]
        print(date)
        newtext = re.sub(regexpcredit, r'\1|date=%s|%s' % (date, creditend), newtext)
    
    #camera
    try:
        if not pagehtml:
            req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
            pagehtml = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        time.sleep(60)
        if not pagehtml:
            req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
            pagehtml = urllib.request.urlopen(req).read().strip().decode('utf-8')
    try:
        if filelink:
            urllib.request.urlretrieve(filelink, "file.jpg")
    except:
        time.sleep(60)
        if filelink:
            urllib.request.urlretrieve(filelink, "file.jpg")
    #<tr class="exif-model"><th>Modelo de cámara</th><td>X-3,C-60Z       </td></tr>
    model = re.findall(r'(?im)<tr class="exif-model"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if model:
        model = model[0]
        model = re.sub(r'(?im)<a[^<>]*?>', r'', model)
        model = re.sub(r'(?im)</a>', r'', model).strip()
        print(model)
        newtext = re.sub(regexpcredit, r'\1|device=%s|%s' % (model, creditend), newtext)
    elif re.search(r'(?im)microscope', pagetitle) and re.search(r'(?im)data-file-width="640" data-file-height="480"', pagehtml):
        model = 'Jiusion Digital Microscope'
        newtext = re.sub(regexpcredit, r'\1|device=%s|%s' % (model, creditend), newtext)
    else:
        print("Modelo no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un modelo de camara")
    
    #exposuretime
    #https://commons.wikimedia.org/wiki/Category:Photographs_by_exposure_time
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?exposuretime=', newtext):
    #<tr class="exif-exposuretime"><th>Tiempo de exposición</th><td>1/333 seg (0,003003003003003)</td></tr>
    exposuretime = re.findall(r'(?im)<tr class="exif-exposuretime"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if exposuretime:
        exposuretime = exposuretime[0].split('s')[0].strip() #le quitamos la unidad seg para poder hacer calculos en la plantilla
        exposuretime = re.sub(r'&#160;', r'', exposuretime)
        exposuretime = re.sub(r',', r'', exposuretime)
        print(exposuretime)
        if exposuretime:
            newtext = re.sub(regexpcredit, r'\1|exposure-time=%s|%s' % (exposuretime, creditend), newtext)
    else:
        print("Tiempo de exposicion no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un tiempo de exposicion")
    
    #iso
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?iso=', newtext):
    #<tr class="exif-isospeedratings"><th>Calificación de velocidad ISO</th><td>3200</td></tr>
    iso = re.findall(r'(?im)<tr class="exif-isospeedratings"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if iso:
        iso = iso[0].strip()
        iso = re.sub(r',', r'', iso)
        print(iso)
        if iso:
            newtext = re.sub(regexpcredit, r'\1|iso=%s|%s' % (iso, creditend), newtext)
    else:
        print("ISO no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un ISO")
    
    #focal length
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?focal-length=', newtext):
    #<tr class="exif-focallength"><th>Longitud focal de la lente</th><td>34 mm</td></tr>
    focallength = re.findall(r'(?im)<tr class="exif-focallength"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if focallength:
        focallength = focallength[0].strip()
        focallength = re.sub(r' mm', r'', focallength) # le quitamos el mm para poder hacer calculos en la plantilla
        focallength = focallength.strip()
        print(focallength)
        if focallength:
            newtext = re.sub(regexpcredit, r'\1|focal-length=%s|%s' % (focallength, creditend), newtext)
    else:
        print("Focal length no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un focal length")
    
    #fnumber
    #if not re.search(r'(?im){{User:Emijrp/credit[^\{\}]*?f-number=', newtext):
    #<tr class="exif-fnumber"><th>Número F</th><td>f/1,8</td></tr>
    fnumber = re.findall(r'(?im)<tr class="exif-fnumber"><th>.*?</th><td>(.*?)</td></tr>', pagehtml)
    #en el pagehtml html inglés sale <th><a href="https://en.wikipedia.org/wiki/F-number" class="extiw" title="wikipedia:F-number">F-number</a></th>
    if fnumber:
        fnumber = fnumber[0].strip()
        #fnumber = re.sub(r'f/', r'', fnumber) #le dejamos la f mejor, y no hace falta quitar ',' porque no las hay, mantenemos los '.' decimales
        fnumber = fnumber.strip()
        print(fnumber)
        if fnumber:
            newtext = re.sub(regexpcredit, r'\1|f-number=%s|%s' % (fnumber, creditend), newtext)
    else:
        print("f-number no encontrado en exif")        
    #else:
    #    print("La plantilla credit ya tiene un f-number")
    
    #{{QualityImage}}
    qualityimage = re.findall(r'(?im)\{\{\s*Quality\s*Image', newtext)
    if qualityimage:
        newtext = re.sub(regexpcredit, r'\1|quality-image=yes|%s' % (creditend), newtext)
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
    if re.findall(r'(?im)\{\{\s*Location withheld', newtext):
        newtext = re.sub(regexpcredit, r'\1|location-withheld=yes|%s' % (creditend), newtext)
    else:
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
                    print("country=", country, "city=", city)
                    if country or city:
                        print(country, city)
                        newtext = re.sub(regexpcredit, r'\1|%s-latitude=%s|%s-longitude=%s|%s-country=%s|%s-city=%s|%s' % (locparam, lat, locparam, lon, locparam, country, locparam, city, creditend), newtext)
                        with open('commons-credit.geo', 'a') as f:
                            f.write('%s,%s,%s,%s,%s,%s,%s\n' % (results[0]['lat'], results[0]['lon'], results[0]['cc'], results[0]['admin1'], results[0]['admin2'], results[0]['name'], pagelink))
                    else:
                        print('Error in country or city')
                else:
                    print('Error doing reverse geocoding')
                    newtext = re.sub(regexpcredit, r'\1|%s-latitude=%s|%s-longitude=%s|%s' % (locparam, lat, locparam, lon, creditend), newtext)
            else:
                print("{{Location}} no encontrado")
            #else:
            #    print("La plantilla credit ya tiene location")
    
    #topics
    #|topic=museum si contiene la palabra museo en alguna parte (o solo el título? o solo categorías?)
    #|topic2= topic3=...
    #ideas: teatro romano (topic=arquitectura romana?)
    #bronze age (topic=edad del bronce) https://commons.wikimedia.org/wiki/Category:Prehistory_by_period
    #art? mosaico pintura mural murales
    # cueva
    topics = [
        ["animals", 
            ["zoo", "zoobotanico", "zoologico", "gato", "insecto", "perro", "reptil", "cangrejo", "peces" ], 
            ["estacion", "santa justa", "monumento"], 
        ], 
        ["aquariums",
            ["acuario", "acuarios", "aquarium", "aquariums", ],
            [], 
        ], 
        ["astronomy", 
            ["astronomy", "astronomia", "iridium", ], 
            [], 
        ], 
        
        ["architectural-elements-arches", 
            ["arco", "arcos", "arch", "arches"], 
            ["arcos de la frontera"], 
        ], 
        ["architectural-elements-ceilings", 
            ["ceilings"], 
            [], 
        ], 
        ["architectural-elements-columns", 
            ["columns"], 
            [], 
        ], 
        ["architectural-elements-doors", 
            ["doors"], 
            [], 
        ], 
        ["architectural-elements-pavements", 
            ["pavements"], 
            [], 
        ], 
        ["architectural-elements-stairs", 
            ["stairs"], 
            [], 
        ], 
        
        ["art-paintings", 
            ["painting", "paintings", "pintura", "pinturas"], 
            [], 
        ], 
        ["art-sculptures", 
            ["sculpture", "sculptures", "statue", "statues", "estatua", "estatuas"], 
            [], 
        ], 
        
        ["buildings", 
            ["edificio", "building", "academia", "centro cultural", "colegio", "school", "facultad", "universidad", "university"], 
            [], 
        ], 
        ["buildings-airports", 
            ["aeropuerto", "aeropuertos", "airport", "airports", ], 
            [], 
        ], 
        ["buildings-alcazabas", 
            ["alcazaba", "alcazabas"], 
            [], 
        ], 
        ["buildings-alcazares", 
            ["alcazar", "alcazares"], 
            [], 
        ], 
        ["buildings-amphitheatres", 
            ["anfiteatro", "anfiteatros", "amphitheatre", "amphitheatres", ], 
            [], 
        ], 
        ["buildings-archives", 
            ["archivo general", "archivo historico", "archivo municipal", "archivo nacional", "archivo provincial", "archive", "archives", "municipal archive", "national archive", "archivo de"], 
            [], 
        ], 
        ["buildings-aqueducts", 
            ["acueducto", "acueductos", "aqueduct", "aqueducts"], 
            [], 
        ], 
        ["buildings-bridges", 
            ["puente", "puentes", "bridge", "bridges"], 
            [], 
        ], 
        ["buildings-bunkers", 
            ["bunker", "bunkers"], 
            [], 
        ], 
        ["buildings-castles", 
            ["castillo", "castillos", "castle", "castles"], 
            ["canovas"], 
        ], 
        ["buildings-cathedrals", 
            ["catedral", "catedrales", "cathedral", "cathedrals"], 
            [], 
        ], 
        ["buildings-cemeteries", 
            ["cementerio", "cementerios", "panteon", "cemetery", "cemeteries"], 
            [], 
        ], 
        ["buildings-houses", 
            ["casa de", "house", "casas colgadas"], 
            [], 
        ], 
        ["buildings-libraries", 
            ["biblioteca", "bibliotecas", "library", "libraries", "libreria", "librerias"], 
            [], 
        ], 
        ["buildings-national-libraries", 
            ["biblioteca nacional", "bibliotecas nacionales", "national library", "national libraries"], 
            [], 
        ], 
        ["buildings-lighthouses", 
            ["faro", "faros", "lighthouse", "lighthouses"], 
            ["moncloa", ], 
        ], 
        ["buildings-palaces", 
            ["palacio", "palacios", "palace", "palaces"], 
            ["calle", ], 
        ], 
        ["buildings-ports", 
            ["puerto", "lonja", "muelle", "seaport", "seaports", "shipyard", "shipyards", ], 
            ["puerto de santa", "puerto santa", "puerto real", "ciudad de el puerto", "puerto lapice", "puerto lápice"], 
        ], 
        ["buildings-religion", 
            ["iglesia", "catedral", "capilla", "concatedral", "convento", "conventos", "ermita", "parroquia", "edificios religiosos", "mezquita", "church", "churches", "cathedral", "cathedrals", "chapel", "chapels", "convent", "convents"], 
            [], 
        ], 
        ["buildings-roads", 
            ["autovia", "carretera", "carreteras", "glorieta", "road", "roads", "road signs", ], 
            [], 
        ], 
        ["buildings-train-stations", 
            ["estacion de tren", "entacion de trenes", "train station", "train stations", "anden"], 
            [], 
        ], 
        ["buildings-towers", 
            ["torre", "torres", "torreon", "torreones", "torrespana", "tower", "towers"], 
            [], 
        ], 
        ["buildings-town-halls", 
            ["ayuntamiento", "ayuntamientos", "town hall", "town halls"], 
            [], 
        ], 
        ["buildings-tunnels", 
            ["tunel", "tuneles", "tunnel", "tunnels"], 
            [], 
        ], 
        ["buildings-walls", 
            ["muralla", "murallas", "wall", "walls"], 
            [], 
        ], 
        ["events-carnival", 
            ["carnaval", "carrusel de coros", "chirigota", ], 
            [], 
        ], 
        ["events-culture", 
            ["charla", "conferencia", "conferencias", "debate", "teatro", "jornada", "jornadas", "mesa redonda", "presentacion", ], 
            ["teatro falla", "teatro romano"], 
        ], 
        ["events-exhibitions", 
            ["exposicion", "exposiciones", "exhibition", "exhibitions"], 
            [], 
        ], 
        ["events-concerts", 
            ["concierto", "conciertos", "concert", "concerts"], 
            [], 
        ], 
        ["events-demonstrations", 
            ["manifestacion", "manifestaciones", "marcha contra", "huelga", "19jmani", "protesta", "protestas", "paseo reflexivo"], 
            [], 
        ], 
        ["events-disasters", 
            ["tornado", "accidente", "incendio", "inundacion"], 
            [], 
        ], 
        ["events-religion", 
            ["semana santa", "lunes santo", "martes santo", "miercoles santo", "jueves santo", "viernes santo", "sabado santo", "domingo de resurreccion", "penitente", "penitentes", "palio", "virgen de"], 
            [], 
        ], 
        ["events-sports", 
            ["futbol", "triatlon", "carrera", "motorada", "football", "soccer", "vuelta ciclista", ], 
            [], 
        ], 
        ["events-other", 
            ["dia de", "dia del", "dia de la", "dia local", "dia nacional", "dia internacional", "festividad", "fiesta", "feria", "homenaje", ], 
            [], 
        ], 
        ["fossils", 
            ["fossil", "fossils", "fosil", "fósil", "fosiles", "fósiles"], 
            [], 
        ], 
        ["maps", 
            ["plano", "mapa", "callejero"], 
            ["en primer plano", "en segundo plano"], 
        ], 
        ["memoria-historica", 
            ["memoria historica", "memoria democratica", "represion franquista", "memorial republicano", "bandera republicana", "13 rosas", "trece rosas", "guerra civil espanola", "brigadas internacionales", "por la memoria", "franquismo"], 
            [], 
        ], 
        ["monuments", #limitado a monumentos estilo esculturas, bustos, homenajes
            ["monumento", "monument"], 
            [], 
        ], 
        ["museums", 
            ["museo", "museu", "museum", "casa museo", "casa natal"], 
            [], 
        ], 
        ["nature-countryside", 
            ["campos de lavanda"], 
            [""], 
        ], 
        ["nature-gardens", 
            ["jardin", "jardines", "orchidarium", "parque", "parques", "arbol", "alameda"], 
            ["natural", "eolico"], 
        ], 
        ["numismatics", 
            ["moneda", "monedas", "coin", "coins", "numismatica", "numismatics", "billete", "billetes", "banknote", "banknotes", "peseta", "pesetas"], 
            ["tren", "metro"], 
        ], 
        ["objects", 
            ["objeto", ], 
            [], 
        ], 
        ["objects-books", 
            ["libro", "libros", "book", "books"], 
            [], 
        ], 
        ["objects-chairs", 
            ["silla", "sillas", "chair", "chairs"], 
            [], 
        ], 
        ["objects-dvds", 
            ["dvd", "dvds"], 
            ["mando", "remote", "control"], 
        ], 
        ["objects-puppets", 
            ["títere", "títeres", "titere", "titeres", "marioneta", "marionetas", "puppet", "puppets"], 
            [], 
        ], 
        ["objects-tables", 
            ["mesa", "mesas", "table", "tables"], 
            ["mesas de asta", "mesa redonda"], 
        ], 
        ["people", 
            ["people", ], 
            [], 
        ], 
        ["plants", 
            ["planta", "plantas", "plant", "plants", ], 
            ["edificio", "building", "planta de residuos", "primera planta", "segunda planta", "tercera planta", "cuarta planta", "quinta planta", "sexta planta", "power plant"], 
        ], 
        ["plaques", 
            ["placa", "placas", "plaque", "plaques", ], 
            ["solar", "solares", "alicante"],  #varias Plaça en alicante #File:Alicante en julio de 2022 55.jpg
        ], 
        ["streets", 
            ["calle", "calles", "callejero", "callejeando", "avenida", "plaza", "rotonda"], 
            ["plaza de toros"], 
        ], 
        ["vehicles-air", #for airports see buildings-airports
            ["avion", "aeronave", "desfile aereo", "exhibicion aerea", "helicoptero", "aircraft", "aircrafts", "plane", "helicopter"], 
            ["viaje en avión", "viaje en avion"], 
        ], 
        ["vehicles-rail", #for roads see buildings-train-stations
            ["tren", "trenes", "train", "trains", "tranvia", "tranvias"], 
            ["viaje en tren", "vistas desde el tren", "vistas desde tren"], 
        ], 
        ["vehicles-road", #for roads see buildings-roads
            ["autobus", "bus", "camion", "coche", "coches", "furgoneta", "automobile", "automobiles", "automocion", "car", "cars", "museo emt"], 
            ["viaje en coche", "viaje en bus", "viaje en autobús", "viaje en autobus"], 
        ], 
        ["vehicles-sea", #for seaports see buildings-ports
            ["barco", "barcos", "catamaran", "crucero", "navio", "vaporcito", "boat", "ship", "watercraft", "watercrafts"], 
            ["calle crucero", "viaje en barco"], 
        ], 
        ["views", 
            ["vista", "vistas", "mirador", "miradores", "views", ], 
            [], 
        ], 
        ["views-from-automobiles", 
            ["viaje en coche", "vistas desde el coche", "por carretera", "por autovía", "por autovia"], 
            [], 
        ], 
        ["views-from-trains", 
            ["viaje en tren", "vistas desde el tren", "ave sevilla"], 
            [], 
        ], 
        ["water-body", 
            ["embalse", "pantano", "laguna", ], 
            [], 
        ], 
        ["water-rivers", 
            ["rio", "rios", "arroyo", "afluente", "river", "rivers", "guadalete", "guadalquivir"], 
            ["instituto cervantes", "ribera del río", "ríos rosas"], 
        ], 
        ["water-sea", 
            ["mar", "oceano", "playa", "playas", "beach", "beaches", ], 
            ["apartamentos", "multicines", "puerta del mar", "legado del mar"], 
        ], 
        ["weather", 
            ["lluvia", "nieve", "nube", "nubes", "temporal", "tormenta", "viento", "calor", "frio", "termometro", "rain", "snow", "storm", "weather"], 
            [], 
        ], 
        ["weather-sunshine", 
            ["amanecer", "sunshine"], 
            [], 
        ], 
        ["weather-sunset", 
            ["atardecer", "sunset"], 
            [], 
        ], 
        
        #prehistoria
        ["prehistory", 
            ["prehistory", "prehistoric"], 
            [], 
        ], 
        ["bronze-age", 
            ["bronze-age", "bronze age"], 
            [], 
        ], 
        ["copper-age", 
            ["copper-age", "copper age"], 
            [], 
        ], 
        ["iron-age", 
            ["iron-age", "iron age"], 
            [], 
        ], 
        ["stone-age", 
            ["stone-age", "stone age"], 
            [], 
        ], 
        ["paleolithic", 
            ["paleolithic"], 
            [], 
        ], 
        ["mesolithic", 
            ["mesolithic"], 
            [], 
        ], 
        ["neolithic", 
            ["neolithic"], 
            [], 
        ], 
        
        #estilos
        #rococo https://commons.wikimedia.org/w/index.php?title=File:Museo_de_Salamanca_en_octubre_de_2022_23.jpg&curid=124250086&diff=724017192&oldid=699324973
        
        #otras cosas
        ["plots",
            ["wmchart", "wmcharts", ],
            [],
        ], 
        
    ]
    #paises
    countries_dic = {
        "Algeria": ["Argelia"], 
        "Belarus": ["Bielorrusia", "Bielorusia", "Minsk", "Belarussian"], 
        "Burkina Faso": ["Burkina Faso", "Burkinabe"], 
        "Czech Republic": ["Republica Checa", "República Checa", "Czech"], 
        "France": ["Francia", "French", "Paris", "París"], 
        "Germany": ["Alemania", "German", "Berlin", "Berlín"], 
        "Ghana": ["Ghana"], 
        "Greece": ["Grecia", "griego", "griega"], 
        "Italy": ["Italia", "Italian", "Roma", "Rome"], 
        "Mali": ["Mali"], 
        "Morocco": ["Marruecos"], 
        "Myanmar": ["Birmania", "Burma", "Myanmar"], 
        "Nepal": ["Nepal", "Nepalese", "Nepalí", "Nepali"], 
        "Portugal": ["Lisboa", "Portuguese", "Portugués", "Portugues"], 
        "Russia": ["Rusia", "Moscu", "Moscú", "Moscow", "Ruso", "Rusa"], 
        "United States": ["Estados Unidos", "EEUU", "Washington", "estadounidense"], 
    }
    countries = list(set(countries_dic.keys()))
    countries.sort()
    for country in countries:
        country_list = [
            "%s" % (country),
                ["%s" % (country)] + countries_dic[country],
                [], 
        ]
        topics.append(country_list)
    #siglos
    suffixes = {1:"st",2:"nd",3:"rd",21:"st",22:"nd",23:"rd"}
    for century in range(4, 20): #no meter el siglo XXI, hay mucha cosa del estilo January 2005 in Andalusia, ni siglos 1 y 2, porque hay fotos 001 002, 256, etc
        suffix = century in suffixes.keys() and suffixes[century] or "th"
        century_list = [
            "%d%s-century" % (century, suffix),
                ["%d%s century" % (century, suffix), "%d%s-century" % (century, suffix), "%d\d0s" % (century-1), "%d\d\d" % (century-1), "%d00" % (century)],
                ["%d00" % (century-1), "class", "boeing", "number", "[a-z]\-\d", "metros", "glorieta", "resolution"], #modelos de trenes, coches...
            ]
        topics.append(century_list)
        century_list = [
            "%d%s-century BC" % (century, suffix),
                ["%d%s century BC" % (century, suffix), "%d%s-century BC" % (century, suffix), "%d\d0s BC" % (century-1), "%d\d\d BC" % (century-1), "%d00 BC" % (century)],
                ["%d00" % (century-1), "class", "boeing", "number", "[a-z]\-\d", "metros", "glorieta", "resolution"], #modelos de trenes, coches...
        ]
        topics.append(century_list)
    #opencv
    ocrtext = re.sub(r'\s+', ' ', ocr(filename=filename))
    if len(re.sub(r'(?im)\b(.{1,3})\b', '', ocrtext)) >= 25:
        print("*****", "\nOCR:\n", ocrtext, "\n*****")
        imageswithtext = ["images-with-text", ["."], []] #. como palabra que siempre va a estar
        topics.append(imageswithtext)
    
    topics.sort()
    topics_c = 1
    for topic, topic_keywords, topic_keywords_exclusion in topics:
        categories = re.findall(r"(?im)\[\[\s*Category\s*:\s*([^\[\]\|]+?)\s*[\[\]\|]", newtext)
        categories.append(pagetitle.split("File:")[1])
        categories = [removeAccents(category.lower()) for category in categories]
        for category in categories:
            regexp = "|".join([removeAccents(topic_keyword.lower()) for topic_keyword in topic_keywords])
            regexpexc = "|".join([removeAccents(topic_keyword_exclusion.lower()) for topic_keyword_exclusion in topic_keywords_exclusion])
            if re.search(r"(?im)\b(%s)\b" % (regexp), category):
                if regexpexc and re.search(r"(?im)\b(%s)\b" % (regexpexc), removeAccents(" ".join(categories)).lower()):
                    continue
                newtext = re.sub(regexpcredit, r'\1|topic%s%s|%s' % ((topics_c == 1 and '=' or str(topics_c)+"="), topic, creditend), newtext)
                topics_c += 1
                break
    if topics_c == 1:
        print("topic no encontrado")   
    
    #timeline gallery
    timelinegallery = generateTimelineGallery(pagetitle=pagetitle)
    if timelinegallery:
        print(timelinegallery)
        newtext = re.sub(regexpcredit, r'\1|timeline-gallery=%s|%s' % (timelinegallery, creditend), newtext)
    
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
        newtext = re.sub(r'(?im)(\|\s*source\s*=\s*)({{User:Emijrp/credit}}|Self[ -]?published work by \[\[User:emijrp\|emijrp\]\])', r'\1{{own work}}', newtext)
    return newtext

def creditByWhatlinkshere():
    purgeedit = True #force template cache purge
    skip = ''
    skip = 'File:Andén 0 Estación de Chamberí en septiembre de 2022 01.jpg'
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
        
        if not page.title() in timeline.keys():
            print("No en timeline, saltamos")
            continue
        
        newtext = page.text
        newtext = replaceAuthor(newtext=newtext)
        newtext = replaceSource(newtext=newtext)
        newtext = addMetadata(pagetitle=page.title(), newtext=newtext, pagelink=page.full_url(), pagehtml=page.getImagePageHtml(), filelink=page.get_file_url(url_width=1200))
        if newtext != page.text or purgeedit:
            pywikibot.showDiff(page.text, newtext)
            page.text = newtext
            page.save('BOT - Updating credit template')

def creditByCategory():
    commons = pywikibot.Site('commons', 'commons')
    category = pywikibot.Category(commons, '15-O Demonstrations, Cádiz')
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
            pagehtml = urllib.request.urlopen(req).read().strip().decode('utf-8')
            images = re.findall(r'title="(File:[^<>]+?)">File:', pagehtml)
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

def loadTimeline(overwrite=False):
    global timeline
    
    filename = "timeline.pickle"
    if overwrite:
        commons = pywikibot.Site('commons', 'commons')
        category = pywikibot.Category(commons, 'Images by User:Emijrp')
        gen = pagegenerators.CategorizedPageGenerator(category, content=True)
        for page in gen:
            #print('==', page.title(), '==')
            title = page.title()
            text = page.text
            if re.findall(r'(?im)(cropped)', title) or re.findall(r'(?im)(\{\{\s*(extracted|cropped))', text): # ignorar las recortadas
                continue
            if re.findall(r'(?im)(withheld)', text): # ignorar las location withheld
                continue
            
            m = re.findall(r'(?im)^\|\s*(?:date|photo date)\s*=\s*(?:\{\{(?:according ?to ?exif ?data|taken ?on)\s*\|\s*(?:1=)?)?\s*(\d\d\d\d-\d\d-\d\d( \d\d:\d\d(:\d\d)?)?)', text)
            if m:
                time = m[0][0]
                if len(time) == 19 or len(time) == 16 or len(time) == 10:
                    #print(title, time)
                    if not title in timeline.keys():
                        timeline[title] = time
                        if len(timeline.keys()) % 100 == 0:
                            print("Loaded %d timelines" % (len(timeline.keys())))
                            #break
        pickle.dump(timeline, open(filename, "wb"))
        pickle.dump(timeline, open(filename+datetime.datetime.today().strftime("%Y%m%d%H%M%S"), "wb"))
    else:
        if os.path.exists(filename):
            timeline = pickle.load(open(filename, "rb"))
            print("Loaded %d timelines" % (len(timeline.keys())))

def main():
    loadTimeline(overwrite=False)
    #creditByFlickrUrl()
    #creditByCategory()
    creditByWhatlinkshere()

if __name__ == '__main__':
    main()
