#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2025 emijrp <emijrp@gmail.com>
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
import hashlib
import json
import math
import os
import random
import re
import string
import sys
import time
import urllib.parse
import threading
from queue import Queue

import pywikibot
from pywikibot import pagegenerators
from pywikibot.textlib import extract_sections
from wikidatafun import *

def generateChartCreationsbyyear(valuesbyyear={}):
	maxvalue = 0
	valuesbyyear_list = []
	for year, value in valuesbyyear.items():
		valuesbyyear_list.append([year, value])
		if value > maxvalue:
			maxvalue = value
	valuesbyyear_list.sort()
	divisor = 10 * len(str(maxvalue))
	maxvalueuprounded = math.ceil(maxvalue / divisor) * divisor
	valuesbyyear_ = "\n".join(["|%s value=%s|%s text=%s" % (x, y, x, y) for x, y in valuesbyyear_list])
	chart = f"""{{{{Wikipedia:Statistics/Statistics/EasyTimeline
|max value={maxvalueuprounded}|ScaleMajor={maxvalueuprounded}|ScaleMinor={int(maxvalueuprounded / 4)}
|title posx=400|title posy=150|title fontsize=L|title=Creations by year|color=blue
{valuesbyyear_}
}}}}"""
	return chart

def generateChartPagesbyclass(valuesbyclass={}):
	total = sum(valuesbyclass.values())
	chart = f"""{{{{Pie chart
|caption=Pages by '''quality'''.|radius=110
|label1=Featured Article|value1={"FA" in valuesbyclass and round(valuesbyclass["FA"] / (total / 100), 2) or 0}|color1=#9cbdff
|label2=Featured List|value2={"FL" in valuesbyclass and round(valuesbyclass["FL"] / (total / 100), 2) or 0}|color2=#9cbdff
|label3=A-Class|value3={"A" in valuesbyclass and round(valuesbyclass["A"] / (total / 100), 2) or 0}|color3=#66ffff
|label4=Good Article|value4={"GA" in valuesbyclass and round(valuesbyclass["GA"] / (total / 100), 2) or 0}|color4=#66ff66
|label5=B-Class|value5={"B" in valuesbyclass and round(valuesbyclass["B"] / (total / 100), 2) or 0}|color5=#b2ff66
|label6=C-Class|value6={"C" in valuesbyclass and round(valuesbyclass["C"] / (total / 100), 2) or 0}|color6=#ffff66
|label7=Start-Class|value7={"Start" in valuesbyclass and round(valuesbyclass["Start"] / (total / 100), 2) or 0}|color7=#ffaa66
|label8=Stub-Class|value8={"Stub" in valuesbyclass and round(valuesbyclass["Stub"] / (total / 100), 2) or 0}|color8=#ffa4a4
|label9=List-Class|value9={"List" in valuesbyclass and round(valuesbyclass["List"] / (total / 100), 2) or 0}|color9=#c7b1ff
|other-label=???|other=1|other-color=#dcdcdc
}}}}"""
	return chart

def generateChartPagesbyimportance(valuesbyimportance={}):
	total = sum(valuesbyimportance.values())
	chart = f"""{{{{Pie chart
|caption=Pages by '''importance'''.|radius=110
|label1=Top|value1={"Top" in valuesbyimportance and round(valuesbyimportance["Top"] / (total / 100), 2) or 0}|color1=#ff97ff
|label2=High|value2={"High" in valuesbyimportance and round(valuesbyimportance["High"] / (total / 100), 2) or 0}|color2=#ffacff
|label3=Mid|value3={"Mid" in valuesbyimportance and round(valuesbyimportance["Mid"] / (total / 100), 2) or 0}|color3=#ffc1ff
|label4=Low|value4={"Low" in valuesbyimportance and round(valuesbyimportance["Low"] / (total / 100), 2) or 0}|color4=#ffd6ff
|other-label=???|other=1|other-color=#dcdcdc
}}}}"""
	return chart

def generateChartPagesbynamespace(valuesbynamespace={}):
	total = sum(valuesbynamespace.values())
	valuesbynamespace_list = [[v, k] for k, v in valuesbynamespace.items()]
	valuesbynamespace_list.sort(reverse=True)
	c = 1
	rows = []
	for v, k in valuesbynamespace_list:
		rows.append(f"""|label{c}={k}|value{c}={round(v / (total / 100), 2)}""")
		c += 1
	rows = "\n".join(rows)
	chart = f"""{{{{Pie chart
|caption=Pages by '''namespace'''.|radius=110
{rows}
}}}}"""
	return chart

def getURLThreading(url="", queue=""):
	queue.put([url, getURL(url=url)])

