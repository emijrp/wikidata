#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 emijrp <emijrp@gmail.com>
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
import pywikibot
from pywikibot import pagegenerators
import json
import urllib.request

imageinfocache = {}
imagehtmlcache = {}

def getClaims(site, mid):
    payload = {
      'action' : 'wbgetclaims',
      'format' : 'json',
      'entity' : mid,
    }
    request = site.simple_request(**payload)
    try:
        r = request.submit()
        #return json.loads(r)
        return r
    except pywikibot.data.api.APIError as e:
        print("ERROR:", e)
    return {}

def getHTML(pagelink):
    global imagehtmlcache
    if not pagelink in imagehtmlcache:
        try:
            req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
            pagehtml = urllib.request.urlopen(req).read().strip().decode('utf-8')
        except:
            time.sleep(60)
            req = urllib.request.Request(pagelink, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
            pagehtml = urllib.request.urlopen(req).read().strip().decode('utf-8')
        if pagelink:
            imagehtmlcache[pagelink] = pagehtml
    return imagehtmlcache[pagelink]

def addClaims(site, mid, claims, comments):
    #https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim
    csrf_token = site.tokens['csrf']
    data = '{"claims":[%s]}' % (",".join(claims))
    comments.sort()
    payload = {
      'action' : 'wbeditentity',
      'format' : 'json',
      'id' : mid,
      'data' : data,
      'token' : csrf_token,
      'bot' : True, 
      'summary': "BOT - Adding [[Commons:Structured data|structured data]] based on file information: %s" % (", ".join(comments)),
    }
    request = site.simple_request(**payload)
    try:
      r = request.submit()
    except pywikibot.data.api.APIError as e:
      print("ERROR:", e)

def getImageInfo(site, pagetitle):
    global imageinfocache
    if not pagetitle in imageinfocache:
        request = site.simple_request(action="query", titles=pagetitle, prop="imageinfo", iiprop="mime|size|sha1")
        result = request.submit()
        imageinfocache[pagetitle] = result
    return imageinfocache[pagetitle]

def getMIMEtype(site, pagetitle):
    mimetype = False
    result = getImageInfo(site=site, pagetitle=pagetitle)
    pages = result["query"]["pages"]
    for pageid, pagedata in pages.items():
        mimetype = pagedata["imageinfo"][0]["mime"]
    return mimetype

def getSize(site, pagetitle, size):
    value = False
    result = getImageInfo(site=site, pagetitle=pagetitle)
    pages = result["query"]["pages"]
    for pageid, pagedata in pages.items():
        value = pagedata["imageinfo"][0][size]
    return value

def getSHA1(site, pagetitle):
    sha1 = False
    result = getImageInfo(site=site, pagetitle=pagetitle)
    pages = result["query"]["pages"]
    for pageid, pagedata in pages.items():
        sha1 = pagedata["imageinfo"][0]["sha1"]
    return sha1

def getISO(site, pagelink):
    iso = False
    pagehtml = getHTML(pagelink=pagelink)
    m = re.findall(r'(?im)<tr class="exif-isospeedratings"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if m:
        iso = m[0].strip()
        iso = re.sub(r',', r'', iso)
    return iso

def getExposureTime(site, pagelink):
    exposuretime = False
    pagehtml = getHTML(pagelink=pagelink)
    m = re.findall(r'(?im)<tr class="exif-exposuretime"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if m:
        exposuretime = m[0].split('(')[1].split(')')[0].strip()
        exposuretime = re.sub(r',', r'', exposuretime)
    return exposuretime

def getFNumber(site, pagelink):
    fnumber = False
    pagehtml = getHTML(pagelink=pagelink)
    m = re.findall(r'(?im)<tr class="exif-fnumber"><th>.*?</th><td>(.*?)</td></tr>', pagehtml)
    if m:
        fnumber = m[0].split('f/')[1].strip()
        fnumber = re.sub(r',', r'', fnumber)
    return fnumber

def getFocalLength(site, pagelink):
    focallength = False
    pagehtml = getHTML(pagelink=pagelink)
    m = re.findall(r'(?im)<tr class="exif-focallength"><th>[^<>]*?</th><td>(.*?)</td></tr>', pagehtml)
    if m:
        focallength = m[0].split('mm')[0].strip()
        focallength = re.sub(r',', r'', focallength)
    return focallength

def genP1163(site, page): #media type
    claim = False
    comment = False
    prop = "P1163"
    mimetype = getMIMEtype(site, page.title())
    if mimetype:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": "%s", "type":"string"} }, "type": "statement", "rank": "normal" }""" % (prop, mimetype)
        comment = "media type"
    return claim, comment
    
def genP2048(site, page): #height
    claim = False
    comment = False
    prop = "P2048"
    height = getSize(site, page.title(), size="height")
    if height:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q355198"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, height)
        comment = "height"
    return claim, comment

def genP2049(site, page): #width
    claim = False
    comment = False
    prop = "P2049"
    width = getSize(site, page.title(), size="width")
    if width:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q355198"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, width)
        comment = "width"
    return claim, comment

def genP3575(site, page): #size
    claim = False
    comment = False
    prop = "P3575"
    size = getSize(site, page.title(), size="size")
    if size:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q8799"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, size)
        comment = "size"
    return claim, comment

def genP4092(site, page): #sha1
    claim = False
    comment = False
    prop = "P4092"
    sha1 = getSHA1(site, page.title())
    if sha1:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": "%s", "type":"string"} }, "type": "statement", "qualifiers": {"P459": [{"snaktype": "value", "property": "P459", "datavalue": {"value": {"entity-type": "item", "numeric-id": 13414952, "id": "Q13414952"}, "type": "wikibase-entityid"}, "datatype": "wikibase-item"}]}, "rank": "normal" }""" % (prop, sha1)
        comment = "sha1"
    return claim, comment

def genP6789(site, page): #iso
    claim = False
    comment = False
    prop = "P6789"
    iso = getISO(site, page.full_url())
    if iso:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "1"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, iso)
        comment = "iso speed"
    return claim, comment

def genP6757(site, page): #exposure time
    claim = False
    comment = False
    prop = "P6757"
    exposuretime = getExposureTime(site, page.full_url())
    if exposuretime:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q11574"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, exposuretime)
        comment = "exposure time"
    return claim, comment

def genP6790(site, page): #f number
    claim = False
    comment = False
    prop = "P6790"
    fnumber = getFNumber(site, page.full_url())
    if fnumber:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "1"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, fnumber)
        comment = "f-number"
    return claim, comment

def genP2151(site, page): #focal length
    claim = False
    comment = False
    prop = "P2151"
    focallength = getFocalLength(site, page.full_url())
    if focallength:
        claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q174789"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, focallength)
        comment = "focal length"
    return claim, comment

def genClaim(site, page, prop):
    if prop == "P1163": #media type
        return genP1163(site, page)
    
    elif prop == "P2048": #height
        return genP2048(site, page)
    elif prop == "P2049": #width
        return genP2049(site, page)
    elif prop == "P3575": #size
        return genP3575(site, page)
    elif prop == "P4092": #sha1
        return genP4092(site, page)
    
    elif prop == "P6789": #iso
        return genP6789(site, page)
    elif prop == "P6757": #exposure time
        return genP6757(site, page)
    elif prop == "P6790": #f number
        return genP6790(site, page)
    elif prop == "P2151": #focal length
        return genP2151(site, page)
    
    else:
        return "", ""

def main():
    site = pywikibot.Site('commons', 'commons')
    props = [
        "P1163", #media type
        
        "P2048", #height
        "P2049", #width
        "P3575", #size
        "P4092", #sha1
        
        "P6789", #iso
        "P6757", #exposure time
        "P6790", #f number
        "P2151", #focal length
    ]
    category = pywikibot.Category(site, 'Images by User:Emijrp by date')
    category = pywikibot.Category(site, 'Images of Madrid by User:Emijrp taken in 2023')
    gen = pagegenerators.CategorizedPageGenerator(category, namespaces=[6])
    for page in gen:
        print('==', page.title(), '==')
        page = pywikibot.Page(site, page.title())
        print(page.full_url())
        mid = "M" + str(page.pageid)
        print(mid)
        if getMIMEtype(site=site, pagetitle=page.title()) != "image/jpeg":
            print("No es JPG, saltamos")
            continue
        
        claims = getClaims(site=site, mid=mid)
        #print(claims["claims"]["P2151"])
        claimstoadd = []
        comments = []
        
        for prop in props:
            if prop in claims["claims"]:
                print("Ya tiene", prop)
            else:
                claim, comment = genClaim(site=site, page=page, prop=prop)
                if claim and comment:
                    print("Anadiendo", prop, comment, claim)
                    claimstoadd.append(claim)
                    comments.append(comment)
        
        if claimstoadd and comments and len(claimstoadd) == len(comments):
            pass
            addClaims(site=site, mid=mid, claims=claimstoadd, comments=comments)

if __name__ == '__main__':
    main()

