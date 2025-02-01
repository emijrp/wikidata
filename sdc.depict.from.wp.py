#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024-2025 emijrp <emijrp@gmail.com>
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

import random
import re
import string
import sys
import time
import urllib.parse

import pywikibot
from pywikibot import pagegenerators
from wikidatafun import *

def main():
	targetlangs = ["es", "fr", "de", "pt", "it", "sv", "nl", "pl", "ca", "id", "no", "li", "hu", "da"]
	targetlangs += ["en"] * len(targetlangs)
	targetlang = random.choice(targetlangs)
	sitewp = pywikibot.Site(targetlang, 'wikipedia')
	sitecommons = pywikibot.Site('commons', 'commons')
	sitewd = pywikibot.Site('wikidata', 'wikidata')
	repowd = sitewd.data_repository()
	
	for loop in range(10000):
		time.sleep(1)
		#randomstart = ''.join(random.choice("!¡()" + string.ascii_letters + string.digits) for xx in range(5))
		randomstart = ''.join(random.choice(string.ascii_letters) for xx in range(5))
		randomstart = randomstart[0].upper() + randomstart[1:].lower()
		print("Random start from:", randomstart)
		gen = pagegenerators.AllpagesPageGenerator(site=sitewp, start=randomstart, namespace=0, includeredirects=False, content=True)
		pre = pagegenerators.PreloadingGenerator(gen, groupsize=50)
		c = 0
		for page in pre:
			wtitle = page.title()
			wtext = page.text
			#print(wtitle)
			if c % 10 == 0:
				print(c,")", wtitle)
			if page.isRedirectPage():
				continue
			c += 1
			if c >= 25000:
				c = 0
				print("###Skiping to other Wikipedia region")
				break #this is to randomize more
			
			"""
			#mode1 filename compared to page title
			m = re.findall(r"(?im)\[\[\s*(?:File|Image)\s*:\s*([^\|\[\]]+?)\|", wtext)
			m = list(set(m))
			for mm in m:
				if len(mm) < 8 or not re.search(r"(?im)\.(jpe?g|gif|png|tiff?)", mm):
					continue
				if len(wtitle) < 8 or not " " in wtitle or re.search(r"(?im)[^a-záéíóúàèìòùäëïöüçñ\,\.\-\_ ]", wtitle):
					continue
				filename = "File:"+mm.strip()
				#cuidado al comparar, q si soy demasiado flexible con los simbolos (numeros por ej), puede salir como positivo cosas diferentes
				symbols = "[0-9\-\.\,\!\¡\"\$\&\(\)\*\?\¿\~\@\= ]*?"
				wtitlex = wtitle.replace(".", " ").replace(",", " ").replace("-", " ").replace("(", " ").replace(")", " ").replace("_", " ")
				wtitlex = wtitlex.replace(" ", symbols)
				titleregexp = r"(?im)^File:%s(%s|%s)%s\.(?:jpe?g|gif|png|tiff?)$" % (symbols, wtitle, wtitlex, symbols)
				regexpmonths = "(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|apr|jun|jul|aug|sept?|oct|nov|dec)"
				regexpdays = "(([012]?\d|3[01])(st|nd|rd|th))"
				filenameclean = re.sub(r"(?im)\b(cropp?e?d?|rotated?|portrait|before|after|cut|sir|prince|dr|in|on|at|en|circa|c|rev|img|imagen?|pic|picture|photo|photograph|foto|fotograf[íi]a|the|[a-z]+\d+|\d+[a-z]+|%s|%s)\b" % (regexpdays, regexpmonths), "", filename)
				#print(titleregexp, filenameclean)
				if re.search(titleregexp, filenameclean):
					print(page.full_url(), filename)
			
			continue
			"""
			
			#mode2 linked thumb descriptions
			fileregexpdefault = "(?:File|Image)"
			fileregexps = {
				"default": fileregexpdefault, 
				"de": "(?:File|Image|Datei)", 
				"en": fileregexpdefault, 
				"es": "(?:File|Image|Fichero|Imagen)", 
				"fr": "(?:File|Image|Fichier)", 
				"it": fileregexpdefault, 
				"pt": "(?:File|Image|Imagem)", 
				"sv": "(?:File|Image|Fil)", 
			}
			thumbregexpdefault = "(?:\|\s*(?:thumb|thumbnail|frame|center|right|left|upright\s*=?\s*\d*\.?\d*|upleft\s*=?\s*\d*\.?\d*|\d+px|\d+x\d+px)\s*)*"
			thumbregexps = {
				"default": thumbregexpdefault, 
				"de": "(?:\|\s*(?:thumb|thumbnail|frame|center|right|left|upright\s*=?\s*\d*\.?\d*|upleft\s*=?\s*\d*\.?\d*|\d+px|\d+x\d+px|mini|links)\s*)*", 
				"en": thumbregexpdefault, 
				"es": thumbregexpdefault, 
				"fr": "(?:\|\s*(?:thumb|thumbnail|frame|center|right|left|upright\s*=?\s*\d*\.?\d*|upleft\s*=?\s*\d*\.?\d*|\d+px|\d+x\d+px|vignette|redresse)\s*)*", 
				"it": "(?:\|\s*(?:thumb|thumbnail|frame|center|right|left|upright\s*=?\s*\d*\.?\d*|upleft\s*=?\s*\d*\.?\d*|\d+px|\d+x\d+px|miniatura)\s*)*", 
				"pt": "(?:\|\s*(?:thumb|thumbnail|frame|center|right|left|upright\s*=?\s*\d*\.?\d*|upleft\s*=?\s*\d*\.?\d*|\d+px|\d+x\d+px|miniatura|miniaturadaimagem|esquerda|direita)\s*)*", 
				"sv": "(?:\|\s*(?:thumb|thumbnail|frame|center|right|left|upright\s*=?\s*\d*\.?\d*|upleft\s*=?\s*\d*\.?\d*|\d+px|\d+x\d+px|miniatyr)\s*)*", 
			}
			captionregexpdefault = "(?:[a-z\,\.\(\) ]{,4}\s*\'*\[\[([^\|\[\]\#]+?)(?:\|[\|\[\]\#]*?)?\]\]\'*\s*[a-z\,\.\(\) ]{,4}\s*\.?)" #no mas de 4 chars o puede ser frases cortas que lleve a error
			captionregexps = {
				"default": captionregexpdefault, 
				"de": captionregexpdefault, 
				#la caption es solo un [[link]], o un [[link]] con palabras muy concretas antes o después (The, Aerial view...), o un [[link]] seguido de coma y un número de caracteres (mínimo 10, máximo 100) sin ningún enlace más
				"en": "(?:(?:(?:The|Oldtown of|View of|Aerial view|Exterior view|Another view|Details?|Detailed view|Photograph of|Image of|Portrait of)\s*(?:of)?\s*)?\s*\'*\[\[([^\|\[\]\#]+?)(?:\|[\|\[\]\#]*?)?\]\]\'*\s*(?:(?:in|on|at|before|after) (?:\[?\[?(?:\d+|night|sunset|sunrise|spring|summer|autumn|winter)\]?\]?|skyline|\(?\d{4}\)?)|, [a-z\,\.\(\) ]{10,100})?\s*\.?)", 
				"es": captionregexpdefault, 
				"fr": captionregexpdefault, 
				"it": captionregexpdefault, 
				"pt": captionregexpdefault, 
				"sv": captionregexpdefault, 
			}
			if targetlang in fileregexps.keys() and targetlang in thumbregexps.keys() and targetlang in captionregexps.keys():
				#el \[?\[? es para que capture también los File: de los <gallery> que no llevan [[ ni ]]
				m = re.findall(r"(?im)^\[?\[?\s*%s\s*:\s*([^\|\[\]]+?)%s\s*\|\s*%s\s*(?:\]\]|\n)" % (fileregexps[targetlang], thumbregexps[targetlang], captionregexps[targetlang]), wtext)
			else: #other langs, generic
				m = re.findall(r"(?im)^\[?\[?\s*%s\s*:\s*([^\|\[\]]+?)%s\s*\|\s*%s\s*(?:\]\]|\n)" % (fileregexps["default"], thumbregexps["default"], captionregexps["default"]), wtext)
			
			for mm in m:
				filename = mm[0].strip()
				thumblink = mm[1].split("|")[0].strip()
				if not filename.lower().endswith(".jpg") and not filename.lower().endswith(".jpeg"):
					continue
				print(filename, thumblink)
				filepagewp = pywikibot.Page(sitewp, "File:"+filename)
				if filepagewp.exists():
					print("Existe pagina para este fichero en wp, saltamos")
					continue
				filepagecommons = pywikibot.Page(sitecommons, "File:"+filename)
				if not filepagecommons.exists():
					print("No existe pagina para este fichero en commons, saltamos")
					continue
				if filepagecommons.isRedirectPage():
					filepagecommons = filepagecommons.getRedirectTarget()
				if isArtwork(text=filepagecommons.text):
					print("Obra de arte, saltamos")
					continue
				if myBotWasReverted(page=filepagecommons):
					print("Bot reverted, skiping")
					continue
				thumblinkwp = pywikibot.Page(sitewp, thumblink)
				if not thumblinkwp.exists():
					print("No existe pagina para este thumblink en wp, saltamos")
					continue
				if thumblinkwp.isRedirectPage():
					thumblinkwp = thumblinkwp.getRedirectTarget()
				item = ''
				try:
					item = pywikibot.ItemPage.fromPage(thumblinkwp)
				except:
					pass
				if not item:
					print("No se encontro item asociado, saltamos")
					continue
				q = item.title()
				print(", ".join([wtitle, filename, thumblinkwp.title(), item.title()]))
				print(filepagecommons.full_url())
				mid = "M" + str(filepagecommons.pageid)
				print(mid)
				
				overwritecomment = "BOT - Adding [[Commons:Structured data|structured data]] based on Wikipedia pages [[:%s:%s|%s]]/[[:%s:%s|%s]] and Wikidata item [[:d:%s|%s]]: depicts" % (targetlang, page.title(), page.title(), targetlang, thumblinkwp.title(), thumblinkwp.title(), q, q)
				addP180Claim(site=sitecommons, mid=mid, q=q, rank="normal", overwritecomment=overwritecomment, skipifP180exists=True) #rank=normal, skipifP180exists=True to avoid redundancy https://commons.wikimedia.org/w/index.php?title=File%3A2007_Audi_Q7_3.0_TDI_quattro_01.jpg&diff=988221095&oldid=988219347

if __name__ == '__main__':
	main()