def getPageInfo(site="", page="", wikiproject=""):
	pagetitle = page.title()
	pagetitlequoted = urllib.parse.quote(pagetitle)
	pageinfo = {}
	
	item = pywikibot.ItemPage.fromPage(page)
	wikidataq = item.getID()
	pageinfo["item"] = wikidataq
	
	wikipageurl = "https://en.wikipedia.org/w/index.php?title=%s" % (pagetitlequoted)
	pageinfourl = "https://en.wikipedia.org/w/index.php?title=%s&action=info" % (pagetitlequoted)
	xtoolsurl = "https://xtools.wmcloud.org/api/page/assessments/en.wikipedia.org/%s?classonly=false" % (pagetitlequoted)
	wikidatajsonurl = "https://www.wikidata.org/wiki/Special:EntityData/%s.json" % (wikidataq)
	threads = []
	queue = Queue()
	thread1 = threading.Thread(target=getURLThreading, args=(wikipageurl,queue))
	threads.append(thread1)
	thread1.start()
	thread2 = threading.Thread(target=getURLThreading, args=(pageinfourl,queue))
	threads.append(thread2)
	thread2.start()
	thread3 = threading.Thread(target=getURLThreading, args=(xtoolsurl,queue))
	threads.append(thread3)
	thread3.start()
	thread4 = threading.Thread(target=getURLThreading, args=(wikidatajsonurl,queue))
	threads.append(thread4)
	thread4.start()
	for thread in threads:
		thread.join()
	while not queue.empty():
		response = queue.get()
		#print("Response:", response)
		if response[0] == wikipageurl:
			pageinfo["wikipageraw"] = response[1]
		elif response[0] == pageinfourl:
			pageinfo["pageinforaw"] = response[1]
		elif response[0] == xtoolsurl:
			pageinfo["xtoolsraw"] = response[1]
			pageinfo["xtoolsjson"] = json.loads(pageinfo["xtoolsraw"])
		elif response[0] == wikidatajsonurl:
			pageinfo["wikidataraw"] = response[1]
			pageinfo["wikidatajson"] = json.loads(pageinfo["wikidataraw"])
	
	#info from action=info
	m = re.findall(r'(?im)<tr style="vertical-align: top;"><td><a [^<>]*?>Number of redirects to this page</a></td><td>([^<>]*?)</td></tr>', pageinfo["pageinforaw"])
	pageinfo["redirects"] = m and int(re.sub(",", "", m[0])) or 0
	m = re.findall(r'(?im)<tr id="mw-pageinfo-watchers" style="vertical-align: top;"><td>Number of page watchers</td><td>([^<>]*?)</td></tr>', pageinfo["pageinforaw"])
	pageinfo["watchers"] = m and m[0] != "Fewer than 30 watchers" and int(re.sub(",", "", m[0])) or 0
	m = re.findall(r'(?im)<tr id="mw-pvi-month-count".*>([^<>]*?)</a></div></td></tr>', pageinfo["pageinforaw"])
	pageinfo["views30days"] = m and int(re.sub(",", "", m[0])) or 0
	m = re.findall(r'(?im)<tr style="vertical-align: top;"><td>Local description</td><td>([^<>]*?)</td></tr>', pageinfo["pageinforaw"])
	pageinfo["shortdescription"] = m and len(m[0]) or 0
	m = re.findall(r'(?im)<tr id="mw-pageinfo-edits" style="vertical-align: top;"><td>Total number of edits</td><td>([^<>]*?)</td></tr>', pageinfo["pageinforaw"])
	pageinfo["edits"] = m and int(re.sub(",", "", m[0])) or 0
	m = re.findall(r'(?im)<tr id="mw-pageinfo-recent-edits" style="vertical-align: top;"><td>Recent number of edits \(within past 30 days\)</td><td>([^<>]*?)</td></tr>', pageinfo["pageinforaw"])
	pageinfo["edits30days"] = m and int(re.sub(",", "", m[0])) or 0
	
	m = re.findall(r'(?im)<tr id="mw-pageinfo-firsttime" style="vertical-align: top;"><td>Date of page creation</td><td><a [^<>]*?>([^<>]*?)</a></td></tr>', pageinfo["pageinforaw"])
	pageinfo["creationdate"] = m and datetime.datetime.strptime(m[0], "%H:%M, %d %B %Y").strftime("%Y-%m-%d") or " "
	pageinfo["creationdatetime"] = m and datetime.datetime.strptime(m[0], "%H:%M, %d %B %Y").strftime("%Y-%m-%d %H:%M") or " "
	m = re.findall(r'(?im)Date of page creation</td><td><a href="/w/index\.php\?title=.*?&amp;oldid=(\d+)"', pageinfo["pageinforaw"])
	pageinfo["firstedit"] = m and m[0] or 0
	
	m = re.findall(r'(?im)<tr id="mw-pageinfo-lasttime" style="vertical-align: top;"><td>Date of latest edit</td><td><a [^<>]*?>([^<>]*?)</a></td></tr>', pageinfo["pageinforaw"])
	latesteditdate = datetime.datetime.strptime(m[0], "%H:%M, %d %B %Y")
	pageinfo["latesteditdate"] = m and datetime.datetime.strptime(m[0], "%H:%M, %d %B %Y").strftime("%Y-%m-%d") or " "
	pageinfo["latesteditdatetime"] = m and datetime.datetime.strptime(m[0], "%H:%M, %d %B %Y").strftime("%Y-%m-%d %H:%M") or " "
	m = re.findall(r'(?im)Date of latest edit</td><td><a href="/w/index\.php\?title=.*?&amp;oldid=(\d+)"', pageinfo["pageinforaw"])
	pageinfo["latestedit"] = m and m[0] or 0
	pageinfo["dayssincelatestedit"] = (datetime.datetime.today()-latesteditdate).days
	
	pageinfo["pageeditprotection"] = not re.search(r'(?im)<tr id="mw-restriction-edit" style="vertical-align: top;"><td>Edit</td><td>Allow all users \(no expiry set\)</td></tr>', pageinfo["pageinforaw"])
	pageinfo["pagemoveprotection"] = not re.search(r'(?im)<tr id="mw-restriction-move" style="vertical-align: top;"><td>Move</td><td>Allow all users \(no expiry set\)</td></tr>', pageinfo["pageinforaw"])
	
	#info from xtools
	pageinfo["class"] = " "
	pageinfo["importance"] = " "
	if "pages" in pageinfo["xtoolsjson"] and pagetitle in pageinfo["xtoolsjson"]["pages"] and "wikiprojects" in pageinfo["xtoolsjson"]["pages"][pagetitle]:
		if wikiproject in pageinfo["xtoolsjson"]["pages"][pagetitle]["wikiprojects"]:
			if "class" in pageinfo["xtoolsjson"]["pages"][pagetitle]["wikiprojects"][wikiproject]:
				pageinfo["class"] = pageinfo["xtoolsjson"]["pages"][pagetitle]["wikiprojects"][wikiproject]["class"]["value"]
				if pageinfo["class"] == "???":
					pageinfo["class"] = " "
			if "importance" in pageinfo["xtoolsjson"]["pages"][pagetitle]["wikiprojects"][wikiproject]:
				pageinfo["importance"] = pageinfo["xtoolsjson"]["pages"][pagetitle]["wikiprojects"][wikiproject]["importance"]["value"]
				if pageinfo["importance"] == "???":
					pageinfo["importance"] = " "
	
	#info from wikipage
	pageinfo["redlinks"] = list(set([x[0].upper()+x[1:] for x in re.findall(r'(?im)class="new" title="([^<>]+?) \(page does not exist\)">', pageinfo["wikipageraw"])]))
	pageinfo["interwikis"] = len(re.findall(r"interlanguage-link-target", pageinfo["wikipageraw"]))
	m = re.findall(r'(?im)<li class="wb-otherproject-link wb-otherproject-commons mw-list-item"><a href="https://commons\.wikimedia\.org/wiki/([^ ]+?)" ', pageinfo["wikipageraw"])
	pageinfo["commons"] = m and m[0] or " "
	
	#info from wikidata
	pageinfo["wikidatalabel"] = pageinfo["item"] and ("en" in pageinfo["wikidatajson"]["entities"][pageinfo["item"]]["labels"].keys() or "mul" in pageinfo["wikidatajson"]["entities"][pageinfo["item"]]["labels"].keys()) and 1 or 0
	pageinfo["wikidataaliases"] = pageinfo["item"] and "en" in pageinfo["wikidatajson"]["entities"][pageinfo["item"]]["aliases"].keys() and len(pageinfo["wikidatajson"]["entities"][pageinfo["item"]]["aliases"]["en"]) or 0
	pageinfo["wikidataaliases"] += pageinfo["item"] and "mul" in pageinfo["wikidatajson"]["entities"][pageinfo["item"]]["aliases"].keys() and len(pageinfo["wikidatajson"]["entities"][pageinfo["item"]]["aliases"]["mul"]) or 0
	pageinfo["wikidataclaims"] = pageinfo["item"] and len(re.findall('"mainsnak"', pageinfo["wikidataraw"]))
	
	#derived info
	pageinfo["size"] = len(page.text.encode()) #"{:,}".format(len(text.encode()))
	pageinfo["inlinks"] = 0 #len(list(page.getReferences(namespaces=0)))
	pageinfo["weblinks"] = countWeblinks(text=page.text)
	pageinfo["outlinks"] = countLinks(text=page.text)
	pageinfo["images"] = countImages(text=page.text)
	pageinfo["categories"] = countCategories(text=page.text)
	pageinfo["references"] = countReferences(text=page.text)
	pageinfo["templates"] = countTemplates(text=page.text)
	pageinfo["infoboxes"] = countInfoboxes(text=page.text)
	pageinfo["tables"] = countTables(text=page.text)
	pageinfo["mathformulas"] = countMathFormulas(text=page.text)
	pageinfo["maintenancetags"] = 0
	pageinfo["quality"] = getQuality(text=page.text)
	pageinfo["quality_"] = " "
	if pageinfo["quality"] == "featured article":
		pageinfo["quality_"] = "{{icon|fa}}"
	elif pageinfo["quality"] == "featured list":
		pageinfo["quality_"] = "{{icon|fl}}"
	elif pageinfo["quality"] == "good article":
		pageinfo["quality_"] = "{{icon|ga}}"
	pageinfo["namespace"] = page.namespace().id
	pageinfo["namespacename"] = site.namespaces[page.namespace().id].canonical_name
	pageinfo["namespacename"] = pageinfo["namespacename"] == "" and "Article" or pageinfo["namespacename"]
	pageinfo["domains"] = getDomains(text=page.text)
	pageinfo["isbns"] = getISBNs(text=page.text)
	pageinfo["dois"] = getDOIs(text=page.text)
	pageinfo["categories_list"] = getCategories(text=page.text)
	pageinfo["templates_list"] = getTemplates(text=page.text)
	return pageinfo

