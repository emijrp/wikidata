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

import re
import sys

import pwb
import pywikibot
from quickstatements import *

def main():
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
        'Czech': {
            'ca': { 'male': 'txec', 'female': 'txeca' },
            'en': { 'male': 'Czech', 'female': 'Czech' }, 
            'es': { 'male': 'checo', 'female': 'checa' }, 
            'gl': { 'male': 'checo', 'female': 'checa' }, 
        },
        'Ecuadorian': {
            'ca': { 'male': 'equatorià', 'female': 'equatoriana' },
            'en': { 'male': 'Ecuadorian', 'female': 'Ecuadorian' }, 
            'es': { 'male': 'ecuatoriano', 'female': 'ecuatoriana' }, 
            'gl': { 'male': 'ecuatoriano', 'female': 'ecuatoriana' }, 
        },
        'French': {
            'ca': { 'male': 'francés', 'female': 'francesa' },
            'en': { 'male': 'French', 'female': 'French' }, 
            'es': { 'male': 'francés', 'female': 'francesa' }, 
            'gl': { 'male': 'francés', 'female': 'francesa' }, 
        },
        'German': {
            'ca': { 'male': 'alemany', 'female': 'alemanya' },
            'en': { 'male': 'German', 'female': 'German' }, 
            'es': { 'male': 'alemán', 'female': 'alemana' }, 
            'gl': { 'male': 'alemán', 'female': 'alemá' }, 
        },
        'Herzegovinian': {
            'ca': { 'male': 'hercegoví', 'female': 'hercegovina' },
            'en': { 'male': 'Herzegovinian', 'female': 'Herzegovinian' }, 
            'es': { 'male': 'herzegovino', 'female': 'herzegovina' }, 
            'gl': { 'male': 'hercegovino', 'female': 'hercegovina' }, 
        },
        'Italian': {
            'ca': { 'male': 'italià', 'female': 'italiana' }, 
            'en': { 'male': 'Italian ', 'female': 'Italian' }, 
            'es': { 'male': 'italiano', 'female': 'italiana' }, 
            'gl': { 'male': 'italiano', 'female': 'italiana' }, 
        }, 
        'Portuguese': {
            'ca': { 'male': 'portuguès', 'female': 'portuguesa' }, 
            'en': { 'male': 'Portuguese', 'female': 'Portuguese' }, 
            'es': { 'male': 'portugués', 'female': 'portuguesa' }, 
            'gl': { 'male': 'portugués', 'female': 'portuguesa' }, 
        }, 
        'Russian': {
            'ca': { 'male': 'rus', 'female': 'russa' }, 
            'en': { 'male': 'Russian', 'female': 'Russian' }, 
            'es': { 'male': 'ruso', 'female': 'rusa' }, 
            'gl': { 'male': 'ruso', 'female': 'rusa' }, 
        }, 
        'Spanish': {
            'ca': { 'male': 'espanyol', 'female': 'espanyola' }, 
            'en': { 'male': 'Spanish', 'female': 'Spanish' }, 
            'es': { 'male': 'español', 'female': 'española' }, 
            'gl': { 'male': 'español', 'female': 'española' }, 
        }, 
    }
    #more occupations https://query.wikidata.org/#SELECT%20%3Foccupation%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP27%20wd%3AQ142.%0A%20%20%20%20%3Fitem%20wdt%3AP106%20%3Foccupation.%0A%20%20%20%20%23SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D%0AGROUP%20by%20%3Foccupation%0AORDER%20BY%20DESC%28%3Fcount%29
    #translations https://query.wikidata.org/#SELECT%20%3FitemDescription%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ5.%0A%20%20%20%20%3Fitem%20wdt%3AP106%20wd%3AQ28389.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER%28LANG%28%3FitemDescription%29%20%3D%20%22gl%22%29.%20%20%7D%0A%09FILTER%20%28BOUND%28%3FitemDescription%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC%28%3Fcount%29
    translationsOccupations = {
        '~ actor': {
            'ca': { 'male': 'actor ~', 'female': 'actriu ~' }, 
            'en': { 'male': '~ actor', 'female': '~ actress' }, 
            'es': { 'male': 'actor ~', 'female': 'actriz ~' }, 
            'gl': { 'male': 'actor ~', 'female': 'actriz ~' }, 
        }, 
        '~ association football player': {
            'ca': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
            'en': { 'male': '~ association football player', 'female': '~ association football player' }, 
            'es': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
            'gl': { 'male': 'futbolista ~', 'female': 'futbolista ~' }, 
        }, 
        '~ composer': {
            'ca': { 'male': 'compositor ~', 'female': 'compositora ~' }, 
            'en': { 'male': '~ composer', 'female': '~ composer' }, 
            'es': { 'male': 'compositor ~', 'female': 'compositora ~' }, 
            'gl': { 'male': 'compositor ~', 'female': 'compositora ~' }, 
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
        '~ painter': {
            'ca': { 'male': 'pintor ~', 'female': 'pintora ~' }, 
            'en': { 'male': '~ painter', 'female': '~ painter' }, 
            'es': { 'male': 'pintor ~', 'female': 'pintora ~' }, 
            'gl': { 'male': 'pintor ~', 'female': 'pintora ~' }, 
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
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%20%20%20%20%3Fitem%20wdt%3AP31%20wd%3AQ5%20.%20%23instanceof%0A%20%20%20%20%3Fitem%20wdt%3AP21%20wd%3A'+genderq+'%20.%20%23gender%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22'+re.sub(' ', '%20', translation)+'%22%40en.%20%23description%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22'+targetlang+'%22).%20%20%7D%0A%20%20%20%20FILTER%20(!BOUND(%3FitemDescription))%0A%7D'
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

if __name__ == "__main__":
    main()
