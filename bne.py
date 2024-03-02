#!/usr/bin/env python
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

import datetime
import os
import pickle
import re
import sys
import time
import unicodedata
import urllib.request

import pywikibot
from pywikibot import pagegenerators

def processobj(obj="", props=""):
    if not obj or not props:
        return
    #print(props.items())
    try:
        objid = props[obj]["https://datos.bne.es/def/id"]
        objtitle = props[obj]["https://datos.bne.es/def/P3002"]
        objpublisher = props[obj]["https://datos.bne.es/def/P3001"]
        objisbn = props[obj]["https://datos.bne.es/def/P3013"]
        objtype = props[obj]["https://datos.bne.es/def/P3064"]
        objpages = props[obj]["https://datos.bne.es/def/P3004"]
        objpages = re.findall(r"(?im)^(\d\d\d+) *(?:p\.?|pp\.?|pag\.?|páginas)$", objpages)[0]
        if objid and objtitle and objpublisher and objisbn and objtype in ["Libro"] and objpages:
            print("https://datos.bne.es/resource/%s" % (objid))
            print(objtitle)
            print(objpublisher)
            print(objisbn)
            print(objtype)
            print(objpages)
            print()
    except:
        pass

def main():
    f = open("bibliograficos.nt", "r")
    c = 0
    cobj = 0
    props = {}
    prevobj = ""
    for line in f:
        c += 1
        line = line.strip().strip(".").strip()
        #print(line)
        obj, prop, value, trail = ["", "", "", ""]
        if len(re.findall(" ", line)) >= 3:
            splits = line.split(" ")
            obj = splits[0]
            prop = splits[1]
            value = " ".join(splits[2:])
        elif len(re.findall(" ", line)) == 2:
            obj, prop, value = line.split(" ")
        else:
            print("ERROR: ", line)
            sys.exit()
        obj = obj.strip().strip("<").strip().strip(">").strip()
        if not obj in props:
            props[obj] = {}
        prop = prop.strip().strip("<").strip().strip(">").strip()
        value = value.strip().strip("<").strip().strip(">").strip('"').strip()
        props[obj][prop] = value
        #print(str(c), obj, prop, value)
        
        if obj != prevobj:
            processobj(obj=prevobj, props=props)
            if prevobj in props:
                del props[prevobj]
                cobj += 1
                if cobj % 10000 == 0:
                    print("Analysed", cobj, "objects")
        props[obj][prop] = value
        prevobj = obj
    f.close()

if __name__ == "__main__":
    main()
