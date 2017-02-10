#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
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

import os
import re
import sys
import urllib.parse

import pwb
import pywikibot
from wikidatafun import *

def main():
    #isScriptAlive(__file__) #using jstart continuous grid job
    #https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Grid#Submitting_continuous_jobs_.28such_as_bots.29_with_.27jstart.27
    #jstart -N humandesc -mem 1G /usr/bin/python3 /data/project/.../human.descriptions.py
    
    targetlangs = ['es', 'ca', 'gl']
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    genders = {
        'Q6581097': 'male', 
        'Q6581072': 'female', 
    }
    
    #ca: https://ca.wikipedia.org/wiki/Llista_de_gentilicis#Llista_de_gentilicis_per_estat
    #en: https://en.wikipedia.org/wiki/List_of_adjectival_and_demonymic_forms_for_countries_and_nations
    #es: https://es.wikipedia.org/wiki/Anexo:Gentilicios
    #gl: https://web.archive.org/web/20060512203621/http://www.galegoenlinna.uvigo.es/fichasVer.asp?idFicha=132
    translationsNationalities = {
        'Afghan': {
            'ca': { 'male': 'afganès', 'female': 'afganesa' },
            'en': { 'male': 'Afghan', 'female': 'Afghan' }, 
            'es': { 'male': 'afgano', 'female': 'afgana' }, 
            'gl': { 'male': 'afgán', 'female': 'afgá' }, 
        },
        'Albanian': {
            'ca': { 'male': 'albanès', 'female': 'albanesa' },
            'en': { 'male': 'Albanian', 'female': 'Albanian' }, 
            'es': { 'male': 'albanés', 'female': 'albanesa' }, 
            'gl': { 'male': 'albanés', 'female': 'albanesa' }, 
        },
        'Algerian': {
            'ca': { 'male': 'algerià', 'female': 'algeriana' },
            'en': { 'male': 'Algerian', 'female': 'Algerian' }, 
            'es': { 'male': 'argelino', 'female': 'argelina' }, 
            'gl': { 'male': 'alxeriano', 'female': 'alxeriana' }, 
        },
        'American': {
            'ca': { 'male': 'estatunidenc', 'female': 'estatunidenca' }, 
            'en': { 'male': 'American', 'female': 'American' }, 
            'es': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
            'gl': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
        }, 
        'Andorran': {
            'ca': { 'male': 'andorrà', 'female': 'andorrana' },
            'en': { 'male': 'Andorran', 'female': 'Andorran' }, 
            'es': { 'male': 'andorrano', 'female': 'andorrana' }, 
            'gl': { 'male': 'andorrano', 'female': 'andorrana' }, 
        },
        'Angolan': {
            'ca': { 'male': 'angolès', 'female': 'angolesa' },
            'en': { 'male': 'Angolan', 'female': 'Angolan' }, 
            'es': { 'male': 'angoleño', 'female': 'angoleña' }, 
            'gl': { 'male': 'angolano', 'female': 'angolana' }, 
        },
        'Argentine': {
            'ca': { 'male': 'argentí', 'female': 'argentina' },
            'en': { 'male': 'Argentine', 'female': 'Argentine' }, 
            'es': { 'male': 'argentino', 'female': 'argentina' }, 
            'gl': { 'male': 'arxentino', 'female': 'arxentina' }, 
        },
        'Argentinean': {
            'ca': { 'male': 'argentí', 'female': 'argentina' },
            'en': { 'male': 'Argentinean', 'female': 'Argentinean' }, 
            'es': { 'male': 'argentino', 'female': 'argentina' }, 
            'gl': { 'male': 'arxentino', 'female': 'arxentina' }, 
        },
        'Armenian': {
            'ca': { 'male': 'armeni', 'female': 'armènia' },
            'en': { 'male': 'Armenian', 'female': 'Armenian' }, 
            'es': { 'male': 'armenio', 'female': 'armenia' }, 
            'gl': { 'male': 'armenio', 'female': 'armenia' }, 
        },
        'Argentinian': {
            'ca': { 'male': 'argentí', 'female': 'argentina' },
            'en': { 'male': 'Argentinian', 'female': 'Argentinian' }, 
            'es': { 'male': 'argentino', 'female': 'argentina' }, 
            'gl': { 'male': 'arxentino', 'female': 'arxentina' }, 
        },
        'Australian': {
            'ca': { 'male': 'australià', 'female': 'australiana' },
            'en': { 'male': 'Australian', 'female': 'Australian' }, 
            'es': { 'male': 'australiano', 'female': 'australiana' }, 
            'gl': { 'male': 'australiano', 'female': 'australiana' }, 
        },
        'Austrian': {
            'ca': { 'male': 'austríac', 'female': 'austríaca' },
            'en': { 'male': 'Austrian', 'female': 'Austrian' }, 
            'es': { 'male': 'austríaco', 'female': 'austríaca' }, 
            'gl': { 'male': 'austríaco', 'female': 'austríaca' }, 
        },
        'Azerbaijani': {
            'ca': { 'male': 'azerbaidjanès', 'female': 'azerbaidjanesa' },
            'en': { 'male': 'Azerbaijani', 'female': 'Azerbaijani' }, 
            'es': { 'male': 'azerbaiyano', 'female': 'azerbaiyana' }, 
            'gl': { 'male': 'acerbaixano', 'female': 'acerbaixana' }, 
        },
        'Bahamian': {
            'ca': { 'male': 'bahamià', 'female': 'bahamiana' },
            'en': { 'male': 'Bahamian', 'female': 'Bahamian' }, 
            'es': { 'male': 'bahameño', 'female': 'bahameña' }, 
            'gl': { 'male': 'bahameño', 'female': 'bahameña' }, 
        },
        'Bahraini': {
            'ca': { 'male': 'bahrenià', 'female': 'bahreniana' },
            'en': { 'male': 'Bahraini', 'female': 'Bahraini' }, 
            'es': { 'male': 'bareiní', 'female': 'bareiní' }, 
            'gl': { 'male': 'bahrainí', 'female': 'bahrainí' }, 
        },
        'Bangladeshi': {
            'ca': { 'male': 'bangladeshià', 'female': 'bangladeshiana' },
            'en': { 'male': 'Bangladeshi', 'female': 'Bangladeshi' }, 
            'es': { 'male': 'bangladesí', 'female': 'bangladesí' }, 
            'gl': { 'male': 'bangladesí', 'female': 'bangladesí' }, 
        },
        'Barbadian': {
            'ca': { 'male': 'barbadià', 'female': 'barbadiana' },
            'en': { 'male': 'Barbadian', 'female': 'Barbadian' }, 
            'es': { 'male': 'barbadense', 'female': 'barbadense' }, 
            'gl': { 'male': 'barbadense', 'female': 'barbadense' }, 
        },
        'Belarusian': {
            'ca': { 'male': 'bielorús', 'female': 'bielorussa' },
            'en': { 'male': 'Belarusian', 'female': 'Belarusian' }, 
            'es': { 'male': 'bielorruso', 'female': 'bielorrusa' }, 
            'gl': { 'male': 'bielorruso', 'female': 'bielorrusa' }, 
        },
        'Belgian': {
            'ca': { 'male': 'belga', 'female': 'belga' },
            'en': { 'male': 'Belgian', 'female': 'Belgian' }, 
            'es': { 'male': 'belga', 'female': 'belga' }, 
            'gl': { 'male': 'belga', 'female': 'belga' }, 
        },
        'Belizean': {
            'ca': { 'male': 'belizià', 'female': 'beliziana' },
            'en': { 'male': 'Belizean', 'female': 'Belizean' }, 
            'es': { 'male': 'beliceño', 'female': 'beliceña' }, 
            'gl': { 'male': 'belizense', 'female': 'belizense' }, 
        },
        'Beninese': {
            'ca': { 'male': 'beninès', 'female': 'beninesa' },
            'en': { 'male': 'Beninese', 'female': 'Beninese' }, 
            'es': { 'male': 'beninés', 'female': 'beninesa' }, 
            'gl': { 'male': 'beninés', 'female': 'beninesa' }, 
        },
        'Beninois': {
            'ca': { 'male': 'beninès', 'female': 'beninesa' },
            'en': { 'male': 'Beninois', 'female': 'Beninois' }, 
            'es': { 'male': 'beninés', 'female': 'beninesa' }, 
            'gl': { 'male': 'beninés', 'female': 'beninesa' }, 
        },
        'Bermudan': {
            'ca': { 'male': 'de Bermudes', 'female': 'de Bermudes' },
            'en': { 'male': 'Bermudan', 'female': 'Bermudan' }, 
            'es': { 'male': 'bermudeño', 'female': 'bermudeño' }, 
            'gl': { 'male': 'bermudano', 'female': 'bermudana' }, 
        },
        'Bermudian': {
            'ca': { 'male': 'de Bermudes', 'female': 'de Bermudes' },
            'en': { 'male': 'Bermudan', 'female': 'Bermudan' }, 
            'es': { 'male': 'bermudeño', 'female': 'bermudeño' }, 
            'gl': { 'male': 'bermudano', 'female': 'bermudana' }, 
        },
        'Bhutanese': {
            'ca': { 'male': 'bhutanès', 'female': 'bhutanesa' },
            'en': { 'male': 'Bhutanese', 'female': 'Bhutanese' }, 
            'es': { 'male': 'butanés', 'female': 'butanesa' }, 
            'gl': { 'male': 'butanés', 'female': 'butanesa' }, 
        },
        'Bissau-Guinean': {
            'ca': { 'male': 'guineà', 'female': 'guineana' },
            'en': { 'male': 'Bissau-Guinean', 'female': 'Bissau-Guinean' }, 
            'es': { 'male': 'guineano', 'female': 'guineana' }, 
            'gl': { 'male': 'guineano', 'female': 'guineana' }, 
        },
        'Bolivian': {
            'ca': { 'male': 'bolivià', 'female': 'boliviana' },
            'en': { 'male': 'Bolivian', 'female': 'Bolivian' }, 
            'es': { 'male': 'boliviano', 'female': 'boliviana' }, 
            'gl': { 'male': 'boliviano', 'female': 'boliviana' }, 
        },
        'Bosnian': {
            'ca': { 'male': 'bosnià', 'female': 'bosniana' },
            'en': { 'male': 'Bosnian', 'female': 'Bosnian' }, 
            'es': { 'male': 'bosnio', 'female': 'bosnia' }, 
            'gl': { 'male': 'bosníaco', 'female': 'bosníaca' }, 
        },
        'Botswanan': {
            'ca': { 'male': 'botswanès', 'female': 'botswanesa' },
            'en': { 'male': 'Botswanan', 'female': 'Botswanan' }, 
            'es': { 'male': 'botsuano', 'female': 'botsuana' }, 
            'gl': { 'male': 'botswaniano', 'female': 'botswaniana' }, 
        },
        'Brazilian': {
            'ca': { 'male': 'brasiler', 'female': 'brasilera' },
            'en': { 'male': 'Brazilian', 'female': 'Brazilian' }, 
            'es': { 'male': 'brasileño', 'female': 'brasileña' }, 
            'gl': { 'male': 'brasileiro', 'female': 'brasileira' }, 
        },
        'British': {
            'ca': { 'male': 'britànic', 'female': 'britànica' },
            'en': { 'male': 'British', 'female': 'British' }, 
            'es': { 'male': 'británico', 'female': 'británica' }, 
            'gl': { 'male': 'británico', 'female': 'británica' }, 
        },
        'Bruneian': {
            'ca': { 'male': 'bruneiès', 'female': 'bruneiesa' },
            'en': { 'male': 'Bruneian', 'female': 'Bruneian' }, 
            'es': { 'male': 'bruneano', 'female': 'bruneana' }, 
            'gl': { 'male': 'bruneano', 'female': 'bruneana' }, 
        },
        'Bulgarian': {
            'ca': { 'male': 'búlgar', 'female': 'búlgara' },
            'en': { 'male': 'Bulgarian', 'female': 'Bulgarian' }, 
            'es': { 'male': 'búlgaro', 'female': 'búlgara' }, 
            'gl': { 'male': 'búlgaro', 'female': 'búlgara' }, 
        },
        'Burkinabe': {
            'ca': { 'male': 'burkinès', 'female': 'burkinesa' },
            'en': { 'male': 'Burkinabe', 'female': 'Burkinabe' }, 
            'es': { 'male': 'burkinés', 'female': 'burkinesa' }, 
            'gl': { 'male': 'burkinense', 'female': 'burkinense' }, 
        },
        'Burkinabé': {
            'ca': { 'male': 'burkinès', 'female': 'burkinesa' },
            'en': { 'male': 'Burkinabé', 'female': 'Burkinabé' }, 
            'es': { 'male': 'burkinés', 'female': 'burkinesa' }, 
            'gl': { 'male': 'burkinense', 'female': 'burkinense' }, 
        },
        'Burmese': {
            'ca': { 'male': 'birmà', 'female': 'birmana' },
            'en': { 'male': 'Burmese', 'female': 'Burmese' }, 
            'es': { 'male': 'birmano', 'female': 'birmana' }, 
            'gl': { 'male': 'birmano', 'female': 'birmana' }, 
        },
        'Burundian': {
            'ca': { 'male': 'burundès', 'female': 'burundesa' },
            'en': { 'male': 'Burundian', 'female': 'Burundian' }, 
            'es': { 'male': 'burundés', 'female': 'burundesa' }, 
            'gl': { 'male': 'burundiano', 'female': 'burundiana' }, 
        },
        'Cabo Verdean': {
            'ca': { 'male': 'capverdià', 'female': 'capverdiana' },
            'en': { 'male': 'Cabo Verdean', 'female': 'Cabo Verdean' }, 
            'es': { 'male': 'caboverdiano', 'female': 'caboverdiana' }, 
            'gl': { 'male': 'caboverdiano', 'female': 'caboverdiana' }, 
        },
        'Cambodian': {
            'ca': { 'male': 'cambodjà', 'female': 'cambodjana' },
            'en': { 'male': 'Cambodian', 'female': 'Cambodian' }, 
            'es': { 'male': 'camboyano', 'female': 'camboyana' }, 
            'gl': { 'male': 'camboxano', 'female': 'camboxana' }, 
        },
        'Cameroonian': {
            'ca': { 'male': 'camerunès', 'female': 'camerunesa' },
            'en': { 'male': 'Cameroonian', 'female': 'Cameroonian' }, 
            'es': { 'male': 'camerunés', 'female': 'camerunesa' }, 
            'gl': { 'male': 'camerunés', 'female': 'camerunesa' }, 
        },
        'Canadian': {
            'ca': { 'male': 'canadenc', 'female': 'canadenca' },
            'en': { 'male': 'Canadian', 'female': 'Canadian' }, 
            'es': { 'male': 'canadiense', 'female': 'canadiense' }, 
            'gl': { 'male': 'canadense', 'female': 'canadense' }, 
        },
        'Chadian': {
            'ca': { 'male': 'txadià', 'female': 'txadiana' },
            'en': { 'male': 'Chadian', 'female': 'Chadian' }, 
            'es': { 'male': 'chadiano', 'female': 'chadiana' }, 
            'gl': { 'male': 'chadiano', 'female': 'chadiana' }, 
        },
        'Chilean': {
            'ca': { 'male': 'xilè', 'female': 'xilena' },
            'en': { 'male': 'Chilean', 'female': 'Chilean' }, 
            'es': { 'male': 'chileno', 'female': 'chilena' }, 
            'gl': { 'male': 'chileno', 'female': 'chilena' }, 
        },
        'Chinese': {
            'ca': { 'male': 'xinès', 'female': 'xinesa' },
            'en': { 'male': 'Chinese', 'female': 'Chinese' }, 
            'es': { 'male': 'chino', 'female': 'china' }, 
            'gl': { 'male': 'chinés', 'female': 'chinesa' }, 
        },
        'Colombian': {
            'ca': { 'male': 'colombià', 'female': 'colombiana' },
            'en': { 'male': 'Colombian', 'female': 'Colombian' }, 
            'es': { 'male': 'colombiano', 'female': 'colombiana' }, 
            'gl': { 'male': 'colombiano', 'female': 'colombiana' }, 
        },
        'Comoran': {
            'ca': { 'male': 'comorià', 'female': 'comoriana' },
            'en': { 'male': 'Comoran', 'female': 'Comoran' }, 
            'es': { 'male': 'comorense', 'female': 'comorense' }, 
            'gl': { 'male': 'comoriano', 'female': 'comoriana' }, 
        },
        'Comorian': {
            'ca': { 'male': 'comorià', 'female': 'comoriana' },
            'en': { 'male': 'Comorian', 'female': 'Comorian' }, 
            'es': { 'male': 'comorense', 'female': 'comorense' }, 
            'gl': { 'male': 'comoriano', 'female': 'comoriana' }, 
        },
        'Congolese': {
            'ca': { 'male': 'congolès', 'female': 'congolesa' },
            'en': { 'male': 'Congolese', 'female': 'Congolese' }, 
            'es': { 'male': 'congoleño', 'female': 'congoleña' }, 
            'gl': { 'male': 'congolés', 'female': 'congolesa' }, 
        },
        'Costa Rican': {
            'ca': { 'male': 'costa-riqueny', 'female': 'costa-riquenya' },
            'en': { 'male': 'Costa Rican', 'female': 'Costa Rican' }, 
            'es': { 'male': 'costarricense', 'female': 'costarricense' }, 
            'gl': { 'male': 'costarriqueño', 'female': 'costarriqueña' }, 
        },
        'Croatian': {
            'ca': { 'male': 'croat', 'female': 'croata' },
            'en': { 'male': 'Croatian', 'female': 'Croatian' }, 
            'es': { 'male': 'croata', 'female': 'croata' }, 
            'gl': { 'male': 'croata', 'female': 'croata' }, 
        },
        'Cuban': {
            'ca': { 'male': 'cubà', 'female': 'cubana' },
            'en': { 'male': 'Cuban', 'female': 'Cuban' }, 
            'es': { 'male': 'cubano', 'female': 'cubana' }, 
            'gl': { 'male': 'cubano', 'female': 'cubana' }, 
        },
        'Cypriot': {
            'ca': { 'male': 'xipriota', 'female': 'xipriota' },
            'en': { 'male': 'Cypriot', 'female': 'Cypriot' }, 
            'es': { 'male': 'chipriota', 'female': 'chipriota' }, 
            'gl': { 'male': 'chipriota', 'female': 'chipriota' }, 
        },
        'Czech': {
            'ca': { 'male': 'txec', 'female': 'txeca' },
            'en': { 'male': 'Czech', 'female': 'Czech' }, 
            'es': { 'male': 'checo', 'female': 'checa' }, 
            'gl': { 'male': 'checo', 'female': 'checa' }, 
        },
        'Danish': {
            'ca': { 'male': 'danès', 'female': 'danesa' },
            'en': { 'male': 'Danish', 'female': 'Danish' }, 
            'es': { 'male': 'danés', 'female': 'danesa' }, 
            'gl': { 'male': 'danés', 'female': 'danesa' }, 
        },
        'Djiboutian': {
            'ca': { 'male': 'djiboutià', 'female': 'djiboutiana' },
            'en': { 'male': 'Djiboutian', 'female': 'Djiboutian' }, 
            'es': { 'male': 'yibutiano', 'female': 'yibutiana' }, 
            'gl': { 'male': 'xibutiano', 'female': 'xibutiana' }, 
        },
        'Dutch': {
            'ca': { 'male': 'neerlandès', 'female': 'neerlandesa' },
            'en': { 'male': 'Dutch', 'female': 'Dutch' }, 
            'es': { 'male': 'neerlandés', 'female': 'neerlandesa' }, 
            'gl': { 'male': 'neerlandés', 'female': 'neerlandesa' }, 
        },
        'Ecuadorian': {
            'ca': { 'male': 'equatorià', 'female': 'equatoriana' },
            'en': { 'male': 'Ecuadorian', 'female': 'Ecuadorian' }, 
            'es': { 'male': 'ecuatoriano', 'female': 'ecuatoriana' }, 
            'gl': { 'male': 'ecuatoriano', 'female': 'ecuatoriana' }, 
        },
        'Egyptian': {
            'ca': { 'male': 'egipci', 'female': 'egípcia' },
            'en': { 'male': 'Egyptian', 'female': 'Egyptian' }, 
            'es': { 'male': 'egipcio', 'female': 'egipcia' }, 
            'gl': { 'male': 'exipcio', 'female': 'exipcia' }, 
        },
        'Emirati': {
            'ca': { 'male': 'dels Emirats Àrabs Units', 'female': 'dels Emirats Àrabs Units' },
            'en': { 'male': 'Emirati', 'female': 'Emirati' }, 
            'es': { 'male': 'emiratí', 'female': 'emiratí' }, 
            'gl': { 'male': 'emiratí', 'female': 'emiratí' }, 
        },
        'Emiri': {
            'ca': { 'male': 'dels Emirats Àrabs Units', 'female': 'dels Emirats Àrabs Units' },
            'en': { 'male': 'Emiri', 'female': 'Emiri' }, 
            'es': { 'male': 'emiratí', 'female': 'emiratí' }, 
            'gl': { 'male': 'emiratí', 'female': 'emiratí' }, 
        },
        'Emirian': {
            'ca': { 'male': 'dels Emirats Àrabs Units', 'female': 'dels Emirats Àrabs Units' },
            'en': { 'male': 'Emirian', 'female': 'Emirian' }, 
            'es': { 'male': 'emiratí', 'female': 'emiratí' }, 
            'gl': { 'male': 'emiratí', 'female': 'emiratí' }, 
        },
        'Equatoguinean': {
            'ca': { 'male': 'equatoguineà', 'female': 'equatoguineana' },
            'en': { 'male': 'Equatoguinean', 'female': 'Equatoguinean' }, 
            'es': { 'male': 'ecuatoguineano', 'female': 'ecuatoguineana' }, 
            'gl': { 'male': 'ecuatoguineano', 'female': 'ecuatoguineana' }, 
        },
        'Equatorial Guinean': {
            'ca': { 'male': 'equatoguineà', 'female': 'equatoguineana' },
            'en': { 'male': 'Equatorial Guinean', 'female': 'Equatorial Guinean' }, 
            'es': { 'male': 'ecuatoguineano', 'female': 'ecuatoguineana' }, 
            'gl': { 'male': 'ecuatoguineano', 'female': 'ecuatoguineana' }, 
        },
        'Eritrean': {
            'ca': { 'male': 'eritreu', 'female': 'eritrea' },
            'en': { 'male': 'Eritrean', 'female': 'Eritrean' }, 
            'es': { 'male': 'eritreo', 'female': 'eritrea' }, 
            'gl': { 'male': 'eritreo', 'female': 'eritrea' }, 
        },
        'Estonian': {
            'ca': { 'male': 'estonià', 'female': 'estoniana' },
            'en': { 'male': 'Estonian', 'female': 'Estonian' }, 
            'es': { 'male': 'estonio', 'female': 'estonia' }, 
            'gl': { 'male': 'estoniano', 'female': 'estoniana' }, 
        },
        'Ethiopian': {
            'ca': { 'male': 'etiòpic', 'female': 'etiòpica' },
            'en': { 'male': 'Ethiopian', 'female': 'Ethiopian' }, 
            'es': { 'male': 'etíope', 'female': 'etíope' }, 
            'gl': { 'male': 'etíope', 'female': 'etíope' }, 
        },
        'Fijian': {
            'ca': { 'male': 'fijià', 'female': 'fijiana' },
            'en': { 'male': 'Fijian', 'female': 'Fijian' }, 
            'es': { 'male': 'fiyiano', 'female': 'fiyiana' }, 
            'gl': { 'male': 'fidxiano', 'female': 'fidxiana' }, 
        },
        'Filipino': {
            'ca': { 'male': 'filipí', 'female': 'filipina' },
            'en': { 'male': 'Filipino', 'female': 'Filipino' }, 
            'es': { 'male': 'filipino', 'female': 'filipina' }, 
            'gl': { 'male': 'filipino', 'female': 'filipina' }, 
        },
        'Finnish': {
            'ca': { 'male': 'finlandès', 'female': 'finlandesa' },
            'en': { 'male': 'Finnish', 'female': 'Finnish' }, 
            'es': { 'male': 'finlandés', 'female': 'finlandesa' }, 
            'gl': { 'male': 'finlandés', 'female': 'finlandesa' }, 
        },
        'French': {
            'ca': { 'male': 'francès', 'female': 'francesa' },
            'en': { 'male': 'French', 'female': 'French' }, 
            'es': { 'male': 'francés', 'female': 'francesa' }, 
            'gl': { 'male': 'francés', 'female': 'francesa' }, 
        },
        'Gabonese': {
            'ca': { 'male': 'gabonès', 'female': 'gabonesa' },
            'en': { 'male': 'Gabonese', 'female': 'Gabonese' }, 
            'es': { 'male': 'gabonés', 'female': 'gabonesa' }, 
            'gl': { 'male': 'gabonés', 'female': 'gabonesa' }, 
        },
        'Gambian': {
            'ca': { 'male': 'gambià', 'female': 'gambiana' },
            'en': { 'male': 'Gambian', 'female': 'Gambian' }, 
            'es': { 'male': 'gambiano', 'female': 'gambiana' }, 
            'gl': { 'male': 'gambiano', 'female': 'gambiana' }, 
        },
        'Georgian': {
            'ca': { 'male': 'georgià', 'female': 'georgiana' },
            'en': { 'male': 'Georgian', 'female': 'Georgian' }, 
            'es': { 'male': 'georgiano', 'female': 'georgiana' }, 
            'gl': { 'male': 'xeorxiano', 'female': 'xeorxiana' }, 
        },
        'German': {
            'ca': { 'male': 'alemany', 'female': 'alemanya' },
            'en': { 'male': 'German', 'female': 'German' }, 
            'es': { 'male': 'alemán', 'female': 'alemana' }, 
            'gl': { 'male': 'alemán', 'female': 'alemá' }, 
        },
        'Ghanaian': {
            'ca': { 'male': 'ghanès', 'female': 'ghanesa' },
            'en': { 'male': 'Ghanaian', 'female': 'Ghanaian' }, 
            'es': { 'male': 'ghanés', 'female': 'ghanesa' }, 
            'gl': { 'male': 'ghanés', 'female': 'ghanesa' }, 
        },
        'Greek': {
            'ca': { 'male': 'grec', 'female': 'grega' },
            'en': { 'male': 'Greek', 'female': 'Greek' }, 
            'es': { 'male': 'griego', 'female': 'griega' }, 
            'gl': { 'male': 'grego', 'female': 'grega' }, 
        },
        'Greenlandic': {
            'ca': { 'male': 'groenlandès', 'female': 'groenlandesa' },
            'en': { 'male': 'Greenlandic', 'female': 'Greenlandic' }, 
            'es': { 'male': 'groenlandés', 'female': 'groenlandesa' }, 
            'gl': { 'male': 'groenlandés', 'female': 'groenlandesa' }, 
        },
        'Grenadian': {
            'ca': { 'male': 'grenadí', 'female': 'grenadina' },
            'en': { 'male': 'Grenadian', 'female': 'Grenadian' }, 
            'es': { 'male': 'granadino', 'female': 'granadina' }, 
            'gl': { 'male': 'granadino', 'female': 'granadina' }, 
        },
        'Guatemalan': {
            'ca': { 'male': 'guatemalenc', 'female': 'guatemalenca' },
            'en': { 'male': 'Guatemalan', 'female': 'Guatemalan' }, 
            'es': { 'male': 'guatemalteco', 'female': 'guatemalteca' }, 
            'gl': { 'male': 'guatemalteco', 'female': 'guatemalteca' }, 
        },
        'Guinean': {
            'ca': { 'male': 'guineà', 'female': 'guineana' },
            'en': { 'male': 'Guinean', 'female': 'Guinean' }, 
            'es': { 'male': 'guineano', 'female': 'guineana' }, 
            'gl': { 'male': 'guineano', 'female': 'guineana' }, 
        },
        'Guyanese': {
            'ca': { 'male': 'guyanès', 'female': 'guyanesa' },
            'en': { 'male': 'Guyanese', 'female': 'Guyanese' }, 
            'es': { 'male': 'guyanés', 'female': 'guyanesa' }, 
            'gl': { 'male': 'güianés', 'female': 'güianesa' }, 
        },
        'Haitian': {
            'ca': { 'male': 'haitià', 'female': 'haitiana' },
            'en': { 'male': 'Haitian', 'female': 'Haitian' }, 
            'es': { 'male': 'haitiano', 'female': 'haitiana' }, 
            'gl': { 'male': 'haitiano', 'female': 'haitiana' }, 
        },
        'Herzegovinian': {
            'ca': { 'male': 'hercegoví', 'female': 'hercegovina' },
            'en': { 'male': 'Herzegovinian', 'female': 'Herzegovinian' }, 
            'es': { 'male': 'herzegovino', 'female': 'herzegovina' }, 
            'gl': { 'male': 'hercegovino', 'female': 'hercegovina' }, 
        },
        'Honduran': {
            'ca': { 'male': 'hondureny', 'female': 'hondurenya' },
            'en': { 'male': 'Honduran', 'female': 'Honduran' }, 
            'es': { 'male': 'hondureño', 'female': 'hondureña' }, 
            'gl': { 'male': 'hondureño', 'female': 'hondureña' }, 
        },
        'Hungarian': {
            'ca': { 'male': 'hongarès', 'female': 'hongaresa' },
            'en': { 'male': 'Hungarian', 'female': 'Hungarian' }, 
            'es': { 'male': 'húngaro', 'female': 'húngara' }, 
            'gl': { 'male': 'húngaro', 'female': 'húngara' }, 
        },
        'Icelandic': {
            'ca': { 'male': 'islandès', 'female': 'islandesa' },
            'en': { 'male': 'Icelandic', 'female': 'Icelandic' }, 
            'es': { 'male': 'islandés', 'female': 'islandesa' }, 
            'gl': { 'male': 'islandés', 'female': 'islandesa' }, 
        },
        'I-Kiribati': {
            'ca': { 'male': 'kiribatià', 'female': 'kiribatiana' }, 
            'en': { 'male': 'I-Kiribati', 'female': 'I-Kiribati' }, 
            'es': { 'male': 'kiribatiano', 'female': 'kiribatiana' }, 
            'gl': { 'male': 'kiribatiano', 'female': 'kiribatiana' }, 
        }, 
        'Indian': {
            'ca': { 'male': 'indi', 'female': 'índia' },
            'en': { 'male': 'Indian', 'female': 'Indian' }, 
            'es': { 'male': 'indio', 'female': 'india' }, 
            'gl': { 'male': 'indio', 'female': 'india' }, 
        },
        'Indonesian': {
            'ca': { 'male': 'indonesi', 'female': 'indonèsia' },
            'en': { 'male': 'Indonesian', 'female': 'Indonesian' }, 
            'es': { 'male': 'indonesio', 'female': 'indonesia' }, 
            'gl': { 'male': 'indonesio', 'female': 'indonesia' }, 
        },
        'Iranian': {
            'ca': { 'male': 'iranià', 'female': 'iraniana' },
            'en': { 'male': 'Iranian', 'female': 'Iranian' }, 
            'es': { 'male': 'iraní', 'female': 'iraní' }, 
            'gl': { 'male': 'iraniano', 'female': 'iraniana' }, 
        },
        'Iraqi': {
            'ca': { 'male': 'iraquià', 'female': 'iraquiana' },
            'en': { 'male': 'Iraqi', 'female': 'Iraqi' }, 
            'es': { 'male': 'iraquí', 'female': 'iraquí' }, 
            'gl': { 'male': 'iraquí', 'female': 'iraquí' }, 
        },
        'Irish': {
            'ca': { 'male': 'irlandès', 'female': 'irlandesa' },
            'en': { 'male': 'Irish', 'female': 'Irish' }, 
            'es': { 'male': 'irlandés', 'female': 'irlandesa' }, 
            'gl': { 'male': 'irlandés', 'female': 'irlandesa' }, 
        },
        'Israeli': {
            'ca': { 'male': 'israelià', 'female': 'israeliana' },
            'en': { 'male': 'Israeli', 'female': 'Israeli' }, 
            'es': { 'male': 'israelí', 'female': 'israelí' }, 
            'gl': { 'male': 'israelí', 'female': 'israelí' }, 
        },
        'Italian': {
            'ca': { 'male': 'italià', 'female': 'italiana' }, 
            'en': { 'male': 'Italian', 'female': 'Italian' }, 
            'es': { 'male': 'italiano', 'female': 'italiana' }, 
            'gl': { 'male': 'italiano', 'female': 'italiana' }, 
        }, 
        'Ivorian': {
            'ca': { 'male': 'ivorià', 'female': 'ivoriana' }, 
            'en': { 'male': 'Ivorian', 'female': 'Ivorian' }, 
            'es': { 'male': 'marfileño', 'female': 'marfileña' }, 
            'gl': { 'male': 'marfilés', 'female': 'marfilesa' }, 
        }, 
        'Jamaican': {
            'ca': { 'male': 'jamaicà', 'female': 'jamaicana' }, 
            'en': { 'male': 'Jamaican', 'female': 'Jamaican' }, 
            'es': { 'male': 'jamaicano', 'female': 'jamaicana' }, 
            'gl': { 'male': 'xamaicano', 'female': 'xamaicana' }, 
        }, 
        'Japanese': {
            'ca': { 'male': 'japonès', 'female': 'japonesa' }, 
            'en': { 'male': 'Japanese', 'female': 'Japanese' }, 
            'es': { 'male': 'japonés', 'female': 'japonesa' }, 
            'gl': { 'male': 'xaponés', 'female': 'xaponesa' }, 
        }, 
        'Jordanian': {
            'ca': { 'male': 'jordà', 'female': 'jordana' }, 
            'en': { 'male': 'Jordanian', 'female': 'Jordanian' }, 
            'es': { 'male': 'jordano', 'female': 'jordana' }, 
            'gl': { 'male': 'xordano', 'female': 'xordana' }, 
        }, 
        'Kazakh': {
            'ca': { 'male': 'kazakh', 'female': 'kazakh' }, 
            'en': { 'male': 'Kazakh', 'female': 'Kazakh' }, 
            'es': { 'male': 'kazajo', 'female': 'kazaja' }, 
            'gl': { 'male': 'casaco', 'female': 'casaca' }, 
        }, 
        'Kazakhstani': {
            'ca': { 'male': 'kazakh', 'female': 'kazakh' }, 
            'en': { 'male': 'Kazakhstani', 'female': 'Kazakhstani' }, 
            'es': { 'male': 'kazajo', 'female': 'kazaja' }, 
            'gl': { 'male': 'casaco', 'female': 'casaca' }, 
        }, 
        'Kenyan': {
            'ca': { 'male': 'kenyà', 'female': 'kenyana' }, 
            'en': { 'male': 'Kenyan', 'female': 'Kenyan' }, 
            'es': { 'male': 'keniata', 'female': 'keniata' }, 
            'gl': { 'male': 'kenyano', 'female': 'kenyana' }, 
        }, 
        'Kirghiz': {
            'ca': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'en': { 'male': 'Kirghiz', 'female': 'Kirghiz' }, 
            'es': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'gl': { 'male': 'kirguiz', 'female': 'kirguiz' }, 
        }, 
        'Kirgiz': {
            'ca': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'en': { 'male': 'Kirgiz', 'female': 'Kirgiz' }, 
            'es': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'gl': { 'male': 'kirguiz', 'female': 'kirguiz' }, 
        }, 
        'Kiribati': {
            'ca': { 'male': 'kiribatià', 'female': 'kiribatiana' }, 
            'en': { 'male': 'Kiribati', 'female': 'Kiribati' }, 
            'es': { 'male': 'kiribatiano', 'female': 'kiribatiana' }, 
            'gl': { 'male': 'kiribatiano', 'female': 'kiribatiana' }, 
        }, 
        'Kosovan': {
            'ca': { 'male': 'kosovar', 'female': 'kosovar' }, 
            'en': { 'male': 'Kosovan', 'female': 'Kosovan' }, 
            'es': { 'male': 'kosovar', 'female': 'kosovar' }, 
            'gl': { 'male': 'kosovar', 'female': 'kosovar' }, 
        }, 
        'Kosovar': {
            'ca': { 'male': 'kosovar', 'female': 'kosovar' }, 
            'en': { 'male': 'Kosovar', 'female': 'Kosovar' }, 
            'es': { 'male': 'kosovar', 'female': 'kosovar' }, 
            'gl': { 'male': 'kosovar', 'female': 'kosovar' }, 
        }, 
        'Kuwaiti': {
            'ca': { 'male': 'kuwaitià', 'female': 'kuwaitiana' }, 
            'en': { 'male': 'Kuwaiti', 'female': 'Kuwaiti' }, 
            'es': { 'male': 'kuwaití', 'female': 'kuwaití' }, 
            'gl': { 'male': 'kuwaití', 'female': 'kuwaití' }, 
        }, 
        'Kyrgyz': {
            'ca': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'en': { 'male': 'Kyrgyz', 'female': 'Kyrgyz' }, 
            'es': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'gl': { 'male': 'kirguiz', 'female': 'kirguiz' }, 
        }, 
        'Kyrgyzstani': {
            'ca': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'en': { 'male': 'Kyrgyzstani', 'female': 'Kyrgyzstani' }, 
            'es': { 'male': 'kirguís', 'female': 'kirguís' }, 
            'gl': { 'male': 'kirguiz', 'female': 'kirguiz' }, 
        }, 
        'Lao': {
            'ca': { 'male': 'laosià', 'female': 'laosiana' }, 
            'en': { 'male': 'Lao', 'female': 'Lao' }, 
            'es': { 'male': 'laosiano', 'female': 'laosiana' }, 
            'gl': { 'male': 'laosiano', 'female': 'laosiana' }, 
        }, 
        'Laotian': {
            'ca': { 'male': 'laosià', 'female': 'laosiana' }, 
            'en': { 'male': 'Laotian', 'female': 'Laotian' }, 
            'es': { 'male': 'laosiano', 'female': 'laosiana' }, 
            'gl': { 'male': 'laosiano', 'female': 'laosiana' }, 
        }, 
        'Latvian': {
            'ca': { 'male': 'letó', 'female': 'letona' }, 
            'en': { 'male': 'Latvian', 'female': 'Latvian' }, 
            'es': { 'male': 'letón', 'female': 'letona' }, 
            'gl': { 'male': 'letón', 'female': 'letoa' }, 
        }, 
        'Lebanese': {
            'ca': { 'male': 'libanès', 'female': 'libanesa' }, 
            'en': { 'male': 'Lebanese', 'female': 'Lebanese' }, 
            'es': { 'male': 'libanés', 'female': 'libanesa' }, 
            'gl': { 'male': 'libanés', 'female': 'libanesa' }, 
        }, 
        'Liberian': {
            'ca': { 'male': 'liberià', 'female': 'liberiana' }, 
            'en': { 'male': 'Liberian', 'female': 'Liberian' }, 
            'es': { 'male': 'liberiano', 'female': 'liberiana' }, 
            'gl': { 'male': 'liberiano', 'female': 'liberiana' }, 
        }, 
        'Libyan': {
            'ca': { 'male': 'libi', 'female': 'líbia' }, 
            'en': { 'male': 'Libyan', 'female': 'Libyan' }, 
            'es': { 'male': 'libio', 'female': 'libia' }, 
            'gl': { 'male': 'libio', 'female': 'libia' }, 
        }, 
        'Liechtensteiner': {
            'ca': { 'male': 'liechtensteinès', 'female': 'liechtensteinesa' }, 
            'en': { 'male': 'Liechtensteiner', 'female': 'Liechtensteiner' }, 
            'es': { 'male': 'liechtensteiniano', 'female': 'liechtensteiniana' }, 
            'gl': { 'male': 'de Liechtenstein', 'female': 'de Liechtenstein' }, 
        }, 
        'Lithuanian': {
            'ca': { 'male': 'lituà', 'female': 'lituana' }, 
            'en': { 'male': 'Lithuanian', 'female': 'Lithuanian' }, 
            'es': { 'male': 'lituano', 'female': 'lituana' }, 
            'gl': { 'male': 'lituano', 'female': 'lituana' }, 
        }, 
        'Luxembourg': {
            'ca': { 'male': 'luxemburguès', 'female': 'luxemburguesa' }, 
            'en': { 'male': 'Luxembourg', 'female': 'Luxembourg' }, 
            'es': { 'male': 'luxemburgués', 'female': 'luxemburguesa' }, 
            'gl': { 'male': 'luxemburgués', 'female': 'luxemburguesa' }, 
        }, 
        'Luxembourgish': {
            'ca': { 'male': 'luxemburguès', 'female': 'luxemburguesa' }, 
            'en': { 'male': 'Luxembourgish', 'female': 'Luxembourgish' }, 
            'es': { 'male': 'luxemburgués', 'female': 'luxemburguesa' }, 
            'gl': { 'male': 'luxemburgués', 'female': 'luxemburguesa' }, 
        }, 
        'Macanese': {
            'ca': { 'male': 'de Macau', 'female': 'de Macau' }, 
            'en': { 'male': 'Macanese', 'female': 'Macanese' }, 
            'es': { 'male': 'macaense', 'female': 'macaense' }, 
            'gl': { 'male': 'de Macau', 'female': 'de Macau' }, 
        }, 
        'Macedonian': {
            'ca': { 'male': 'macedonià', 'female': 'macedoniana' }, 
            'en': { 'male': 'Macedonian', 'female': 'Macedonian' }, 
            'es': { 'male': 'macedonio', 'female': 'macedonia' }, 
            'gl': { 'male': 'macedonio', 'female': 'macedonia' }, 
        }, 
        'Malagasy': {
            'ca': { 'male': 'malgaix', 'female': 'malgaixa' }, 
            'en': { 'male': 'Malagasy', 'female': 'Malagasy' }, 
            'es': { 'male': 'malgache', 'female': 'malgache' }, 
            'gl': { 'male': 'malgaxe', 'female': 'malgaxe' }, 
        }, 
        'Malawian': {
            'ca': { 'male': 'malawià', 'female': 'malawiana' }, 
            'en': { 'male': 'Malawian', 'female': 'Malawian' }, 
            'es': { 'male': 'malauí', 'female': 'malauí' }, 
            'gl': { 'male': 'de Malawi', 'female': 'de Malawi' }, 
        }, 
        'Malaysian': {
            'ca': { 'male': 'malaisi', 'female': 'malàisia' }, 
            'en': { 'male': 'Malaysian', 'female': 'Malaysian' }, 
            'es': { 'male': 'malasio', 'female': 'malasia' }, 
            'gl': { 'male': 'malaisiano', 'female': 'malaisiana' }, 
        }, 
        'Maldivian': {
            'ca': { 'male': 'maldivià', 'female': 'maldiviana' }, 
            'en': { 'male': 'Maldivian', 'female': 'Maldivian' }, 
            'es': { 'male': 'maldivo', 'female': 'maldiva' }, 
            'gl': { 'male': 'maldivano', 'female': 'maldivana' }, 
        }, 
        'Malian': {
            'ca': { 'male': 'malià', 'female': 'maliana' }, 
            'en': { 'male': 'Malian', 'female': 'Malian' }, 
            'es': { 'male': 'maliense', 'female': 'maliense' }, 
            'gl': { 'male': 'maliano', 'female': 'maliana' }, 
        }, 
        'Maltese': {
            'ca': { 'male': 'maltès', 'female': 'maltesa' }, 
            'en': { 'male': 'Maltese', 'female': 'Maltese' }, 
            'es': { 'male': 'maltés', 'female': 'maltesa' }, 
            'gl': { 'male': 'maltés', 'female': 'maltesa' }, 
        }, 
        'Mauritanian': {
            'ca': { 'male': 'maurità', 'female': 'mauritana' }, 
            'en': { 'male': 'Mauritanian', 'female': 'Mauritanian' }, 
            'es': { 'male': 'mauritano', 'female': 'mauritana' }, 
            'gl': { 'male': 'mauritano', 'female': 'mauritana' }, 
        }, 
        'Mauritian': {
            'ca': { 'male': 'mauricià', 'female': 'mauriciana' }, 
            'en': { 'male': 'Mauritian', 'female': 'Mauritian' }, 
            'es': { 'male': 'mauriciano', 'female': 'mauriciana' }, 
            'gl': { 'male': 'mauriciana', 'female': 'mauriciana' }, 
        }, 
        'Mexican': {
            'ca': { 'male': 'mexicà', 'female': 'mexicana' }, 
            'en': { 'male': 'Mexican', 'female': 'Mexican' }, 
            'es': { 'male': 'mexicano', 'female': 'mexicana' }, 
            'gl': { 'male': 'mexicano', 'female': 'mexicana' }, 
        }, 
        'Moldovan': {
            'ca': { 'male': 'moldau', 'female': 'moldava' }, 
            'en': { 'male': 'Moldovan', 'female': 'Moldovan' }, 
            'es': { 'male': 'moldavo', 'female': 'moldava' }, 
            'gl': { 'male': 'moldavo', 'female': 'moldava' }, 
        }, 
        'Monacan': {
            'ca': { 'male': 'monegasc', 'female': 'monegasca' }, 
            'en': { 'male': 'Monacan', 'female': 'Monacan' }, 
            'es': { 'male': 'monegasco', 'female': 'monegasca' }, 
            'gl': { 'male': 'monegasco', 'female': 'monegasca' }, 
        }, 
        'Monégasque': {
            'ca': { 'male': 'monegasc', 'female': 'monegasca' }, 
            'en': { 'male': 'Monégasque', 'female': 'Monégasque' }, 
            'es': { 'male': 'monegasco', 'female': 'monegasca' }, 
            'gl': { 'male': 'monegasco', 'female': 'monegasca' }, 
        }, 
        'Mongolian': {
            'ca': { 'male': 'mongol', 'female': 'mongola' }, 
            'en': { 'male': 'Mongolian', 'female': 'Mongolian' }, 
            'es': { 'male': 'mongol', 'female': 'mongola' }, 
            'gl': { 'male': 'mongol', 'female': 'mongol' }, 
        }, 
        'Montenegrin': {
            'ca': { 'male': 'montenegrí', 'female': 'montenegrina' }, 
            'en': { 'male': 'Montenegrin', 'female': 'Montenegrin' }, 
            'es': { 'male': 'montenegrino', 'female': 'montenegrina' }, 
            'gl': { 'male': 'montenegrino', 'female': 'montenegrina' }, 
        }, 
        'Moroccan': {
            'ca': { 'male': 'marroquí', 'female': 'marroquina' }, 
            'en': { 'male': 'Moroccan', 'female': 'Moroccan' }, 
            'es': { 'male': 'marroquí', 'female': 'marroquí' }, 
            'gl': { 'male': 'marroquí', 'female': 'marroquí' }, 
        }, 
        'Mosotho': { #Lesotho
            'ca': { 'male': 'basuto', 'female': 'basuto' }, 
            'en': { 'male': 'Mosotho', 'female': 'Mosotho' }, 
            'es': { 'male': 'lesotense', 'female': 'lesotense' }, 
            'gl': { 'male': 'lesotense', 'female': 'lesotense' }, 
        }, 
        'Mozambican': {
            'ca': { 'male': 'moçambiquès', 'female': 'moçambiquesa' }, 
            'en': { 'male': 'Mozambican', 'female': 'Mozambican' }, 
            'es': { 'male': 'mozambiqueño', 'female': 'mozambiqueña' }, 
            'gl': { 'male': 'mozambicano', 'female': 'mozambicana' }, 
        }, 
        'Namibian': {
            'ca': { 'male': 'namibià', 'female': 'namibiana' }, 
            'en': { 'male': 'Namibian', 'female': 'Namibian' }, 
            'es': { 'male': 'namibio', 'female': 'namibia' }, 
            'gl': { 'male': 'namibio', 'female': 'namibia' }, 
        }, 
        'Nauruan': {
            'ca': { 'male': 'nauruà', 'female': 'nauruana' }, 
            'en': { 'male': 'Nauruan', 'female': 'Nauruan' }, 
            'es': { 'male': 'nauruano', 'female': 'nauruana' }, 
            'gl': { 'male': 'nauruano', 'female': 'nauruana' }, 
        }, 
        'Nepalese': {
            'ca': { 'male': 'nepalès', 'female': 'nepalesa' }, 
            'en': { 'male': 'Nepalese', 'female': 'Nepalese' }, 
            'es': { 'male': 'nepalés', 'female': 'nepalesa' }, 
            'gl': { 'male': 'nepalés', 'female': 'nepalesa' }, 
        }, 
        'Nepali': {
            'ca': { 'male': 'nepalès', 'female': 'nepalesa' }, 
            'en': { 'male': 'Nepali', 'female': 'Nepali' }, 
            'es': { 'male': 'nepalés', 'female': 'nepalesa' }, 
            'gl': { 'male': 'nepalés', 'female': 'nepalesa' }, 
        }, 
        'New Zealand': {
            'ca': { 'male': 'neozelandès', 'female': 'neozelandesa' }, 
            'en': { 'male': 'New Zealand', 'female': 'New Zealand' }, 
            'es': { 'male': 'neozelandés', 'female': 'neozelandesa' }, 
            'gl': { 'male': 'neozelandés', 'female': 'neozelandesa' }, 
        }, 
        'Ni-Vanuatu': {
            'ca': { 'male': 'vanuatuenc', 'female': 'vanuatuenca' }, 
            'en': { 'male': 'Ni-Vanuatu', 'female': 'Ni-Vanuatu' }, 
            'es': { 'male': 'vanuatuense', 'female': 'vanuatuense' }, 
            'gl': { 'male': 'vanuatiano', 'female': 'vanuatiana' }, 
        }, 
        'Nicaraguan': {
            'ca': { 'male': 'nicaragüenc', 'female': 'nicaragüenca' }, 
            'en': { 'male': 'Nicaraguan', 'female': 'Nicaraguan' }, 
            'es': { 'male': 'nicaragüense', 'female': 'nicaragüense' }, 
            'gl': { 'male': 'nicaraguano', 'female': 'nicaraguana' }, 
        }, 
        'Nigerian': {
            'ca': { 'male': 'nigerià', 'female': 'nigeriana' }, 
            'en': { 'male': 'Nigerian', 'female': 'Nigerian' }, 
            'es': { 'male': 'nigeriano', 'female': 'nigeriana' }, 
            'gl': { 'male': 'nixeriano', 'female': 'nixeriana' }, 
        }, 
        'Nigerien': {
            'ca': { 'male': 'nigerí', 'female': 'nigerina' }, 
            'en': { 'male': 'Nigerien', 'female': 'Nigerien' }, 
            'es': { 'male': 'nigerino', 'female': 'nigerina' }, 
            'gl': { 'male': 'nixerino', 'female': 'nixerina' }, 
        }, 
        'North Korean': {
            'ca': { 'male': 'nord-coreà', 'female': 'nord-coreana' }, 
            'en': { 'male': 'North Korean', 'female': 'North Korean' }, 
            'es': { 'male': 'norcoreano', 'female': 'norcoreana' }, 
            'gl': { 'male': 'norcoreano', 'female': 'norcoreana' }, 
        }, 
        'Norwegian': {
            'ca': { 'male': 'noruec', 'female': 'noruega' }, 
            'en': { 'male': 'Norwegian', 'female': 'Norwegian' }, 
            'es': { 'male': 'noruego', 'female': 'noruega' }, 
            'gl': { 'male': 'noruegués', 'female': 'norueguesa' }, 
        }, 
        'Omani': {
            'ca': { 'male': 'omanita', 'female': 'omanita' }, 
            'en': { 'male': 'Omani', 'female': 'Omani' }, 
            'es': { 'male': 'omaní', 'female': 'omaní' }, 
            'gl': { 'male': 'omaní', 'female': 'omaní' }, 
        }, 
        'Pakistani': {
            'ca': { 'male': 'pakistanès', 'female': 'pakistanesa' }, 
            'en': { 'male': 'Pakistani', 'female': 'Pakistani' }, 
            'es': { 'male': 'pakistaní', 'female': 'pakistaní' }, 
            'gl': { 'male': 'paquistaní', 'female': 'paquistaní' }, 
        }, 
        'Palauan': {
            'ca': { 'male': 'palauà', 'female': 'palauana' }, 
            'en': { 'male': 'Palauan', 'female': 'Palauan' }, 
            'es': { 'male': 'palauano', 'female': 'palauana' }, 
            'gl': { 'male': 'de Palau', 'female': 'de Palau' }, 
        }, 
        'Palestinian': {
            'ca': { 'male': 'palestí', 'female': 'palestina' }, 
            'en': { 'male': 'Palestinian', 'female': 'Palestinian' }, 
            'es': { 'male': 'palestino', 'female': 'palestina' }, 
            'gl': { 'male': 'palestino', 'female': 'palestina' }, 
        }, 
        'Panamanian': {
            'ca': { 'male': 'panameny', 'female': 'panamenya' }, 
            'en': { 'male': 'Panamanian', 'female': 'Panamanian' }, 
            'es': { 'male': 'panameño', 'female': 'panameña' }, 
            'gl': { 'male': 'panameño', 'female': 'panameña' }, 
        }, 
        'Papua New Guinean': {
            'ca': { 'male': 'papú', 'female': 'papú' }, 
            'en': { 'male': 'Papua New Guinean', 'female': 'Papua New Guinean' }, 
            'es': { 'male': 'papú', 'female': 'papú' }, 
            'gl': { 'male': 'papú', 'female': 'papú' }, 
        }, 
        'Papuan': {
            'ca': { 'male': 'papú', 'female': 'papú' }, 
            'en': { 'male': 'Papuan', 'female': 'Papuan' }, 
            'es': { 'male': 'papú', 'female': 'papú' }, 
            'gl': { 'male': 'papú', 'female': 'papú' }, 
        }, 
        'Paraguayan': {
            'ca': { 'male': 'paraguaià', 'female': 'paraguaiana' }, 
            'en': { 'male': 'Paraguayan', 'female': 'Paraguayan' }, 
            'es': { 'male': 'paraguayo', 'female': 'paraguaya' }, 
            'gl': { 'male': 'paraguaio', 'female': 'paraguaia' }, 
        }, 
        'Peruvian': {
            'ca': { 'male': 'peruà', 'female': 'peruana' }, 
            'en': { 'male': 'Peruvian', 'female': 'Peruvian' }, 
            'es': { 'male': 'peruano', 'female': 'peruana' }, 
            'gl': { 'male': 'peruano', 'female': 'peruana' }, 
        }, 
        'Philippine': {
            'ca': { 'male': 'filipí', 'female': 'filipina' },
            'en': { 'male': 'Philippine', 'female': 'Philippine' }, 
            'es': { 'male': 'filipino', 'female': 'filipina' }, 
            'gl': { 'male': 'filipino', 'female': 'filipina' }, 
        },
        'Polish': {
            'ca': { 'male': 'polonès', 'female': 'polonesa' },
            'en': { 'male': 'Polish', 'female': 'Polish' }, 
            'es': { 'male': 'polaco', 'female': 'polaca' }, 
            'gl': { 'male': 'polaco', 'female': 'polaca' }, 
        },
        'Portuguese': {
            'ca': { 'male': 'portuguès', 'female': 'portuguesa' }, 
            'en': { 'male': 'Portuguese', 'female': 'Portuguese' }, 
            'es': { 'male': 'portugués', 'female': 'portuguesa' }, 
            'gl': { 'male': 'portugués', 'female': 'portuguesa' }, 
        }, 
        'Puerto Rican': {
            'ca': { 'male': 'porto-riqueny', 'female': 'porto-riquenya' }, 
            'en': { 'male': 'Puerto Rican', 'female': 'Puerto Rican' }, 
            'es': { 'male': 'puertorriqueño', 'female': 'puertorriqueña' }, 
            'gl': { 'male': 'portorriqueño', 'female': 'portorriqueña' }, 
        }, 
        'Qatari': {
            'ca': { 'male': 'catarí', 'female': 'catarina' }, 
            'en': { 'male': 'Qatari', 'female': 'Qatari' }, 
            'es': { 'male': 'catarí', 'female': 'catarí' }, 
            'gl': { 'male': 'catarí', 'female': 'catarí' }, 
        }, 
        'Romanian': {
            'ca': { 'male': 'romanès', 'female': 'romanesa' }, 
            'en': { 'male': 'Romanian', 'female': 'Romanian' }, 
            'es': { 'male': 'rumano', 'female': 'rumana' }, 
            'gl': { 'male': 'romanés', 'female': 'romanesa' }, 
        }, 
        'Russian': {
            'ca': { 'male': 'rus', 'female': 'russa' }, 
            'en': { 'male': 'Russian', 'female': 'Russian' }, 
            'es': { 'male': 'ruso', 'female': 'rusa' }, 
            'gl': { 'male': 'ruso', 'female': 'rusa' }, 
        }, 
        'Rwandan': {
            'ca': { 'male': 'ruandès', 'female': 'ruandesa' }, 
            'en': { 'male': 'Rwandan', 'female': 'Rwandan' }, 
            'es': { 'male': 'ruandés', 'female': 'ruandesa' }, 
            'gl': { 'male': 'ruandés', 'female': 'ruandesa' }, 
        }, 
        'Salvadoran': {
            'ca': { 'male': 'salvadorenc', 'female': 'salvadorenca' }, 
            'en': { 'male': 'Salvadoran', 'female': 'Salvadoran' }, 
            'es': { 'male': 'salvadoreño', 'female': 'salvadoreña' }, 
            'gl': { 'male': 'salvadoreño', 'female': 'salvadoreña' }, 
        }, 
        'Sammarinese': {
            'ca': { 'male': 'sanmarinès', 'female': 'sanmarinesa' }, 
            'en': { 'male': 'Sammarinese', 'female': 'Sammarinese' }, 
            'es': { 'male': 'sanmarinense', 'female': 'sanmarinense' }, 
            'gl': { 'male': 'sanmariñés', 'female': 'sanmariñesa' }, 
        }, 
        'Samoan': {
            'ca': { 'male': 'samoà', 'female': 'samoana' }, 
            'en': { 'male': 'Samoan', 'female': 'Samoan' }, 
            'es': { 'male': 'samoano', 'female': 'samoana' }, 
            'gl': { 'male': 'samoano', 'female': 'samoana' }, 
        }, 
        'São Toméan': {
            'ca': { 'male': 'de São Tomé i Príncipe', 'female': 'de São Tomé i Príncipe' }, 
            'en': { 'male': 'São Toméan', 'female': 'São Toméan' }, 
            'es': { 'male': 'santotomense', 'female': 'santotomense' }, 
            'gl': { 'male': 'santomense', 'female': 'santomense' }, 
        }, 
        'Saudi': {
            'ca': { 'male': 'saudita', 'female': 'saudita' }, 
            'en': { 'male': 'Saudi', 'female': 'Saudi' }, 
            'es': { 'male': 'saudita', 'female': 'saudita' }, 
            'gl': { 'male': 'saudita', 'female': 'saudita' }, 
        }, 
        'Saudi Arabian': {
            'ca': { 'male': 'saudita', 'female': 'saudita' }, 
            'en': { 'male': 'Saudi', 'female': 'Saudi' }, 
            'es': { 'male': 'saudita', 'female': 'saudita' }, 
            'gl': { 'male': 'saudita', 'female': 'saudita' }, 
        }, 
        'Senegalese': {
            'ca': { 'male': 'senegalès', 'female': 'senegalesa' }, 
            'en': { 'male': 'Senegalese', 'female': 'Senegalese' }, 
            'es': { 'male': 'senegalés', 'female': 'senegalesa' }, 
            'gl': { 'male': 'senegalés', 'female': 'senegalesa' }, 
        }, 
        'Serbian': {
            'ca': { 'male': 'serbi', 'female': 'sèrbia' }, 
            'en': { 'male': 'Serbian', 'female': 'Serbian' }, 
            'es': { 'male': 'serbio', 'female': 'serbia' }, 
            'gl': { 'male': 'serbio', 'female': 'serbia' }, 
        }, 
        'Seychellois': {
            'ca': { 'male': 'seychellès', 'female': 'seychellesa' }, 
            'en': { 'male': 'Seychellois', 'female': 'Seychellois' }, 
            'es': { 'male': 'seychellense', 'female': 'seychellense' }, 
            'gl': { 'male': 'seychelense', 'female': 'seychelense' }, 
        }, 
        'Sierra Leonean': {
            'ca': { 'male': 'de Sierra Leone', 'female': 'de Sierra Leone' }, 
            'en': { 'male': 'Sierra Leonean', 'female': 'Sierra Leonean' }, 
            'es': { 'male': 'sierraleonés', 'female': 'sierraleonesa' }, 
            'gl': { 'male': 'serraleonino', 'female': 'serraleonina' }, 
        }, 
        'Singapore': {
            'ca': { 'male': 'singapurès', 'female': 'singapuresa' }, 
            'en': { 'male': 'Singapore', 'female': 'Singapore' }, 
            'es': { 'male': 'singapurense', 'female': 'singapurense' }, 
            'gl': { 'male': 'singapurense', 'female': 'singapurense' }, 
        }, 
        'Singaporean': {
            'ca': { 'male': 'singapurès', 'female': 'singapuresa' }, 
            'en': { 'male': 'Singaporean', 'female': 'Singaporean' }, 
            'es': { 'male': 'singapurense', 'female': 'singapurense' }, 
            'gl': { 'male': 'singapurense', 'female': 'singapurense' }, 
        }, 
        'Slovak': {
            'ca': { 'male': 'eslovac', 'female': 'eslovaca' }, 
            'en': { 'male': 'Slovak', 'female': 'Slovak' }, 
            'es': { 'male': 'eslovaco', 'female': 'eslovaca' }, 
            'gl': { 'male': 'eslovaco', 'female': 'eslovaca' }, 
        }, 
        'Slovene': {
            'ca': { 'male': 'eslovè', 'female': 'eslovena' }, 
            'en': { 'male': 'Slovene', 'female': 'Slovene' }, 
            'es': { 'male': 'esloveno', 'female': 'eslovena' }, 
            'gl': { 'male': 'esloveno', 'female': 'eslovena' }, 
        }, 
        'Slovenian': {
            'ca': { 'male': 'eslovè', 'female': 'eslovena' }, 
            'en': { 'male': 'Slovenian', 'female': 'Slovenian' }, 
            'es': { 'male': 'esloveno', 'female': 'eslovena' }, 
            'gl': { 'male': 'esloveno', 'female': 'eslovena' }, 
        }, 
        'Somali': {
            'ca': { 'male': 'somali', 'female': 'somali' }, 
            'en': { 'male': 'Somali', 'female': 'Somali' }, 
            'es': { 'male': 'somalí', 'female': 'somalí' }, 
            'gl': { 'male': 'somalí', 'female': 'somalí' }, 
        }, 
        'South African': {
            'ca': { 'male': 'sud-africà', 'female': 'sud-africana' }, 
            'en': { 'male': 'South African', 'female': 'South African' }, 
            'es': { 'male': 'sudafricano', 'female': 'sudafricana' }, 
            'gl': { 'male': 'sudafricano', 'female': 'sudafricana' }, 
        }, 
        'South Korean': {
            'ca': { 'male': 'sud-coreà', 'female': 'sud-coreana' }, 
            'en': { 'male': 'South Korean', 'female': 'South Korean' }, 
            'es': { 'male': 'surcoreano', 'female': 'surcoreana' }, 
            'gl': { 'male': 'surcoreano', 'female': 'surcoreana' }, 
        }, 
        'Spanish': {
            'ca': { 'male': 'espanyol', 'female': 'espanyola' }, 
            'en': { 'male': 'Spanish', 'female': 'Spanish' }, 
            'es': { 'male': 'español', 'female': 'española' }, 
            'gl': { 'male': 'español', 'female': 'española' }, 
        }, 
        'Sri Lankan': {
            'ca': { 'male': 'singalès', 'female': 'singalesa' }, 
            'en': { 'male': 'Sri Lankan', 'female': 'Sri Lankan' }, 
            'es': { 'male': 'ceilanés', 'female': 'ceilanesa' }, 
            'gl': { 'male': 'srilankés', 'female': 'srilankesa' }, 
        }, 
        'Sudanese': {
            'ca': { 'male': 'sudanès', 'female': 'sudanesa' }, 
            'en': { 'male': 'Sudanese', 'female': 'Sudanese' }, 
            'es': { 'male': 'sudanés', 'female': 'sudanesa' }, 
            'gl': { 'male': 'sudanés', 'female': 'sudanesa' }, 
        }, 
        'Surinamese': {
            'ca': { 'male': 'surinamès', 'female': 'surinamesa' }, 
            'en': { 'male': 'Surinamese', 'female': 'Surinamese' }, 
            'es': { 'male': 'surinamés', 'female': 'surinamesa' }, 
            'gl': { 'male': 'surinamés', 'female': 'surinamesa' }, 
        }, 
        'Swedish': {
            'ca': { 'male': 'suec', 'female': 'sueca' }, 
            'en': { 'male': 'Swedish', 'female': 'Swedish' }, 
            'es': { 'male': 'sueco', 'female': 'sueca' }, 
            'gl': { 'male': 'sueco', 'female': 'sueca' }, 
        }, 
        'Swiss': {
            'ca': { 'male': 'suís', 'female': 'suïssa' }, 
            'en': { 'male': 'Swiss', 'female': 'Swiss' }, 
            'es': { 'male': 'suizo', 'female': 'suiza' }, 
            'gl': { 'male': 'suizo', 'female': 'suiza' }, 
        }, 
        'Syrian': {
            'ca': { 'male': 'sirià', 'female': 'siriana' }, 
            'en': { 'male': 'Syrian', 'female': 'Syrian' }, 
            'es': { 'male': 'sirio', 'female': 'siria' }, 
            'gl': { 'male': 'sirio', 'female': 'siria' }, 
        }, 
        'Tajikistani': {
            'ca': { 'male': 'tadjik', 'female': 'tadjik' }, 
            'en': { 'male': 'Tajikistani', 'female': 'Tajikistani' }, 
            'es': { 'male': 'tayiko', 'female': 'tayika' }, 
            'gl': { 'male': 'taxiquistano', 'female': 'taxiquistana' }, 
        }, 
        'Tanzanian': {
            'ca': { 'male': 'tanzà', 'female': 'tanzana' }, 
            'en': { 'male': 'Tanzanian', 'female': 'Tanzanian' }, 
            'es': { 'male': 'tanzano', 'female': 'tanzana' }, 
            'gl': { 'male': 'tanzano', 'female': 'tanzana' }, 
        }, 
        'Thai': {
            'ca': { 'male': 'tailandès', 'female': 'tailandesa' }, 
            'en': { 'male': 'Thai', 'female': 'Thai' }, 
            'es': { 'male': 'tailandés', 'female': 'tailandesa' }, 
            'gl': { 'male': 'tailandés', 'female': 'tailandesa' }, 
        }, 
        'Timorese': {
            'ca': { 'male': 'timorès', 'female': 'timoresa' }, 
            'en': { 'male': 'Timorese', 'female': 'Timorese' }, 
            'es': { 'male': 'timorense', 'female': 'timorense' }, 
            'gl': { 'male': 'timorense', 'female': 'timorense' }, 
        }, 
        'Togolese': {
            'ca': { 'male': 'togolès', 'female': 'togolesa' }, 
            'en': { 'male': 'Togolese', 'female': 'Togolese' }, 
            'es': { 'male': 'togolés', 'female': 'togolesa' }, 
            'gl': { 'male': 'togolés', 'female': 'togolesa' }, 
        }, 
        'Tongan': {
            'ca': { 'male': 'tongalès', 'female': 'tongalesa' }, 
            'en': { 'male': 'Tongan', 'female': 'Tongan' }, 
            'es': { 'male': 'tongano', 'female': 'tongana' }, 
            'gl': { 'male': 'tongano', 'female': 'tongana' }, 
        }, 
        'Trinidadian': {
            'ca': { 'male': 'de Trinitat i Tobago', 'female': 'de Trinitat i Tobago' }, 
            'en': { 'male': 'Trinidadian', 'female': 'Trinidadian' }, 
            'es': { 'male': 'trinitense', 'female': 'trinitense' }, 
            'gl': { 'male': 'trinitense', 'female': 'trinitense' }, 
        }, 
        'Tobagonian': {
            'ca': { 'male': 'de Trinitat i Tobago', 'female': 'de Trinitat i Tobago' }, 
            'en': { 'male': 'Tobagonian', 'female': 'Tobagonian' }, 
            'es': { 'male': 'trinitense', 'female': 'trinitense' }, 
            'gl': { 'male': 'trinitense', 'female': 'trinitense' }, 
        }, 
        'Tunisian': {
            'ca': { 'male': 'tunisià', 'female': 'tunisiana' }, 
            'en': { 'male': 'Tunisian', 'female': 'Tunisian' }, 
            'es': { 'male': 'tunecino', 'female': 'tunecina' }, 
            'gl': { 'male': 'tunesino', 'female': 'tunesina' }, 
        }, 
        'Turkish': {
            'ca': { 'male': 'turc', 'female': 'turca' }, 
            'en': { 'male': 'Turkish', 'female': 'Turkish' }, 
            'es': { 'male': 'turco', 'female': 'turca' }, 
            'gl': { 'male': 'turco', 'female': 'turca' }, 
        }, 
        'Turkmen': {
            'ca': { 'male': 'turcman', 'female': 'turcmana' }, 
            'en': { 'male': 'Turkmen', 'female': 'Turkmen' }, 
            'es': { 'male': 'turcomano', 'female': 'turcomana' }, 
            'gl': { 'male': 'turcomán', 'female': 'turcomá' }, 
        }, 
        'Tuvaluan': {
            'ca': { 'male': 'tuvalià', 'female': 'tuvaliana' }, 
            'en': { 'male': 'Tuvaluan', 'female': 'Tuvaluan' }, 
            'es': { 'male': 'tuvaluano', 'female': 'tuvaluana' }, 
            'gl': { 'male': 'tuvaluano', 'female': 'tuvaluana' }, 
        }, 
        'Ugandan': {
            'ca': { 'male': 'ugandès', 'female': 'ugandesa' }, 
            'en': { 'male': 'Ugandan', 'female': 'Ugandan' }, 
            'es': { 'male': 'ugandés', 'female': 'ugandesa' }, 
            'gl': { 'male': 'ugandés', 'female': 'ugandesa' }, 
        }, 
        'UK': {
            'ca': { 'male': 'britànic', 'female': 'britànica' },
            'en': { 'male': 'UK', 'female': 'UK' }, 
            'es': { 'male': 'británico', 'female': 'británica' }, 
            'gl': { 'male': 'británico', 'female': 'británica' }, 
        },
        'U.K.': {
            'ca': { 'male': 'britànic', 'female': 'britànica' },
            'en': { 'male': 'U.K.', 'female': 'U.K.' }, 
            'es': { 'male': 'británico', 'female': 'británica' }, 
            'gl': { 'male': 'británico', 'female': 'británica' }, 
        },
        'Ukrainian': {
            'ca': { 'male': 'ucraïnès', 'female': 'ucraïnesa' }, 
            'en': { 'male': 'Ukrainian', 'female': 'Ukrainian' }, 
            'es': { 'male': 'ucraniano', 'female': 'ucraniana' }, 
            'gl': { 'male': 'ucraíno', 'female': 'ucraína' }, 
        }, 
        'United States': {
            'ca': { 'male': 'estatunidenc', 'female': 'estatunidenca' }, 
            'en': { 'male': 'United States', 'female': 'United States' }, 
            'es': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
            'gl': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
        }, 
        'Uruguayan': {
            'ca': { 'male': 'uruguaià', 'female': 'uruguaiana' }, 
            'en': { 'male': 'Uruguayan', 'female': 'Uruguayan' }, 
            'es': { 'male': 'uruguayo', 'female': 'uruguaya' }, 
            'gl': { 'male': 'uruguaio', 'female': 'uruguaia' }, 
        }, 
        'US': {
            'ca': { 'male': 'estatunidenc', 'female': 'estatunidenca' }, 
            'en': { 'male': 'US', 'female': 'US' }, 
            'es': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
            'gl': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
        }, 
        'U.S.': {
            'ca': { 'male': 'estatunidenc', 'female': 'estatunidenca' }, 
            'en': { 'male': 'U.S.', 'female': 'U.S.' }, 
            'es': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
            'gl': { 'male': 'estadounidense', 'female': 'estadounidense' }, 
        }, 
        'Uzbek': {
            'ca': { 'male': 'uzbek', 'female': 'uzbeka' }, 
            'en': { 'male': 'Uzbek', 'female': 'Uzbek' }, 
            'es': { 'male': 'uzbeko', 'female': 'uzbeka' }, 
            'gl': { 'male': 'uzbeko', 'female': 'uzbeka' }, 
        }, 
        'Uzbekistani': {
            'ca': { 'male': 'uzbek', 'female': 'uzbeka' }, 
            'en': { 'male': 'Uzbekistani', 'female': 'Uzbekistani' }, 
            'es': { 'male': 'uzbeko', 'female': 'uzbeka' }, 
            'gl': { 'male': 'uzbeko', 'female': 'uzbeka' }, 
        }, 
        'Vanuatuan': {
            'ca': { 'male': 'vanuatuenc', 'female': 'vanuatuenca' }, 
            'en': { 'male': 'Vanuatuan', 'female': 'Vanuatuan' }, 
            'es': { 'male': 'vanuatuense', 'female': 'vanuatuense' }, 
            'gl': { 'male': 'vanuatiano', 'female': 'vanuatiana' }, 
        }, 
        'Vatican': {
            'ca': { 'male': 'vaticà', 'female': 'vaticana' }, 
            'en': { 'male': 'Vatican', 'female': 'Vatican' }, 
            'es': { 'male': 'vaticano', 'female': 'vaticana' }, 
            'gl': { 'male': 'vaticano', 'female': 'vaticana' }, 
        }, 
        'Venezuelan': {
            'ca': { 'male': 'veneçolà', 'female': 'veneçolana' }, 
            'en': { 'male': 'Venezuelan', 'female': 'Venezuelan' }, 
            'es': { 'male': 'venezolano', 'female': 'venezolana' }, 
            'gl': { 'male': 'venezolano', 'female': 'venezolana' }, 
        }, 
        'Vietnamese': {
            'ca': { 'male': 'vietnamita', 'female': 'vietnamita' }, 
            'en': { 'male': 'Vietnamese', 'female': 'Vietnamese' }, 
            'es': { 'male': 'vietnamita', 'female': 'vietnamita' }, 
            'gl': { 'male': 'vietnamita', 'female': 'vietnamita' }, 
        }, 
        'Yemeni': {
            'ca': { 'male': 'iemenita', 'female': 'iemenita' }, 
            'en': { 'male': 'Yemeni', 'female': 'Yemeni' }, 
            'es': { 'male': 'yemení', 'female': 'yemení' }, 
            'gl': { 'male': 'iemení', 'female': 'iemení' }, 
        }, 
        'Zambian': {
            'ca': { 'male': 'zambià', 'female': 'zambiana' }, 
            'en': { 'male': 'Zambian', 'female': 'Zambian' }, 
            'es': { 'male': 'zambiano', 'female': 'zambiana' }, 
            'gl': { 'male': 'zambiano', 'female': 'zambiana' }, 
        }, 
        'Zimbabwean': {
            'ca': { 'male': 'zimbabuès', 'female': 'zimbabuesa' }, 
            'en': { 'male': 'Zimbabwean', 'female': 'Zimbabwean' }, 
            'es': { 'male': 'zimbabuense', 'female': 'zimbabuense' }, 
            'gl': { 'male': 'cimbabuense', 'female': 'cimbabuense' }, 
        }, 
    }
    #more occupations https://query.wikidata.org/#SELECT%20%3Foccupation%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3AQ142.%0A%20%20%20%20%3Fitem%20wdt%3AP106%20%3Foccupation.%0A%20%20%20%20%23SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D%0AGROUP%20by%20%3Foccupation%0AORDER%20BY%20DESC%28%3Fcount%29
    #translations https://query.wikidata.org/#SELECT%20%3FitemDescription%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP106%20wd%3AQ28389.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER%28LANG%28%3FitemDescription%29%20%3D%20%22gl%22%29.%20%20%7D%0A%09FILTER%20%28BOUND%28%3FitemDescription%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC%28%3Fcount%29
    #https://query.wikidata.org/#SELECT%20%3FitemDescription%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5%20.%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3AQ142%20.%0A%09OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER%28LANG%28%3FitemDescription%29%20%3D%20%22en%22%29.%20%20%7D%0A%09FILTER%20%28BOUND%28%3FitemDescription%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC%28%3Fcount%29
    translationsOccupations = {
        '~ actor': {
            'ca': { 'male': 'actor ~', 'female': 'actriu ~' }, 
            'en': { 'male': '~ actor', 'female': '~ actress' }, 
            'es': { 'male': 'actor ~', 'female': 'actriz ~' }, 
            'gl': { 'male': 'actor ~', 'female': 'actriz ~' }, 
        }, 
        '~ architect': {
            'ca': { 'male': 'arquitecte ~', 'female': 'arquitecta ~' }, 
            'en': { 'male': '~ architect', 'female': '~ architect' }, 
            'es': { 'male': 'arquitecto ~', 'female': 'arquitecta ~' }, 
            'gl': { 'male': 'arquitecto ~', 'female': 'arquitecta ~' }, 
        }, 
        '~ artist': {
            'ca': { 'male': 'artista ~', 'female': 'artista ~' }, 
            'en': { 'male': '~ artist', 'female': '~ artist' }, 
            'es': { 'male': 'artista ~', 'female': 'artista ~' }, 
            'gl': { 'male': 'artista ~', 'female': 'artista ~' }, 
        }, 
        '~ association football player': {
            'ca': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
            'en': { 'male': '~ association football player', 'female': '~ association football player' }, 
            'es': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
            'gl': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
        }, 
        '~ astronomer': {
            'ca': { 'male': 'astrònom ~', 'female': 'astrònoma ~' }, 
            'en': { 'male': '~ astronomer', 'female': '~ astronomer' }, 
            'es': { 'male': 'astrónomo ~', 'female': 'astrónoma ~' }, 
            'gl': { 'male': 'astrónomo ~', 'female': 'astrónoma ~' }, 
        }, 
        '~ botanist': {
            'ca': { 'male': 'botànic ~', 'female': 'botànica ~' }, 
            'en': { 'male': '~ botanist', 'female': '~ botanist' }, 
            'es': { 'male': 'botánico ~', 'female': 'botánica ~' }, 
            'gl': { 'male': 'botánico ~', 'female': 'botánica ~' }, 
        }, 
        '~ chemist': {
            'ca': { 'male': 'químic ~', 'female': 'química ~' }, 
            'en': { 'male': '~ chemist', 'female': '~ chemist' }, 
            'es': { 'male': 'químico ~', 'female': 'química ~' }, 
            'gl': { 'male': 'químico ~', 'female': 'química ~' }, 
        }, 
        '~ composer': {
            'ca': { 'male': 'compositor ~', 'female': 'compositora ~' }, 
            'en': { 'male': '~ composer', 'female': '~ composer' }, 
            'es': { 'male': 'compositor ~', 'female': 'compositora ~' }, 
            'gl': { 'male': 'compositor ~', 'female': 'compositora ~' }, 
        }, 
        '~ economist': {
            'ca': { 'male': 'economista ~', 'female': 'economista ~' }, 
            'en': { 'male': '~ economist', 'female': '~ economist' }, 
            'es': { 'male': 'economista ~', 'female': 'economista ~' }, 
            'gl': { 'male': 'economista ~', 'female': 'economista ~' }, 
        }, 
        '~ engineer': {
            'ca': { 'male': 'enginyer ~', 'female': 'enginyera ~' }, 
            'en': { 'male': '~ engineer', 'female': '~ engineer' }, 
            'es': { 'male': 'ingeniero ~', 'female': 'ingeniera ~' }, 
            'gl': { 'male': 'enxeñeiro ~', 'female': 'enxeñeira ~' }, 
        }, 
        '~ film director': {
            'ca': { 'male': 'director de cinema ~', 'female': 'directora de cinema ~' }, 
            'en': { 'male': '~ film director', 'female': '~ film director' }, 
            'es': { 'male': 'director de cine ~', 'female': 'directora de cine ~' }, 
            'gl': { 'male': 'director de cinema ~', 'female': 'directora de cinema ~' }, 
        }, 
        '~ footballer': {
            'ca': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
            'en': { 'male': '~ footballer', 'female': '~ footballer' }, 
            'es': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
            'gl': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
        }, 
        '~ historian': {
            'ca': { 'male': 'historiador ~', 'female': 'historiadora ~' }, 
            'en': { 'male': '~ historian', 'female': '~ historian' }, 
            'es': { 'male': 'historiador ~', 'female': 'historiadora ~' }, 
            'gl': { 'male': 'historiador ~', 'female': 'historiadora ~' }, 
        }, 
        '~ journalist': {
            'ca': { 'male': 'periodista ~', 'female': 'periodista ~' }, 
            'en': { 'male': '~ journalist', 'female': '~ journalist' }, 
            'es': { 'male': 'periodista ~', 'female': 'periodista ~' }, 
            'gl': { 'male': 'xornalista ~', 'female': 'xornalista ~' }, 
        }, 
        '~ jurist': {
            'ca': { 'male': 'jurista ~', 'female': 'jurista ~' }, 
            'en': { 'male': '~ jurist', 'female': '~ jurist' }, 
            'es': { 'male': 'jurista ~', 'female': 'jurista ~' }, 
            'gl': { 'male': 'xurista ~', 'female': 'xurista ~' }, 
        }, 
        '~ mathematician': {
            'ca': { 'male': 'matemàtic ~', 'female': 'matemàtica ~' }, 
            'en': { 'male': '~ mathematician', 'female': '~ mathematician' }, 
            'es': { 'male': 'matemático ~', 'female': 'matemática ~' }, 
            'gl': { 'male': 'matemático ~', 'female': 'matemática ~' }, 
        }, 
        '~ musician': {
            'ca': { 'male': 'músic ~', 'female': 'músic ~' }, 
            'en': { 'male': '~ musician', 'female': '~ musician' }, 
            'es': { 'male': 'músico ~', 'female': 'músico ~' }, 
            'gl': { 'male': 'músico ~', 'female': 'músico ~' }, 
        }, 
        '~ painter': {
            'ca': { 'male': 'pintor ~', 'female': 'pintora ~' }, 
            'en': { 'male': '~ painter', 'female': '~ painter' }, 
            'es': { 'male': 'pintor ~', 'female': 'pintora ~' }, 
            'gl': { 'male': 'pintor ~', 'female': 'pintora ~' }, 
        }, 
        '~ philosopher': {
            'ca': { 'male': 'filòsof ~', 'female': 'filòsofa ~' }, 
            'en': { 'male': '~ philosopher', 'female': '~ philosopher' }, 
            'es': { 'male': 'filósofo ~', 'female': 'filósofa ~' }, 
            'gl': { 'male': 'filósofo ~', 'female': 'filósofa ~' }, 
        }, 
        '~ photographer': {
            'ca': { 'male': 'fotògraf ~', 'female': 'fotògrafa ~' }, 
            'en': { 'male': '~ photographer', 'female': '~ photographer' }, 
            'es': { 'male': 'fotógrafo ~', 'female': 'fotógrafa ~' }, 
            'gl': { 'male': 'fotógrafo ~', 'female': 'fotógrafa ~' }, 
        }, 
        '~ physician': {
            'ca': { 'male': 'metge ~', 'female': 'metgessa ~' }, 
            'en': { 'male': '~ physician', 'female': '~ physician' }, 
            'es': { 'male': 'médico ~', 'female': 'médica ~' }, 
            'gl': { 'male': 'médico ~', 'female': 'médica ~' }, 
        }, 
        '~ physicist': {
            'ca': { 'male': 'físic ~', 'female': 'física ~' }, 
            'en': { 'male': '~ physicist', 'female': '~ physicist' }, 
            'es': { 'male': 'físico ~', 'female': 'física ~' }, 
            'gl': { 'male': 'físico ~', 'female': 'física ~' }, 
        }, 
        '~ pianist': {
            'ca': { 'male': 'pianista ~', 'female': 'pianista ~' }, 
            'en': { 'male': '~ pianist', 'female': '~ pianist' }, 
            'es': { 'male': 'pianista ~', 'female': 'pianista ~' }, 
            'gl': { 'male': 'pianista ~', 'female': 'pianista ~' }, 
        }, 
        '~ poet': {
            'ca': { 'male': 'poeta ~', 'female': 'poetessa ~' }, 
            'en': { 'male': '~ poet', 'female': '~ poet' }, 
            'es': { 'male': 'poeta ~', 'female': 'poetisa ~' }, 
            'gl': { 'male': 'poeta ~', 'female': 'poetisa ~' }, 
        }, 
        '~ politician': {
            'ca': { 'male': 'polític ~', 'female': 'política ~' }, 
            'en': { 'male': '~ politician', 'female': '~ politician' }, 
            'es': { 'male': 'político ~', 'female': 'política ~' }, 
            'gl': { 'male': 'político ~', 'female': 'política ~' }, 
        }, 
        '~ screenwriter': {
            'ca': { 'male': 'guionista ~', 'female': 'guionista ~' }, 
            'en': { 'male': '~ screenwriter', 'female': '~ screenwriter' }, 
            'es': { 'male': 'guionista ~', 'female': 'guionista ~' }, 
            'gl': { 'male': 'guionista ~', 'female': 'guionista ~' }, 
        }, 
        '~ sculptor': {
            'ca': { 'male': 'escultor ~', 'female': 'escultora ~' }, 
            'en': { 'male': '~ sculptor', 'female': '~ sculptor' }, 
            'es': { 'male': 'escultor ~', 'female': 'escultora ~' }, 
            'gl': { 'male': 'escultor ~', 'female': 'escultora ~' }, 
        }, 
        '~ singer': {
            'ca': { 'male': 'cantant ~', 'female': 'cantant ~' }, 
            'en': { 'male': '~ singer', 'female': '~ singer' }, 
            'es': { 'male': 'cantante ~', 'female': 'cantante ~' }, 
            'gl': { 'male': 'cantante ~', 'female': 'cantante ~' }, 
        }, 
        '~ sociologist': {
            'ca': { 'male': 'sociòleg ~', 'female': 'sociòloga ~' }, 
            'en': { 'male': '~ sociologist', 'female': '~ sociologist' }, 
            'es': { 'male': 'sociólogo ~', 'female': 'socióloga ~' }, 
            'gl': { 'male': 'sociólogo ~', 'female': 'socióloga ~' }, 
        }, 
        '~ soldier': {
            'ca': { 'male': 'militar ~', 'female': 'militar ~' }, 
            'en': { 'male': '~ soldier', 'female': '~ soldier' }, 
            'es': { 'male': 'militar ~', 'female': 'militar ~' }, 
            'gl': { 'male': 'militar ~', 'female': 'militar ~' }, 
        }, 
        '~ tennis player': {
            'ca': { 'male': 'tennista professional ~', 'female': 'tennista professional ~' }, 
            'en': { 'male': '~ tennis player', 'female': '~ tennis player' }, 
            'es': { 'male': 'tenista profesional ~', 'female': 'tenista profesional ~' }, 
            'gl': { 'male': 'tenista profesional ~', 'female': 'tenista profesional ~' }, 
        }, 
        '~ writer': {
            'ca': { 'male': 'escriptor ~', 'female': 'escriptora ~' }, 
            'en': { 'male': '~ writer', 'female': '~ writer' }, 
            'es': { 'male': 'escritor ~', 'female': 'escritora ~' }, 
            'gl': { 'male': 'escritor ~', 'female': 'escritora ~' }, 
        }, 
    }
    translations = {}
    for occupkey, occupdic in translationsOccupations.items():
        for natkey, natdic in translationsNationalities.items():
            translations[re.sub('~', natkey, occupkey)] = {}
            for translang in occupdic.keys():
                translations[re.sub('~', natkey, occupkey)][translang] = {
                    'male': re.sub('~', natdic[translang]['male'], occupdic[translang]['male']), 
                    'female': re.sub('~', natdic[translang]['female'], occupdic[translang]['female']), 
                }
    c2 = 1
    total2 = 0
    for targetlang in targetlangs:
        for genderq, genderlabel in genders.items():
            for translation in translations.keys():
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%20%20%20%20%3Fitem%20wdt%3AP31%20wd%3AQ5%20.%20%23instanceof%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3A'+genderq+'%20.%20%23gender%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22'+urllib.parse.quote(translation)+'%22%40en.%20%23description%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+targetlang+'%22).%20%20%7D%0A%20%20%20%20FILTER%20(!BOUND(%3FitemDescription))%0A%7D'
                url = '%s&format=json' % (url)
                sparql = getURL(url=url)
                json1 = loadSPARQL(sparql=sparql)
                total = len(json1['results']['bindings'])
                total2 += total
                c = 1
                for result in json1['results']['bindings']:
                    q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                    print('\n== %s (%d/%d; %s; %s; %d/%d) ==' % (q, c, total, translation, genderlabel, c2, total2))
                    c += 1
                    c2 += 1
                    item = pywikibot.ItemPage(repo, q)
                    item.get()
                    descriptions = item.descriptions
                    addedlangs = []
                    for lang in translations[translation].keys():
                        if not lang in descriptions.keys():
                            descriptions[lang] = translations[translation][lang][genderlabel]
                            addedlangs.append(lang)
                    data = { 'descriptions': descriptions }
                    addedlangs.sort()
                    if addedlangs:
                        summary = 'BOT - Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                        print(summary)
                        try:
                            item.editEntity(data, summary=summary)
                        except:
                            print('Error while saving')
                            continue
                    else:
                        print('No changes needed')

if __name__ == "__main__":
    main()
