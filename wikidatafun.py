#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2025 emijrp <emijrp@gmail.com>
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
import json
import os
import re
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse
import pywikibot

def cronstop():
	return
	if datetime.datetime.now().isoweekday() in [1, 2, 3, 4, 5]: #1 Monday
		if datetime.datetime.now().hour > 4 and datetime.datetime.now().hour < 18:
			sys.exit()

def isArtwork(text=""):
	if not text:
		return False
	if re.search(r"(?im)(artwork|painting|statue|coin|numism|Google Art Project|PD[- ]Art)", text):
		return True
	return False

def myBotWasReverted(page='', botnick="Emijrpbot"):
	if not page or not botnick:
		return False
	hist = page.revisions(reverse=False, total=50)
	for rev in hist:
		#print(rev)
		if re.search(r"(?im)(revert|rv|undo|undid).*%s" % (botnick), rev["comment"]):
			return True
	return False

def addClaimsToCommonsFile(site, mid, claims, overwritecomment="", comments=[], q=""):
	if not overwritecomment and not comments and not q:
		return 
	#https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim
	csrf_token = site.tokens['csrf']
	data = '{"claims":[%s]}' % (",".join(claims))
	comments.sort()
	summary = "BOT - Adding [[Commons:Structured data|structured data]]"
	if overwritecomment:
		summary = overwritecomment
	elif comments and q:
		summary = "BOT - Adding [[Commons:Structured data|structured data]] based on Wikidata item [[:d:%s|%s]]: %s" % (q, q, ", ".join(comments))
	elif comments and not q:
		summary = "BOT - Adding [[Commons:Structured data|structured data]] based on file information: %s" % (", ".join(comments))
	elif not comments and q:
		summary = "BOT - Adding [[Commons:Structured data|structured data]] based on Wikidata item [[:d:%s|%s]]" % (q, q)
	else:
		summary = "BOT - Adding [[Commons:Structured data|structured data]]"
	payload = {
	  'action' : 'wbeditentity',
	  'format' : 'json',
	  'id' : mid,
	  'data' : data,
	  'token' : csrf_token,
	  'bot' : True, 
	  'summary': summary,
	  'tags': 'BotSDC',
	}
	request = site.simple_request(**payload)
	try:
	  r = request.submit()
	except:
	  print("ERROR while saving")

def addP180Claim(site="", mid="", q="", rank="", overwritecomment=""):
	if not site or not mid or not q or not rank or not overwritecomment:
		return
	
	claims = getClaimsFromCommonsFile(site=site, mid=mid)
	if not claims:
		print("Error al recuperar claims, saltamos")
		return
	elif claims and "claims" in claims and claims["claims"] == { }:
		print("No tiene claims, no inicializado, inicializamos")
	
	if "claims" in claims:
		if "P180" in claims["claims"]: #p180 depicts
			for p180 in claims["claims"]["P180"]:
				if p180["mainsnak"]["datavalue"]["value"]["id"] == q:
					print("--> Ya tiene claim depicts, saltamos", q)
					return
		#https://commons.wikimedia.org/w/index.php?title=File%3ANaturkundemuseum_Berlin_-_Archaeopteryx_-_Eichst%C3%A4tt.jpg&diff=987725284&oldid=987724207
		#https://commons.wikimedia.org/w/api.php?action=wbgetclaims&entity=M2457215
		if re.search(r"(?im)%s" % (q), str(claims)):
			print("--> Ya usa este Q en algun sitio, saltamos", q)
			return
		print("--> No se encontro claim, anadimos", q)
		if "P180" in claims["claims"]:
			print("###########Tiene otros P180")
		claimstoadd = []
		depictsclaim = """{ "mainsnak": { "snaktype": "value", "property": "P180", "datavalue": {"value": {"entity-type": "item", "numeric-id": "%s", "id": "%s"}, "type":"wikibase-entityid"} }, "type": "statement", "rank": "%s" }""" % (q[1:], q, rank)
		claimstoadd.append(depictsclaim)
		
		if claimstoadd and overwritecomment:
			addClaimsToCommonsFile(site=site, mid=mid, claims=claimstoadd, overwritecomment=overwritecomment)
		else:
			print("No se encontraron claims para anadir")
			return

def getClaimsFromCommonsFile(site, mid):
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
	except pywikibot.exceptions.APIError as e:
		if e.code == 'no-such-entity':
			return { "claims": { } }
	return 

def removeAccents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
				if unicodedata.category(c) != 'Mn')

def getURL(url='', retry=False, timeout=30):
	raw = ''
	version = 110
	req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/%d.0' % (version) })
	try:
		raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
	except:
		sleep = 10 # seconds
		maxsleep = 60
		while retry and sleep <= maxsleep:
			print('Error while retrieving: %s' % (url))
			print('Retry in %s seconds...' % (sleep))
			time.sleep(sleep)
			try:
				req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/%d.0' % (version) })
				raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
			except:
				version += 1
			sleep = sleep * 2
	return raw

def isScriptAliveCore(pidfilename=''):
	while 1:
		with open(pidfilename, 'w') as f:
			f.write('alive')
		time.sleep(10)

def isScriptAlive(filename=''):
	alivefilename = '%s.alive' % (filename)
	if os.path.exists(alivefilename):
		print('Script is working, we wont launch another copy. Exiting...')
		os.remove(alivefilename)
		sys.exit()
	else:
		print('Alive file not found. We continue this instance')
		try:
		   _thread.start_new_thread(isScriptAliveCore, (alivefilename,) )
		except:
		   print("Error: unable to start thread")

def getUserEditCount(user='', site=''):
	if user and site:
		editcounturl = 'https://%s/w/api.php?action=query&list=users&ususers=%s&usprop=editcount&format=json' % (site, urllib.parse.quote(user))
		raw = getURL(editcounturl)
		json1 = json.loads(raw)
		if 'query' in json1 and 'users' in json1['query'] and 'editcount' in json1['query']['users'][0]:
			return json1['query']['users'][0]['editcount']
	return 0

def loadSPARQL(sparql=''):
	json1 = ''
	if sparql:
		try:
			json1 = json.loads(sparql)
			return json1
		except:
			print('Error downloading SPARQL? Malformatted JSON? Skiping\n')
			return 
	else:
		print('Server return empty file')
		return 
	return

def getAllCountries():
	url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3FitemLabel%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ6256.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D%0AORDER%20BY%20ASC(%3FitemLabel)'
	url = '%s&format=json' % (url)
	sparql = getURL(url=url)
	json1 = loadSPARQL(sparql=sparql)
	countries = []
	for result in json1['results']['bindings']:
		#print(result)
		q = result['item']['value'].split('/entity/')[1]
		label = result['itemLabel']['value']
		countries.append([label, q])
	return countries

