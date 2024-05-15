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

import pywikibot
import json

imageinfocache = {}

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
    global imageinfocache
    mimetype = False
    result = getImageInfo(site=site, pagetitle=pagetitle)
    pages = result["query"]["pages"]
    for pageid, pagedata in pages.items():
        mimetype = pagedata["imageinfo"][0]["mime"]
    return mimetype

def getSize(site, pagetitle, size):
    global imageinfocache
    value = False
    result = getImageInfo(site=site, pagetitle=pagetitle)
    pages = result["query"]["pages"]
    for pageid, pagedata in pages.items():
        value = pagedata["imageinfo"][0][size]
    return value

def getSHA1(site, pagetitle):
    global imageinfocache
    sha1 = False
    result = getImageInfo(site=site, pagetitle=pagetitle)
    pages = result["query"]["pages"]
    for pageid, pagedata in pages.items():
        sha1 = pagedata["imageinfo"][0]["sha1"]
    return sha1

def genP1163(site, page): #media type
    prop = "P1163"
    mimetype = getMIMEtype(site, page.title())
    claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": "%s", "type":"string"} }, "type": "statement", "rank": "normal" }""" % (prop, mimetype)
    comment = "media type"
    return claim, comment
    
def genP2048(site, page): #height
    prop = "P2048"
    height = getSize(site, page.title(), size="height")
    claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q355198"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, height)
    comment = "height"
    return claim, comment

def genP2049(site, page): #width
    prop = "P2049"
    width = getSize(site, page.title(), size="width")
    claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q355198"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, width)
    comment = "width"
    return claim, comment

def genP3575(site, page): #size
    prop = "P3575"
    size = getSize(site, page.title(), size="size")
    claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": {"amount": "+%s", "unit": "http://www.wikidata.org/entity/Q8799"}, "type":"quantity"} }, "type": "statement", "rank": "normal" }""" % (prop, size)
    comment = "size"
    return claim, comment

def genP4092(site, page): #sha1
    prop = "P4092"
    sha1 = getSHA1(site, page.title())
    claim = """{ "mainsnak": { "snaktype": "value", "property": "%s", "datavalue": {"value": "%s", "type":"string"} }, "type": "statement", "qualifiers": {"P459": [{"snaktype": "value", "property": "P459", "datavalue": {"value": {"entity-type": "item", "numeric-id": 13414952, "id": "Q13414952"}, "type": "wikibase-entityid"}, "datatype": "wikibase-item"}]}, "rank": "normal" }""" % (prop, sha1)
    comment = "sha1"
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
    else:
        return "", ""

def main():
    site = pywikibot.Site('commons', 'commons')
    pagetitles = [
        "File:Champlain_Quebec_city.jpg", 
        "File:Parque de El Retiro de Madrid en mayo de 2023 17.jpg", 
        "File:Parque de El Retiro de Madrid en mayo de 2023 18.jpg", 
    ]
    props = [
        "P1163", #media type
        "P2048", #height
        "P2049", #width
        "P3575", #size
        "P4092", #sha1
    ]
    for pagetitle in pagetitles:
        page = pywikibot.Page(site, pagetitle)
        print("==", page.title(), "==")
        mid = "M" + str(page.pageid)
        print(mid)
        if getMIMEtype(site=site, pagetitle=page.title()) != "image/jpeg":
            print("No es JPG, saltamos")
            continue
        
        claims = getClaims(site=site, mid=mid)
        #print(claims["claims"]["P4092"])
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