def getDomains(text=""):
	return list(set([re.sub(r"(?im)^www\.", "", x.lower().strip()).strip() for x in re.findall(r"(?im)://([^/]+)/", text)]))
def getISBNs(text=""):
	return list(set([x.replace("-", "").strip() for x in re.findall(r"(?im)isbn[ \=\|]*?([\d\-]+)", text)]))
def getDOIs(text=""):
	return list(set([x.strip() for x in re.findall(r"(?im)doi[ \=\|]+?([^ \|\n\}]{10,})", text)]))
def getCategories(text=""):
	return list(set([x.strip().capitalize() for x in re.findall(r"(?im)\[\[\s*Category\s*:\s*([^\|\]]+?)\s*[\|\]]", text)]))
def getTemplates(text=""):
	return list(set([x.strip().capitalize() for x in re.findall(r"(?im)[^\{]\{\{\s*([^\|\}]+?)\s*[\|\}]", text)]))
def countCategories(text=""):
	return len(re.findall(r"(?im)\[\[\s*Category\s*:", text))
def countImages(text=""):
	return len(re.findall(r"(?im)(File|Image)\s*:", text)) + len(re.findall(r"(?im)=[^:\n]+?\.(jpe?g|pne?g|svg|gif)", text))
def countLinks(text=""):
	return len(re.findall(r"(?im)\[\[", text)) - len(re.findall(r"(?im)\[\[\s*Category\s*:", text)) - len(re.findall(r"(?im)\[\[\s*(File|Image)\s*:", text))
def countWeblinks(text=""):
	return len(re.findall(r"(?im)://", text))
def countReferences(text=""):
	return len(re.findall(r"(?im)<\s*/\s*ref\s*>", text))
def countMathFormulas(text=""):
	return len(re.findall(r"(?im)<\s*/\s*math\s*>", text))
def countTemplates(text=""):
	return len(re.findall(r"(?im)[^\{\}]\{\{[^\{\}]", text))
def countInfoboxes(text=""):
	return len(re.findall(r"(?im)\{\{\s*Infobox[^\{\}]", text))
def countTables(text=""):
	return len(re.findall(r"(?im)^(\{\||<\s*table)", text))
def getQuality(text=""):
	quality = "-"
	if re.search(r"(?im)\{\{\s*Featured article\s*\}\}", text):
		quality = "featured article"
	elif re.search(r"(?im)\{\{\s*Featured list\s*\}\}", text):
		quality = "featured list"
	elif re.search(r"(?im)\{\{\s*Good article\s*\}\}", text):
		quality = "good article"
	return quality

def main():
	sitewp = pywikibot.Site("en", "wikipedia")
	sitecommons = pywikibot.Site("commons", "commons")
	sitewd = pywikibot.Site("wikidata", "wikidata")
	repowd = sitewd.data_repository()
	
	t1 = time.time()
	wikiproject = "Artificial Intelligence"
	wikiproject = "Numbers"
	catname = "Category:WikiProject %s articles" % (wikiproject)
	wikiprojectpage = pywikibot.Page(sitewp, "Wikipedia:WikiProject " + wikiproject)
	m = re.findall(r"(?im)image\s*=\s*([^\n]+?\.(?:jpe?g|pne?g|svg))", wikiprojectpage.text)
	wikiprojectlogo = m and m[0].strip() or "WikiProject Council with transparent background.svg"
	maintenance = {
		"Category:All Wikipedia articles in need of updating": [], 
		"Category:All accuracy disputes": [], 
		"Category:All articles containing potentially dated statements": [], 
		"Category:All articles with topics of unclear notability": [], 
		"Category:All articles needing coordinates": [], 
		"Category:All articles with dead external links": [], 
		"Category:All articles with bare URLs for citations": [], 
		"Category:All articles lacking in-text citations": [], 
		"Category:All pages needing cleanup": [], 
		"Category:All articles with unsourced statements": [], 
		"Category:All articles to be expanded": [], 
		"Category:Articles with multiple maintenance issues": [], 
		"Category:Pages missing lead section": [], 
		"Category:All Wikipedia articles needing clarification": [], 
		"Category:All articles lacking reliable references": [], 
		"Category:All articles needing rewrite": [], 
		"Category:All articles with a promotional tone": [], 
		"Category:All orphaned articles": [], 
		"Category:All articles needing additional references": [], 
		"Category:All Wikipedia neutral point of view disputes": [], 
		"Category:All articles with style issues": [], 
		"Category:All articles with specifically marked weasel-worded phrases": [], 
		"Category:Articles missing coordinates with coordinates on Wikidata": [], 
	}
	
	notice = "{{notice|This page is automatically generated and updated by a bot. If you edit it, your changes will be overwritten in the next update. ''Last update: ~~~~~''}}"
	intro = f"""{notice}
[[File:{wikiprojectlogo}|right|200px]]
This page is an '''analysis''' of the [[:{catname}|content tracked]] by '''[[Wikipedia:WikiProject {wikiproject}|WikiProject {wikiproject}]]'''."""
	category = pywikibot.Category(sitewp, catname)
	c = 0
	header = """{{static row numbers}}{{sticky header}}{{mw-datatable}}{{table alignment}}
{| class="wikitable sortable plainlinks static-row-numbers sticky-header mw-datatable defaultcenter col1left" style="font-size: 80%;"
! Page
! Creation<ref>Date of creation of page.</ref>
! Size<ref>Size in bytes. Pages smaller than 1,000 bytes are in grey.</ref>
! Views<ref>Page views in the past 30 days. Pages with less than 30 views in that period are in grey.</ref>
! {{vert header|Total edits<ref>Total edits in page history.</ref>}}
! {{vert header|Recent edits<ref>Edits in the past 30 days. Pages with 0 edits in that period are in grey.</ref>}}
! {{vert header|Days since last edit<ref>Number of days since the page was edited.</ref>}}
! {{vert header|Watchers<ref>Number of page watchers.</ref>}}
! {{vert header|Links<ref>Number of <code><nowiki>[[links]]</nowiki></code>.</ref>}}
! {{vert header|Redirects<ref>Number of redirects to this page. Pages without redirects are in grey.</ref>}}
! {{vert header|Weblinks<ref>Number of links to other websites (<code>://</code>).</ref>}}
! {{vert header|Images<ref>Number of images. Pages without images are in grey.</ref>}}
! {{vert header|References<ref>Number of <code><nowiki><ref&gt;</ref&gt;</nowiki></code>.</ref>}}
! {{vert header|Templates<ref>Number of templates.</ref>}}
! {{vert header|Infoboxes<ref>Number of infoboxes.</ref>}}
! {{vert header|Tables<ref>Number of tables.</ref>}}
! {{vert header|Short description<ref>Length of the {{tl|short description}}, if any.</ref>}}
! {{vert header|Categories<ref>Number of categories.</ref>}}
! {{vert header|Math formulas<ref>Number of math formulas.</ref>}}
! {{vert header|[[#Maintenance|Maintenance tags]]<ref>Number of maintenance tags.</ref>}}
! {{vert header|Edit protected<ref>Page is protected for edits.</ref>}}
! {{vert header|Move protected<ref>Page is protected for moves.</ref>}}
! {{vert header|Interwikis<ref>Number of languages this page is available.</ref>}}
! {{vert header|Commons link<ref>Link to Commons gallery or category, if any. Pages without Commons links are in grey.</ref>}}
! {{vert header|Wikidata item<ref>Q item in Wikidata for this page, if any. Pages without Wikidata item are in grey.</ref>}}
! {{vert header|Wikidata label<ref>English (or mul:) label for this page Wikidata item.</ref>}}
! {{vert header|Wikidata aliases<ref>English (and mul:) aliases for this page Wikidata item.</ref>}}
! {{vert header|Wikidata claims<ref>Claims for this page Wikidata item.</ref>}}
! {{vert header|Quality<ref>Quality level.</ref>}}
! {{vert header|Importance<ref>Importance level.</ref>}}
|-
"""
	rows = []
	chartcreationdate = {}
	chartclass = {}
	chartimportance = {}
	chartnamespace = {}
	pagesbycreationdatetime = []
	pagesbysize = []
	pagesbyviews30days = []
	pagesbyedits = []
	pagesbyedits30days = []
	pagesbyimages = []
	pagesbyreferences = []
	pagesbycategories = []
	pagesbyredirects = []
	pagesbywatchers = []
	domains = {}
	isbns = {}
	dois = {}
	categories = {}
	templates = {}
	redlinks = {}
	for page in category.articles():
		if page.isTalkPage():
			page = page.toggleTalkPage()
		if page.namespace() != 0:
			namespacename = sitewp.namespaces[page.namespace().id].canonical_name
			chartnamespace[namespacename] = chartnamespace.get(namespacename, 0) + 1
			continue
		if page.isRedirectPage():
			continue
		
		c += 1
		#retrieve page info
		pageinfo = getPageInfo(site=sitewp, page=page, wikiproject=wikiproject)
		pagesbycreationdatetime.append([pageinfo["creationdate"], page.title()])
		pagesbysize.append([pageinfo["size"], page.title()])
		pagesbyviews30days.append([pageinfo["views30days"], page.title()])
		pagesbyedits.append([pageinfo["edits"], page.title()])
		pagesbyedits30days.append([pageinfo["edits30days"], page.title()])
		pagesbyimages.append([pageinfo["images"], page.title()])
		pagesbyreferences.append([pageinfo["references"], page.title()])
		pagesbycategories.append([pageinfo["categories"], page.title()])
		pagesbyredirects.append([pageinfo["redirects"], page.title()])
		pagesbywatchers.append([pageinfo["watchers"] and pageinfo["watchers"] or 0, page.title()])
		for maintenancecat, maintenancepages in maintenance.items():
			if maintenancecat in pageinfo["pageinforaw"]:
				maintenance[maintenancecat].append(page.title())
				pageinfo["maintenancetags"] += 1
		for domain in pageinfo["domains"]:
			domains[domain] = domains.get(domain, 0) + 1
		for isbn in pageinfo["isbns"]:
			isbns[isbn] = isbns.get(isbn, 0) + 1
		for doi in pageinfo["dois"]:
			dois[doi] = dois.get(doi, 0) + 1
		for category in pageinfo["categories_list"]:
			categories[category] = categories.get(category, 0) + 1
		for template in pageinfo["templates_list"]:
			templates[template] = templates.get(template, 0) + 1
		for redlink in pageinfo["redlinks"]:
			redlinks[redlink] = redlinks.get(redlink, 0) + 1
		#print(pageinfo.items())
		#pagelinks = "{{pagelinks|%s}}" % (page.title())
		
		#generate row
		pagelinks = "[[%s]]" % (page.title())
		pagetitle_ = re.sub(" ", "_", page.title())
		row = f"""|{pagelinks}"""
		row += f"""\n|[//en.wikipedia.org/w/index.php?oldid={pageinfo["firstedit"]} {pageinfo["creationdate"]}]"""
		row += f"""\n|{pageinfo["size"] < 1000 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["size"])}"""
		row += f"""\n|{pageinfo["views30days"] < 30 and 'style="background-color:#dcdcdc"|' or ''}[//pageviews.wmcloud.org/?pages={pagetitle_}&project=en.wikipedia.org {"{:,}".format(pageinfo["views30days"])}]"""
		row += f"""\n|[//en.wikipedia.org/w/index.php?title={pagetitle_}&action=history {"{:,}".format(pageinfo["edits"])}]"""
		row += f"""\n|{pageinfo["edits30days"] == 0 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["edits30days"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["dayssincelatestedit"])}"""
		row += f"""\n|{pageinfo["watchers"] == " " and 'style="background-color:#dcdcdc"|' or ''}{pageinfo["watchers"] and "{:,}".format(pageinfo["watchers"]) or " "}"""
		row += f"""\n|{"{:,}".format(pageinfo["outlinks"])}"""
		row += f"""\n|{pageinfo["redirects"] == 0 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["redirects"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["weblinks"])}"""
		row += f"""\n|{pageinfo["images"] == 0 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["images"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["references"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["templates"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["infoboxes"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["tables"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["shortdescription"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["categories"])}"""
		row += f"""\n|{"{:,}".format(pageinfo["mathformulas"])}"""
		row += f"""\n|{pageinfo["maintenancetags"] > 0 and 'style="background-color:#dcdcdc"|' or ''}{pageinfo["maintenancetags"]}"""
		row += f"""\n|{pageinfo["pageeditprotection"] and "[[File:Semi-protection-shackle.svg|10px|link=|Edit protected]]" or " "}"""
		row += f"""\n|{pageinfo["pagemoveprotection"] and "[[File:Semi-protection-shackle.svg|10px|link=|Move protected]]" or " "}"""
		row += f"""\n|{"{:,}".format(pageinfo["interwikis"])}"""
		row += f"""\n|{pageinfo["commons"] != " " and "[[commons:%s|C]]" % (pageinfo["commons"]) or 'style="background-color:#dcdcdc"| '}"""
		row += f"""\n|{pageinfo["item"] != " " and "[[d:%s|Q]]" % (pageinfo["item"]) or 'style="background-color:#dcdcdc"| '}"""
		row += f"""\n|{pageinfo["wikidatalabel"] == 0 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["wikidatalabel"])}"""
		row += f"""\n|{pageinfo["wikidataaliases"] == 0 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["wikidataaliases"])}"""
		row += f"""\n|{pageinfo["wikidataclaims"] == 0 and 'style="background-color:#dcdcdc"|' or ''}{"{:,}".format(pageinfo["wikidataclaims"])}"""
		row += f"""\n{{{{Class|{pageinfo["class"]}}}}}"""
		row += f"""\n{{{{Importance|{pageinfo["importance"]}}}}}"""
		#print(row)
		rows.append(row)
		print(re.sub(r"\n", "", row))
		
		#chart info
		chartcreationdate[pageinfo["creationdate"][:4]] = chartcreationdate.get(pageinfo["creationdate"][:4], 0) + 1
		chartnamespace[pageinfo["namespacename"]] = chartnamespace.get(pageinfo["namespacename"], 0) + 1
		chartclass[pageinfo["class"]] = chartclass.get(pageinfo["class"], 0) + 1
		chartimportance[pageinfo["importance"]] = chartimportance.get(pageinfo["importance"], 0) + 1
		
		if c >= 50000:
			break
		
	footer = """\n|}\n{{sticky table end}}"""
	
	#table
	rows.sort()
	table = header + "\n|-\n".join(rows) + footer
	
	#summary
	pagesbycreationdatetime.sort(reverse=True)
	newestpagedatetime, newestpage = pagesbycreationdatetime[0]
	oldestpagedatetime, oldestpage = pagesbycreationdatetime[-1]
	chartcreationdate_list = [[v, k] for k, v in chartcreationdate.items()]
	chartcreationdate_list.sort(reverse=True)
	pagesbysize.sort(reverse=True)
	biggestpagesize, biggestpage = pagesbysize[0]
	smallestpagesize, smallestpage = pagesbysize[-1]
	pagesbyviews30days.sort(reverse=True)
	mostviewed30dayspageviews, mostviewed30dayspage = pagesbyviews30days[0]
	leastviewed30dayspageviews, leastviewed30dayspage = pagesbyviews30days[-1]
	pagesbyedits.sort(reverse=True)
	mosteditedpageedits, mosteditedpage = pagesbyedits[0]
	leasteditedpageedits, leasteditedpage = pagesbyedits[-1]
	pagesbyedits30days.sort(reverse=True)
	mostedited30dayspageedits, mostedited30dayspage = pagesbyedits30days[0]
	leastedited30dayspageedits, leastedited30dayspage = pagesbyedits30days[-1]
	pagesbyimages.sort(reverse=True)
	mostimagespageimages, mostimagespage = pagesbyimages[0]
	pagesbyreferences.sort(reverse=True)
	mostreferencespagereferences, mostreferencespage = pagesbyreferences[0]
	pagesbycategories.sort(reverse=True)
	mostcategoriespagecategories, mostcategoriespage = pagesbycategories[0]
	pagesbyredirects.sort(reverse=True)
	mostredirectspageredirects, mostredirectspage = pagesbyredirects[0]
	pagesbywatchers.sort(reverse=True)
	mostwatcherspagewatchers, mostwatcherspage = pagesbywatchers[0]
	
	summary = f"""A total of '''[[#Analyzed pages|{len(rows)} pages]]''' were analyzed in '''{"{:,}".format(int(time.time()-t1))} seconds'''. The pages received '''{"{:,}".format(sum([x for x, y in pagesbyviews30days]))} views''' and '''{"{:,}".format(sum([x for x, y in pagesbyedits30days]))} edits''' in the past 30 days.

The '''oldest''' page is [[{oldestpage}]] ({oldestpagedatetime}) and the '''newest''' is [[{newestpage}]] ({newestpagedatetime}). The most '''[[#Visualizations|prolific year]]''' is [[{chartcreationdate_list[0][1]}]] ({chartcreationdate[chartcreationdate_list[0][1]]} pages). The '''biggest''' is [[{biggestpage}]] ({"{:,}".format(biggestpagesize)} bytes) and the '''smallest''' is [[{smallestpage}]] ({"{:,}".format(smallestpagesize)} bytes). The '''most viewed''' in the past 30 days is [[{mostviewed30dayspage}]] ({"{:,}".format(mostviewed30dayspageviews)} views) and the '''least viewed''' in the past 30 days is [[{leastviewed30dayspage}]] ({"{:,}".format(leastviewed30dayspageviews)} views).

The '''most edited''' page in the past 30 days is [[{mostedited30dayspage}]] ({"{:,}".format(mostedited30dayspageedits)} edits) and the '''least edited''' in the past 30 days is [[{leastedited30dayspage}]] ({"{:,}".format(leastedited30dayspageedits)} edits). The '''most edited''' is [[{mosteditedpage}]] ({"{:,}".format(mosteditedpageedits)} edits) and the '''least edited''' is [[{leasteditedpage}]] ({"{:,}".format(leasteditedpageedits)} edits). The '''most illustrated''' is [[{mostimagespage}]] ({"{:,}".format(mostimagespageimages)} images), the '''most referenced''' is [[{mostreferencespage}]] ({"{:,}".format(mostreferencespagereferences)} references), the '''most categorized''' is [[{mostcategoriespage}]] ({"{:,}".format(mostcategoriespagecategories)} categories), the '''most redirected''' is [[{mostredirectspage}]] ({"{:,}".format(mostredirectspageredirects)} redirects) and the '''most watched''' is [[{mostwatcherspage}]] ({"{:,}".format(mostwatcherspagewatchers)} watchers).
"""
	charts_plain = f"""{generateChartCreationsbyyear(valuesbyyear=chartcreationdate)}
{{|
| valign=top | {generateChartPagesbyclass(valuesbyclass=chartclass)}
| valign=top | {generateChartPagesbyimportance(valuesbyimportance=chartimportance)}
|}}"""
	#| valign=top | {generateChartPagesbynamespace(valuesbynamespace=chartnamespace)}
	maintenance_list = [[k, v] for k, v in maintenance.items()]
	maintenance_list.sort()
	maintenance_plain = ""
	for maintenancecat, maintenancepages in maintenance_list:
		if maintenancepages:
			maintenancepages.sort()
			maintenance_plain += f"""* '''[[:{maintenancecat}|{maintenancecat}]]''': {", ".join(["[[%s]]" % (x) for x in maintenancepages])}.
"""
	if maintenance_plain:
		maintenance_plain = "The following pages have one or more '''maintenance''' tags.\n" + maintenance_plain
	else:
		maintenance_plain = "No pages needing '''maintenance''' found."
	
	#rankings
	rankinglimit = 20
	rankingdois = ""
	dois_list = [[freq, doi] for doi, freq in dois.items()]
	dois_list.sort(reverse=True)
	for freq, doi in dois_list[:rankinglimit]:
		rankingdois += "\n|-\n| [https://doi.org/%s %s] || %s " % (doi, doi, freq)
	rankingisbns = ""
	isbns_list = [[freq, isbn] for isbn, freq in isbns.items()]
	isbns_list.sort(reverse=True)
	for freq, isbn in isbns_list[:rankinglimit]:
		rankingisbns += "\n|-\n| [[Special:BookSources/%s|%s]] || %s " % (isbn, isbn, freq)
	rankingdomains = ""
	domains_list = [[freq, domain] for domain, freq in domains.items()]
	domains_list.sort(reverse=True)
	for freq, domain in domains_list[:rankinglimit]:
		rankingdomains += "\n|-\n| [http://%s %s] || %s " % (domain, domain, freq)
	rankingtemplates = ""
	templates_list = [[freq, template] for template, freq in templates.items()]
	templates_list.sort(reverse=True)
	for freq, template in templates_list[:rankinglimit]:
		rankingtemplates += "\n|-\n| {{tl|%s}} || %s " % (template, freq)
	rankingcategories = ""
	categories_list = [[freq, category] for category, freq in categories.items()]
	categories_list.sort(reverse=True)
	for freq, category in categories_list[:rankinglimit]:
		rankingcategories += "\n|-\n| [[:Category:%s]] || %s " % (category, freq)
	rankingredlinks = ""
	redlinks_list = [[freq, redlink] for redlink, freq in redlinks.items()]
	redlinks_list.sort(reverse=True)
	for freq, redlink in redlinks_list[:rankinglimit]:
		rankingredlinks += "\n|-\n| [[%s]] || %s " % (redlink, freq)
	rankingdomains = f"""{{{{static row numbers}}}}{{{{mw-datatable}}}}{{{{table alignment}}}}\n{{| class="wikitable sortable static-row-numbers mw-datatable defaultcenter col1left" style="font-size: 80%;"\n! Domain !! Freq{rankingdomains}\n|}}"""
	rankingdois = f"""{{{{static row numbers}}}}{{{{mw-datatable}}}}{{{{table alignment}}}}\n{{| class="wikitable sortable static-row-numbers mw-datatable defaultcenter col1left" style="font-size: 80%;"\n! DOI !! Freq{rankingdois}\n|}}"""
	rankingisbns = f"""{{{{static row numbers}}}}{{{{mw-datatable}}}}{{{{table alignment}}}}\n{{| class="wikitable sortable static-row-numbers mw-datatable defaultcenter col1left" style="font-size: 80%;"\n! ISBN !! Freq{rankingisbns}\n|}}"""
	rankingtemplates = f"""{{{{static row numbers}}}}{{{{mw-datatable}}}}{{{{table alignment}}}}\n{{| class="wikitable sortable static-row-numbers mw-datatable defaultcenter col1left" style="font-size: 80%;"\n! Template !! Freq{rankingtemplates}\n|}}"""
	rankingcategories = f"""{{{{static row numbers}}}}{{{{mw-datatable}}}}{{{{table alignment}}}}\n{{| class="wikitable sortable static-row-numbers mw-datatable defaultcenter col1left" style="font-size: 80%;"\n! Category !! Freq{rankingcategories}\n|}}"""
	rankingredlinks = f"""{{{{static row numbers}}}}{{{{mw-datatable}}}}{{{{table alignment}}}}\n{{| class="wikitable sortable static-row-numbers mw-datatable defaultcenter col1left" style="font-size: 80%;"\n! Redlink !! Freq{rankingredlinks}\n|}}"""
	rankings = f"""{{| class="plainlinks"\n| valign=top |\n{rankingdomains}\n| valign=top |\n{rankingdois}\n| valign=top |\n{rankingisbns}\n|}}\n{{| class="plainlinks"\n| valign=top |\n{rankingtemplates}\n| valign=top |\n{rankingcategories}\n| valign=top |\n{rankingredlinks}\n|}}"""
	
	#merge sections
	analysis = f"""{intro}
== Summary ==
{summary}
== Analyzed pages ==
Only '''pages''' in the main namespace are shown.
{table}
== Maintenance ==
{maintenance_plain}
== Rankings ==
'''Rankings''' of domains, DOIs, ISBNs, templates, categories and redlinks sorted by frequency (number of occurrences in different pages).
{rankings}
== Visualizations ==
{charts_plain}
== Notes ==
{{{{reflist|3}}}}"""
	print(analysis)
	pageanalysis = pywikibot.Page(sitewp, "User:Emijrpbot/WikiProject %s" % (wikiproject))
	pageanalysis.text = analysis
	pageanalysis.save("BOT - Updating analysis of [[Wikipedia:WikiProject %s]]" % (wikiproject))

if __name__ == '__main__':
	main()
