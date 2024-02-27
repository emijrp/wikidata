#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017-2024 emijrp <emijrp@gmail.com>
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
import sys
import time
import urllib.parse

import pywikibot
from wikidatafun import *

"""
    #filter by language
    SELECT ?item
    WHERE {
        ?item wdt:P31 wd:Q101352 .
        FILTER NOT EXISTS { ?item wdt:P31 wd:Q4167410 } . 
        OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "ca").  }
        FILTER (!BOUND(?itemDescription))
    }
    #all surnames
    SELECT ?item
    WHERE {
        ?item wdt:P31 wd:Q101352 .
        FILTER NOT EXISTS { ?item wdt:P31 wd:Q4167410 } . 
    }
"""
#family
#genus
#species
#proteins https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3FitemDescription%20(COUNT(%3Fitem)%20AS%20%3Fcount)%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP279%20wd%3AQ8054.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22mammalian%20protein%20found%20in%20Mus%20musculus%22%40en.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09FILTER%20(BOUND(%3FitemDescription))%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC(%3Fcount)

def genQuery(p31='', desc='', desclang=''):
    if not p31 or not desc or not desclang:
        print('Error genQuery', p31, desc, desclang)
        sys.exit()
    query = [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:%s ;
                  wdt:P31 ?instance .
            ?item schema:description "%s"@%s.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """ % (p31, desc, desclang) 
    ]
    return query

def genQueriesByConstellation(p31='', desc='', desclang=''):
    #https://query.wikidata.org/#SELECT%20%3FitemDescBase%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%20%20SERVICE%20bd%3Asample%20%7B%0A%20%20%20%20%23%3Fitem%20wdt%3AP31%20%3Fp31%20.%0A%20%20%20%20%3Fitem%20wdt%3AP31%20wd%3AQ523%20.%0A%20%20%20%20bd%3AserviceParam%20bd%3Asample.limit%20100000%20.%0A%20%20%20%20bd%3AserviceParam%20bd%3Asample.sampleType%20%22RANDOM%22%20.%0A%20%20%7D%0A%20%20%23%3Fitem%20wdt%3AP21%20wd%3AQ6581097.%0A%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescBase.%20FILTER%28LANG%28%3FitemDescBase%29%20%3D%20%22en%22%29.%20%20%7D%0A%20%20FILTER%20%28BOUND%28%3FitemDescBase%29%29%0A%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescTarget.%20FILTER%28LANG%28%3FitemDescTarget%29%20%3D%20%22es%22%29.%20%20%7D%0A%20%20FILTER%20%28%21BOUND%28%3FitemDescTarget%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescBase%0AORDER%20BY%20DESC%28%3Fcount%29%0ALIMIT%20100
    queries = {}
    queries[desc.replace('~', 'Andromeda')] = genQuery(p31=p31, desc=desc.replace('~', 'Andromeda'), desclang=desclang)
    queries[desc.replace('~', 'Aquarius')] = genQuery(p31=p31, desc=desc.replace('~', 'Aquarius'), desclang=desclang)
    queries[desc.replace('~', 'Aquila')] = genQuery(p31=p31, desc=desc.replace('~', 'Aquila'), desclang=desclang)
    queries[desc.replace('~', 'Aries')] = genQuery(p31=p31, desc=desc.replace('~', 'Aries'), desclang=desclang)
    queries[desc.replace('~', 'Auriga')] = genQuery(p31=p31, desc=desc.replace('~', 'Auriga'), desclang=desclang)
    queries[desc.replace('~', 'Camelopardalis')] = genQuery(p31=p31, desc=desc.replace('~', 'Camelopardalis'), desclang=desclang)
    queries[desc.replace('~', 'Cancer')] = genQuery(p31=p31, desc=desc.replace('~', 'Cancer'), desclang=desclang)
    queries[desc.replace('~', 'Capricornus')] = genQuery(p31=p31, desc=desc.replace('~', 'Capricornus'), desclang=desclang)
    queries[desc.replace('~', 'Carina')] = genQuery(p31=p31, desc=desc.replace('~', 'Carina'), desclang=desclang)
    queries[desc.replace('~', 'Cassiopeia')] = genQuery(p31=p31, desc=desc.replace('~', 'Cassiopeia'), desclang=desclang)
    queries[desc.replace('~', 'Cepheus')] = genQuery(p31=p31, desc=desc.replace('~', 'Cepheus'), desclang=desclang)
    queries[desc.replace('~', 'Centaurus')] = genQuery(p31=p31, desc=desc.replace('~', 'Centaurus'), desclang=desclang)
    queries[desc.replace('~', 'Cygnus')] = genQuery(p31=p31, desc=desc.replace('~', 'Cygnus'), desclang=desclang)
    queries[desc.replace('~', 'Draco')] = genQuery(p31=p31, desc=desc.replace('~', 'Draco'), desclang=desclang)
    queries[desc.replace('~', 'Gemini')] = genQuery(p31=p31, desc=desc.replace('~', 'Gemini'), desclang=desclang)
    queries[desc.replace('~', 'Hercules')] = genQuery(p31=p31, desc=desc.replace('~', 'Hercules'), desclang=desclang)
    queries[desc.replace('~', 'Hydra')] = genQuery(p31=p31, desc=desc.replace('~', 'Hydra'), desclang=desclang)
    queries[desc.replace('~', 'Leo')] = genQuery(p31=p31, desc=desc.replace('~', 'Leo'), desclang=desclang)
    queries[desc.replace('~', 'Libra')] = genQuery(p31=p31, desc=desc.replace('~', 'Libra'), desclang=desclang)
    queries[desc.replace('~', 'Monoceros')] = genQuery(p31=p31, desc=desc.replace('~', 'Monoceros'), desclang=desclang)
    queries[desc.replace('~', 'Ophiuchus')] = genQuery(p31=p31, desc=desc.replace('~', 'Ophiuchus'), desclang=desclang)
    queries[desc.replace('~', 'Orion')] = genQuery(p31=p31, desc=desc.replace('~', 'Orion'), desclang=desclang)
    queries[desc.replace('~', 'Pegasus')] = genQuery(p31=p31, desc=desc.replace('~', 'Pegasus'), desclang=desclang)
    queries[desc.replace('~', 'Perseus')] = genQuery(p31=p31, desc=desc.replace('~', 'Perseus'), desclang=desclang)
    queries[desc.replace('~', 'Puppis')] = genQuery(p31=p31, desc=desc.replace('~', 'Puppis'), desclang=desclang)
    queries[desc.replace('~', 'Sagittarius')] = genQuery(p31=p31, desc=desc.replace('~', 'Sagittarius'), desclang=desclang)
    queries[desc.replace('~', 'Scorpius')] = genQuery(p31=p31, desc=desc.replace('~', 'Scorpius'), desclang=desclang)
    queries[desc.replace('~', 'Sextans')] = genQuery(p31=p31, desc=desc.replace('~', 'Sextans'), desclang=desclang)
    queries[desc.replace('~', 'Taurus')] = genQuery(p31=p31, desc=desc.replace('~', 'Taurus'), desclang=desclang)
    queries[desc.replace('~', 'Vela')] = genQuery(p31=p31, desc=desc.replace('~', 'Vela'), desclang=desclang)
    queries[desc.replace('~', 'Virgo')] = genQuery(p31=p31, desc=desc.replace('~', 'Virgo'), desclang=desclang)
    return queries

def genQueriesByCountry(p31='', desc='', desclang=''):
    queries = {}
    queries[desc.replace('~', 'Afghanistan')] = genQuery(p31=p31, desc=desc.replace('~', 'Afghanistan'), desclang=desclang)
    queries[desc.replace('~', 'Angola')] = genQuery(p31=p31, desc=desc.replace('~', 'Angola'), desclang=desclang)
    queries[desc.replace('~', 'Armenia')] = genQuery(p31=p31, desc=desc.replace('~', 'Armenia'), desclang=desclang)
    queries[desc.replace('~', 'Australia')] = genQuery(p31=p31, desc=desc.replace('~', 'Australia'), desclang=desclang)
    queries[desc.replace('~', 'Bangladesh')] = genQuery(p31=p31, desc=desc.replace('~', 'Bangladesh'), desclang=desclang)
    queries[desc.replace('~', 'Belarus')] = genQuery(p31=p31, desc=desc.replace('~', 'Belarus'), desclang=desclang)
    queries[desc.replace('~', 'Belgium')] = genQuery(p31=p31, desc=desc.replace('~', 'Belgium'), desclang=desclang)
    queries[desc.replace('~', 'Benin')] = genQuery(p31=p31, desc=desc.replace('~', 'Benin'), desclang=desclang)
    queries[desc.replace('~', 'Bolivia')] = genQuery(p31=p31, desc=desc.replace('~', 'Bolivia'), desclang=desclang)
    queries[desc.replace('~', 'Bosnia and Herzegovina')] = genQuery(p31=p31, desc=desc.replace('~', 'Bosnia and Herzegovina'), desclang=desclang)
    queries[desc.replace('~', 'Botswana')] = genQuery(p31=p31, desc=desc.replace('~', 'Botswana'), desclang=desclang)
    queries[desc.replace('~', 'Brazil')] = genQuery(p31=p31, desc=desc.replace('~', 'Brazil'), desclang=desclang)
    queries[desc.replace('~', 'Brunei')] = genQuery(p31=p31, desc=desc.replace('~', 'Brunei'), desclang=desclang)
    queries[desc.replace('~', 'Bulgaria')] = genQuery(p31=p31, desc=desc.replace('~', 'Bulgaria'), desclang=desclang)
    queries[desc.replace('~', 'Burkina Faso')] = genQuery(p31=p31, desc=desc.replace('~', 'Burkina Faso'), desclang=desclang)
    queries[desc.replace('~', 'Canada')] = genQuery(p31=p31, desc=desc.replace('~', 'Canada'), desclang=desclang)
    queries[desc.replace('~', 'Chile')] = genQuery(p31=p31, desc=desc.replace('~', 'Chile'), desclang=desclang)
    queries[desc.replace('~', 'Colombia')] = genQuery(p31=p31, desc=desc.replace('~', 'Colombia'), desclang=desclang)
    queries[desc.replace('~', 'Croatia')] = genQuery(p31=p31, desc=desc.replace('~', 'Croatia'), desclang=desclang)
    queries[desc.replace('~', 'Cuba')] = genQuery(p31=p31, desc=desc.replace('~', 'Cuba'), desclang=desclang)
    queries[desc.replace('~', 'Cyprus')] = genQuery(p31=p31, desc=desc.replace('~', 'Cyprus'), desclang=desclang)
    queries[desc.replace('~', 'Democratic Republic of the Congo')] = genQuery(p31=p31, desc=desc.replace('~', 'Democratic Republic of the Congo'), desclang=desclang)
    queries[desc.replace('~', 'Equatorial Guinea')] = genQuery(p31=p31, desc=desc.replace('~', 'Equatorial Guinea'), desclang=desclang)
    queries[desc.replace('~', 'Ethiopia')] = genQuery(p31=p31, desc=desc.replace('~', 'Ethiopia'), desclang=desclang)
    queries[desc.replace('~', 'Fiji')] = genQuery(p31=p31, desc=desc.replace('~', 'Fiji'), desclang=desclang)
    queries[desc.replace('~', 'Gabon')] = genQuery(p31=p31, desc=desc.replace('~', 'Gabon'), desclang=desclang)
    queries[desc.replace('~', 'Germany')] = genQuery(p31=p31, desc=desc.replace('~', 'Germany'), desclang=desclang)
    queries[desc.replace('~', 'Ghana')] = genQuery(p31=p31, desc=desc.replace('~', 'Ghana'), desclang=desclang)
    queries[desc.replace('~', 'Guyana')] = genQuery(p31=p31, desc=desc.replace('~', 'Guyana'), desclang=desclang)
    queries[desc.replace('~', 'India')] = genQuery(p31=p31, desc=desc.replace('~', 'India'), desclang=desclang)
    queries[desc.replace('~', 'Indonesia')] = genQuery(p31=p31, desc=desc.replace('~', 'Indonesia'), desclang=desclang)
    queries[desc.replace('~', 'Iran')] = genQuery(p31=p31, desc=desc.replace('~', 'Iran'), desclang=desclang)
    queries[desc.replace('~', 'Japan')] = genQuery(p31=p31, desc=desc.replace('~', 'Japan'), desclang=desclang)
    queries[desc.replace('~', 'Latvia')] = genQuery(p31=p31, desc=desc.replace('~', 'Latvia'), desclang=desclang)
    queries[desc.replace('~', 'Lebanon')] = genQuery(p31=p31, desc=desc.replace('~', 'Lebanon'), desclang=desclang)
    queries[desc.replace('~', 'Lithuania')] = genQuery(p31=p31, desc=desc.replace('~', 'Lithuania'), desclang=desclang)
    queries[desc.replace('~', 'Malaysia')] = genQuery(p31=p31, desc=desc.replace('~', 'Malaysia'), desclang=desclang)
    queries[desc.replace('~', 'Mexico')] = genQuery(p31=p31, desc=desc.replace('~', 'Mexico'), desclang=desclang)
    queries[desc.replace('~', 'Mozambique')] = genQuery(p31=p31, desc=desc.replace('~', 'Mozambique'), desclang=desclang)
    queries[desc.replace('~', 'New Zealand')] = genQuery(p31=p31, desc=desc.replace('~', 'New Zealand'), desclang=desclang)
    queries[desc.replace('~', 'North Korea')] = genQuery(p31=p31, desc=desc.replace('~', 'North Korea'), desclang=desclang)
    queries[desc.replace('~', 'Norway')] = genQuery(p31=p31, desc=desc.replace('~', 'Norway'), desclang=desclang)
    queries[desc.replace('~', 'Pakistan')] = genQuery(p31=p31, desc=desc.replace('~', 'Pakistan'), desclang=desclang)
    queries[desc.replace('~', "People's Republic of China")] = genQuery(p31=p31, desc=desc.replace('~', "People's Republic of China"), desclang=desclang)
    queries[desc.replace('~', 'Poland')] = genQuery(p31=p31, desc=desc.replace('~', 'Poland'), desclang=desclang)
    queries[desc.replace('~', 'Portugal')] = genQuery(p31=p31, desc=desc.replace('~', 'Portugal'), desclang=desclang)
    queries[desc.replace('~', 'Republic of the Congo')] = genQuery(p31=p31, desc=desc.replace('~', 'Republic of the Congo'), desclang=desclang)
    queries[desc.replace('~', 'Romania')] = genQuery(p31=p31, desc=desc.replace('~', 'Romania'), desclang=desclang)
    queries[desc.replace('~', 'Russia')] = genQuery(p31=p31, desc=desc.replace('~', 'Russia'), desclang=desclang)
    queries[desc.replace('~', 'Serbia')] = genQuery(p31=p31, desc=desc.replace('~', 'Serbia'), desclang=desclang)
    queries[desc.replace('~', 'Sierra Leone')] = genQuery(p31=p31, desc=desc.replace('~', 'Sierra Leone'), desclang=desclang)
    queries[desc.replace('~', 'Slovakia')] = genQuery(p31=p31, desc=desc.replace('~', 'Slovakia'), desclang=desclang)
    queries[desc.replace('~', 'South Africa')] = genQuery(p31=p31, desc=desc.replace('~', 'South Africa'), desclang=desclang)
    queries[desc.replace('~', 'South Sudan')] = genQuery(p31=p31, desc=desc.replace('~', 'South Sudan'), desclang=desclang)
    queries[desc.replace('~', 'Spain')] = genQuery(p31=p31, desc=desc.replace('~', 'Spain'), desclang=desclang)
    queries[desc.replace('~', 'Sweden')] = genQuery(p31=p31, desc=desc.replace('~', 'Sweden'), desclang=desclang)
    queries[desc.replace('~', 'Taiwan')] = genQuery(p31=p31, desc=desc.replace('~', 'Taiwan'), desclang=desclang)
    queries[desc.replace('~', 'Turkey')] = genQuery(p31=p31, desc=desc.replace('~', 'Turkey'), desclang=desclang)
    queries[desc.replace('~', 'the Central African Republic')] = genQuery(p31=p31, desc=desc.replace('~', 'the Central African Republic'), desclang=desclang)
    queries[desc.replace('~', 'the Philippines')] = genQuery(p31=p31, desc=desc.replace('~', 'the Philippines'), desclang=desclang)
    queries[desc.replace('~', 'the United Kingdom')] = genQuery(p31=p31, desc=desc.replace('~', 'the United Kingdom'), desclang=desclang)
    queries[desc.replace('~', 'United States of America')] = genQuery(p31=p31, desc=desc.replace('~', 'United States of America'), desclang=desclang)
    queries[desc.replace('~', 'Ukraine')] = genQuery(p31=p31, desc=desc.replace('~', 'Ukraine'), desclang=desclang)
    queries[desc.replace('~', 'Uganda')] = genQuery(p31=p31, desc=desc.replace('~', 'Uganda'), desclang=desclang)
    queries[desc.replace('~', 'Uruguay')] = genQuery(p31=p31, desc=desc.replace('~', 'Uruguay'), desclang=desclang)
    queries[desc.replace('~', 'Venezuela')] = genQuery(p31=p31, desc=desc.replace('~', 'Venezuela'), desclang=desclang)
    queries[desc.replace('~', 'Vietnam')] = genQuery(p31=p31, desc=desc.replace('~', 'Vietnam'), desclang=desclang)
    queries[desc.replace('~', 'Zambia')] = genQuery(p31=p31, desc=desc.replace('~', 'Zambia'), desclang=desclang)
    return queries

def genTranslationsByConstellationCore(desc='', desclang=''):
    translations = {
        'astronomical galaxy in the constellation ~': { 
            'en': 'astronomical galaxy in the constellation ~', 
            'es': 'galaxia de la constelación ~', 
        }, 
        'astronomical radio source in the constellation ~': { 
            'en': 'astronomical radio source in the constellation ~', 
            'es': 'radiofuente de la constelación ~', 
        }, 
        'astrophysical X-ray source in the constellation ~': { 
            'en': 'astrophysical X-ray source in the constellation ~', 
            'es': 'fuente de rayos X de la constelación ~', 
        }, 
        'eclipsing binary star in the constellation ~': { 
            'en': 'eclipsing binary star in the constellation ~', 
            'es': 'binaria eclipsante de la constelación ~', 
        }, 
        'galaxy in the constellation ~': { 
            'en': 'galaxy in the constellation ~', 
            'es': 'galaxia de la constelación ~', 
        }, 
        'globular cluster in the constellation ~': { 
            'en': 'globular cluster in the constellation ~', 
            'es': 'cúmulo globular de la constelación ~', 
        }, 
        'high proper-motion star in the constellation ~': { 
            'en': 'high proper-motion star in the constellation ~', 
            'es': 'estrella con movimiento propio alto de la constelación ~', 
        }, 
        'nova in the constellation ~': { 
            'en': 'nova in the constellation ~', 
            'es': 'nova de la constelación ~', 
        }, 
        'pulsar in the constellation ~': { 
            'en': 'pulsar in the constellation ~', 
            'es': 'pulsar de la constelación ~', 
        }, 
        'quasar in the constellation ~': { 
            'en': 'quasar in the constellation ~', 
            'es': 'quasar de la constelación ~', 
        }, 
        'radio source in the constellation ~': { 
            'en': 'radio source in the constellation ~', 
            'es': 'radiofuente de la constelación ~', 
        }, 
        'star in the constellation ~': { 
            'en': 'star in the constellation ~', 
            'es': 'estrella de la constelación ~', 
        }, 
        'star cluster in the constellation ~': { 
            'en': 'star cluster in the constellation ~', 
            'es': 'cúmulo estelar de la constelación ~', 
        }, 
        'supernova in the constellation ~': { 
            'en': 'supernova in the constellation ~', 
            'es': 'supernova de la constelación ~', 
        }, 
    }
    return translations[desc][desclang]

def genTranslationsByCountryCore(desc='', desclang=''):
    translations = {
        'bay in ~': { 
            'en': 'bay in ~', 
            'es': 'bahía de ~', 
        }, 
        'bight in ~': { 
            'en': 'bight in ~', 
            'es': 'ancón de ~', 
        }, 
        'cape in ~': { 
            'en': 'cape in ~', 
            'es': 'cabo de ~', 
        }, 
        'cave in ~': { 
            'en': 'cave in ~', 
            'es': 'cueva de ~', 
        }, 
        'dune in ~': { 
            'en': 'dune in ~', 
            'es': 'duna de ~', 
        }, 
        'glacier in ~': { 
            'en': 'glacier in ~', 
            'es': 'glaciar de ~', 
        }, 
        'hill in ~': { 
            'en': 'hill in ~', 
            'es': 'colina de ~', 
        }, 
        'island in ~': { 
            'en': 'island in ~', 
            'es': 'isla de ~', 
        }, 
        'lagoon in ~': { 
            'en': 'lagoon in ~', 
            'es': 'laguna de ~', 
        }, 
        'lake in ~': { 
            'en': 'lake in ~', 
            'es': 'lago de ~', 
        }, 
        'mine in ~': { 
            'en': 'mine in ~', 
            'es': 'mina de ~', 
        }, 
        'mountain in ~': { 
            'en': 'mountain in ~', 
            'es': 'montaña de ~', 
        }, 
        'plain in ~': { 
            'en': 'plain in ~', 
            'es': 'llanura de ~', 
        }, 
        'reef in ~': { 
            'en': 'reef in ~', 
            'es': 'arrecife de ~', 
        }, 
        'reservoir in ~': { 
            'en': 'reservoir in ~', 
            'es': 'embalse de ~', 
        }, 
        'river in ~': { 
            'en': 'river in ~', 
            'es': 'río de ~', 
        }, 
        'road in ~': { 
            'en': 'road in ~', 
            'es': 'carretera de ~', 
        }, 
        'spring in ~': { 
            'en': 'spring in ~', 
            'es': 'manantial de ~', 
        }, 
        'stream in ~': { 
            'en': 'stream in ~', 
            'es': 'arroyo de ~', 
        }, 
        'swamp in ~': { 
            'en': 'swamp in ~', 
            'es': 'pantano de ~', 
        }, 
        'valley in ~': { 
            'en': 'valley in ~', 
            'es': 'valle de ~', 
        }, 
        'watercourse in ~': { 
            'en': 'watercourse in ~', 
            'es': 'curso de agua de ~', 
        }, 
    }
    return translations[desc][desclang]

def genTranslationsByConstellation(desc=''):
    translations = {}
    translations[desc.replace('~', 'Andromeda')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Andromeda'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Andrómeda'), 
    }
    translations[desc.replace('~', 'Aquarius')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Aquarius'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Acuario'), 
    }
    translations[desc.replace('~', 'Aquila')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Aquila'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'del Águila'), 
    }
    translations[desc.replace('~', 'Aries')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Aries'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Aries'), 
    }
    translations[desc.replace('~', 'Auriga')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Auriga'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Auriga'), 
    }
    translations[desc.replace('~', 'Camelopardalis')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Camelopardalis'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Camelopardalis'), 
    }
    translations[desc.replace('~', 'Cancer')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Cancer'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Cáncer'), 
    }
    translations[desc.replace('~', 'Capricornus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Capricornus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Capricornio'), 
    }
    translations[desc.replace('~', 'Carina')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Carina'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Carina'), 
    }
    translations[desc.replace('~', 'Cassiopeia')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Cassiopeia'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Casiopea'), 
    }
    translations[desc.replace('~', 'Cepheus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Cepheus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Cefeo'), 
    }
    translations[desc.replace('~', 'Centaurus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Centaurus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'del Centauro'), 
    }
    translations[desc.replace('~', 'Cygnus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Cygnus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'del Cisne'), 
    }
    translations[desc.replace('~', 'Draco')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Draco'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Draco'), 
    }
    translations[desc.replace('~', 'Gemini')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Gemini'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Géminis'), 
    }
    translations[desc.replace('~', 'Hercules')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Hercules'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Hércules'), 
    }
    translations[desc.replace('~', 'Hydra')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Hydra'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de la Hidra'), 
    }
    translations[desc.replace('~', 'Leo')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Leo'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Leo'), 
    }
    translations[desc.replace('~', 'Libra')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Libra'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Libra'), 
    }
    translations[desc.replace('~', 'Monoceros')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Monoceros'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Monoceros'), 
    }
    translations[desc.replace('~', 'Ophiuchus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Ophiuchus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Ofiuco'), 
    }
    translations[desc.replace('~', 'Orion')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Orion'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Orión'), 
    }
    translations[desc.replace('~', 'Pegasus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Pegasus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Pegaso'), 
    }
    translations[desc.replace('~', 'Perseus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Perseus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Perseo'), 
    }
    translations[desc.replace('~', 'Puppis')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Puppis'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de la Popa'), 
    }
    translations[desc.replace('~', 'Sagittarius')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Sagittarius'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Sagitario'), 
    }
    translations[desc.replace('~', 'Scorpius')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Scorpius'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Escorpio'), 
    }
    translations[desc.replace('~', 'Sextans')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Sextans'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'del Sextante'), 
    }
    translations[desc.replace('~', 'Taurus')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Taurus'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Tauro'), 
    }
    translations[desc.replace('~', 'Vela')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Vela'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Vela'), 
    }
    translations[desc.replace('~', 'Virgo')] = {
        'en': genTranslationsByConstellationCore(desc=desc, desclang='en').replace('~', 'Virgo'), 
        'es': genTranslationsByConstellationCore(desc=desc, desclang='es').replace('~', 'de Virgo'), 
    }
    return translations

def genTranslationsByCountry(desc=''):
    translations = {}
    translations[desc.replace('~', 'Afghanistan')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Afghanistan'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Afganistán'), 
    }
    translations[desc.replace('~', 'Angola')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Angola'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Angola'), 
    }
    translations[desc.replace('~', 'Armenia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Armenia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Armenia'), 
    }
    translations[desc.replace('~', 'Australia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Australia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Australia'), 
    }
    translations[desc.replace('~', 'Bangladesh')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Bangladesh'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Bangladesh'), 
    }
    translations[desc.replace('~', 'Belarus')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Belarus'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Bielorrusia'), 
    }
    translations[desc.replace('~', 'Belgium')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Belgium'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Bélgica'), 
    }
    translations[desc.replace('~', 'Benin')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Benin'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Benín'), 
    }
    translations[desc.replace('~', 'Bolivia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Bolivia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Bolivia'), 
    }
    translations[desc.replace('~', 'Bosnia and Herzegovina')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Bosnia and Herzegovina'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Bosnia y Herzegovina'), 
    }
    translations[desc.replace('~', 'Botswana')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Botswana'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Botsuana'), 
    }
    translations[desc.replace('~', 'Brazil')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Brazil'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Brasil'), 
    }
    translations[desc.replace('~', 'Brunei')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Brunei'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Brunéi'), 
    }
    translations[desc.replace('~', 'Bulgaria')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Bulgaria'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Bulgaria'), 
    }
    translations[desc.replace('~', 'Burkina Faso')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Burkina Faso'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Burkina Faso'), 
    }
    translations[desc.replace('~', 'Canada')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Canada'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Canadá'), 
    }
    translations[desc.replace('~', 'Chile')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Chile'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Chile'), 
    }
    translations[desc.replace('~', 'Colombia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Colombia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Colombia'), 
    }
    translations[desc.replace('~', 'Croatia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Croatia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Croacia'), 
    }
    translations[desc.replace('~', 'Cuba')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Cuba'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Cuba'), 
    }
    translations[desc.replace('~', 'Cyprus')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Cyprus'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Chipre'), 
    }
    translations[desc.replace('~', 'Democratic Republic of the Congo')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Democratic Republic of the Congo'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'República Democrática del Congo'), 
    }
    translations[desc.replace('~', 'Equatorial Guinea')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Equatorial Guinea'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Guinea Ecuatorial'), 
    }
    translations[desc.replace('~', 'Ethiopia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Ethiopia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Etiopía'), 
    }
    translations[desc.replace('~', 'Fiji')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Fiji'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Fiji'), 
    }
    translations[desc.replace('~', 'Gabon')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Gabon'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Gabón'), 
    }
    translations[desc.replace('~', 'Germany')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Germany'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Alemania'), 
    }
    translations[desc.replace('~', 'Ghana')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Ghana'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Ghana'), 
    }
    translations[desc.replace('~', 'Guyana')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Guyana'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Guyana'), 
    }
    translations[desc.replace('~', 'India')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'India'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'la India'), 
    }
    translations[desc.replace('~', 'Indonesia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Indonesia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Indonesia'), 
    }
    translations[desc.replace('~', 'Iran')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Iran'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Irán'), 
    }
    translations[desc.replace('~', 'Japan')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Japan'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Japón'), 
    }
    translations[desc.replace('~', 'Latvia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Latvia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Letonia'), 
    }
    translations[desc.replace('~', 'Lebanon')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Lebanon'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Líbano'), 
    }
    translations[desc.replace('~', 'Lithuania')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Lithuania'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Lituania'), 
    }
    translations[desc.replace('~', 'Malaysia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Malaysia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Malasia'), 
    }
    translations[desc.replace('~', 'Mexico')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Mexico'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'México'), 
    }
    translations[desc.replace('~', 'Mozambique')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Mozambique'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Mozambique'), 
    }
    translations[desc.replace('~', 'New Zealand')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'New Zealand'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Nueva Zelanda'), 
    }
    translations[desc.replace('~', 'North Korea')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'North Korea'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Corea del Norte'), 
    }
    translations[desc.replace('~', 'Norway')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Norway'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Noruega'), 
    }
    translations[desc.replace('~', 'Pakistan')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Pakistan'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Pakistán'), 
    }
    translations[desc.replace('~', "People's Republic of China")] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', "People's Republic of China"), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'la República Popular China'), 
    }
    translations[desc.replace('~', 'Poland')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Poland'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Polonia'), 
    }
    translations[desc.replace('~', 'Portugal')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Portugal'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Portugal'), 
    }
    translations[desc.replace('~', 'Republic of the Congo')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Republic of the Congo'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'República del Congo'), 
    }
    translations[desc.replace('~', 'Romania')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Romania'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Rumanía'), 
    }
    translations[desc.replace('~', 'Russia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Russia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Rusia'), 
    }
    translations[desc.replace('~', 'Serbia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Serbia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Serbia'), 
    }
    translations[desc.replace('~', 'Sierra Leone')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Sierra Leone'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Sierra Leona'), 
    }
    translations[desc.replace('~', 'Slovakia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Slovakia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Eslovaquia'), 
    }
    translations[desc.replace('~', 'South Africa')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'South Africa'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Sudáfrica'), 
    }
    translations[desc.replace('~', 'South Sudan')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'South Sudan'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Sudán del Sur'), 
    }
    translations[desc.replace('~', 'Spain')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Spain'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'España'), 
    }
    translations[desc.replace('~', 'Sweden')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Sweden'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Suecia'), 
    }
    translations[desc.replace('~', 'Taiwan')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Taiwan'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Taiwán'), 
    }
    translations[desc.replace('~', 'Turkey')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Turkey'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Turquía'), 
    }
    translations[desc.replace('~', 'the Central African Republic')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'the Central African Republic'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'República Centroafricana'), 
    }
    translations[desc.replace('~', 'the Philippines')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'the Philippines'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Filipinas'), 
    }
    translations[desc.replace('~', 'the United Kingdom')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'the United Kingdom'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Reino Unido'), 
    }
    translations[desc.replace('~', 'United States of America')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'United States of America'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Estados Unidos'), 
    }
    translations[desc.replace('~', 'Ukraine')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Ukraine'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Ucrania'), 
    }
    translations[desc.replace('~', 'Uganda')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Uganda'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Uganda'), 
    }
    translations[desc.replace('~', 'Uruguay')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Uruguay'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Uruguay'), 
    }
    translations[desc.replace('~', 'Venezuela')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Venezuela'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Venezuela'), 
    }
    translations[desc.replace('~', 'Vietnam')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Vietnam'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Vietnam'), 
    }
    translations[desc.replace('~', 'Zambia')] = {
        'en': genTranslationsByCountryCore(desc=desc, desclang='en').replace('~', 'Zambia'), 
        'es': genTranslationsByCountryCore(desc=desc, desclang='es').replace('~', 'Zambia'), 
    }
    return translations

def main():
    fixthiswhenfound = { #fix (overwrite) old, wrong or poor translations
        'chemical compound': {
            'nl': ['chemische stof'], #https://www.wikidata.org/w/index.php?title=Q27165025&type=revision&diff=486050731&oldid=466952438
        },
        'family name': {
            'sq': ['mbiemri'], #because "mbiemri" = "the family name"
        },
        'galaxy': {
            'es': ['galaxy'], 
        },
        'species of insect': {
            'sq': ['specie e insekteve'], #https://github.com/emijrp/wikidata/pull/47
        },
        'television series': {
            'es': ['television series'], #https://www.wikidata.org/w/index.php?title=Q1043980&oldid=837349507
        },
        'village in China': {
            'bn': ['চীনের গ্রাম'], #https://www.wikidata.org/w/index.php?title=User_talk:Emijrp&diff=prev&oldid=510797889
            'fi': ['kiinalainen kylä'], #https://www.wikidata.org/w/index.php?title=User_talk:Emijrp&diff=468197059&oldid=463649230
            'id': ['desa di Cina'],
        }, 
        'Wikimedia category': {
            'arz': ['ويكيبيديا:تصنيف'],
            'be': ['катэгарызацыя'], #https://www.wikidata.org/w/index.php?title=User:Emijrp/Wikimedia_project_pages_matrix&diff=next&oldid=500158307
            'be-tarask': ['Катэгорыя', 'Вікіпэдыя:Катэгорыя'],#https://www.wikidata.org/w/index.php?title=User:Emijrp/Wikimedia_project_pages_matrix&diff=next&oldid=500158307
            'es': ['categoría de Wikipedia'],
            'mk': ['категорија на Википедија'],
            'sl': ['kategorija Wikimedije'], #https://www.wikidata.org/w/index.php?title=User_talk:Emijrp&diff=prev&oldid=1838633138
            'uk': ['Категорії', 'категорія в проекті Вікімедіа'], #https://www.wikidata.org/w/index.php?title=User_talk%3AEmijrp&type=revision&diff=527336622&oldid=525302741
        }, 
        'Wikimedia disambiguation page': {
            'bn': ['উইকিমিডিয়া দ্ব্যর্থতা নিরসন পাতা'],
            'el': ['σελίδα αποσαφήνισης'],#https://www.wikidata.org/w/index.php?title=Q29449981&diff=prev&oldid=567203989
            'es': ['desambiguación de Wikipedia'], 
            'fy': ['Betsjuttingsside'], #https://www.wikidata.org/w/index.php?title=User:Emijrp/Wikimedia_project_pages_matrix&curid=30597789&diff=499110338&oldid=498167178
            'id': ['halaman disambiguasi'], 
            'tg': ['саҳифаи ибҳомзудоии Викимаълумот'], #https://www.wikidata.org/w/index.php?title=Topic:Ts4qkooukddjcuq9&topic_showPostId=ts4rax4ro9brqqgj#flow-post-ts4rax4ro9brqqgj
            'tt': ['Википедия:Күп мәгънәле мәкаләләр'],
            'uk': ['сторінка значень в проекті Вікімедіа'],
        }, 
        'Wikimedia list article': {
            'et': ['Vikipeedia:Loend', 'Vikipeedia loend'], #https://www.wikidata.org/w/index.php?title=Q13406463&diff=next&oldid=588159017
            'id': ['Wikipedia:Daftar'], #https://www.wikidata.org/w/index.php?title=Q13406463&diff=745905758&oldid=745029653
            'tg': ['саҳифае, ки аз рӯйхат иборат аст'], #https://www.wikidata.org/w/index.php?title=Q13406463&diff=prev&oldid=498154491
            'uk': ['сторінка-список в проекті Вікімедіа'], #https://www.wikidata.org/w/index.php?title=Q13406463&diff=617531932&oldid=606446211
        }, 
        'Wikimedia template': {
            'be': ['шаблон Вікіпедыя'],
            'be-tarask': ['шаблён Вікіпэдыя'],
            'eu': ['Wikimediarako txantiloia'], #https://www.wikidata.org/w/index.php?title=Q11266439&type=revision&diff=469566880&oldid=469541605
            'id': ['templat Wikipedia'],
            'nb': ['Wikipedia mal'],
            'nn': ['Wikipedia mal'],
            'pl': ['szablon Wikipedii'],
            'sq': ['Wikipedia stampa'],
            'sv': ['Wikipedia mall'],
            'sw': ['kigezo Wikipedia'],
            'tg': ['Шаблони Викимедиа', 'шаблон Википедиа'], #https://www.wikidata.org/w/index.php?title=Q11266439&diff=prev&oldid=498153879
            'tr': ['şablon Vikipedi'],
            'uk': ['шаблон Вікіпедії', 'шаблон проекту Вікімедіа'],
            'yo': ['àdàkọ Wikipedia'],
            'vi': ['bản mẫu Wikipedia'],
        },
        'Wikinews article': {
            'nl': ['Wikinews-artikel'], 
        },
    }
    translations = {
        'asteroid': { #Q3863
            'af': 'asteroïde',
            'an': 'asteroide',
            'ar': 'كويكب',
            'arz': 'كويكب',
            'as': 'গ্ৰহাণু',
            'ast': 'asteroide',
            'az': 'asteroid',
            'azb': 'گزگنچه',
            'ba': 'Астероид',
            'bar': 'Asteroid',
            'bcl': 'Asteroyd',
            'be': 'астэроід',
            'be-tarask': 'астэроід',
            'bg': 'астероид',
            'bho': 'एस्टेरॉइड्स',
            'bjn': 'asteruid',
            'bn': 'গ্রহাণু',
            'br': 'asteroidenn',
            'bs': 'Asteroid',
            'ca': 'asteroide',
            'ce': 'Астероид',
            'chr': 'ᏅᏯ ᏧᎳᎬᎭᎸᏓ',
            'ckb': 'گەڕەستێرۆچکە',
            'crh': 'asteroid',
            'cs': 'asteroid',
            'cu': 'Астєроидъ',
            'cv': 'астероид',
            'cy': 'asteroid',
            'da': 'asteroide',
            'de': 'Asteroid',
            'el': 'αστεροειδής',
            'eml': 'Asteròid',
            'en': 'asteroid',
            'en-ca': 'asteroid',
            'en-gb': 'asteroid',
            'eo': 'asteroido',
            'es': 'asteroide',
            'et': 'asteroid',
            'eu': 'asteroide',
            'fa': 'سیارک',
            'fi': 'asteroidi',
            'fj': 'Asteroid',
            'fr': 'astéroïde',
            'fy': 'asteroïde',
            'ga': 'astaróideach',
            'gd': 'astaroid',
            'gl': 'asteroide',
            'gn': 'Mbyjaveve',
            'gsw': 'Asteroid',
            'gv': 'roltageagh',
            'he': 'אסטרואיד',
            'hi': 'क्षुद्रग्रह',
            'hif': 'Chhota tara',
            'hr': 'asteroidi',
            'hsb': 'Asteroid',
            'ht': 'astewoyid',
            'hu': 'kisbolygó',
            'hy': 'աստերոիդ',
            'ia': 'asteroide',
            'id': 'asteroid',
            'ilo': 'asteroid',
            'io': 'asteroido',
            'is': 'Smástirni',
            'it': 'asteroide',
            'ja': '小惑星',
            'jam': 'Astaraid',
            'jbo': 'cmaplini',
            'jv': 'asteroid',
            'ka': 'მცირე ცთომილები',
            'kaa': 'Asteroid',
            'kab': 'Azungur',
            'kk': 'астероид',
            'ko': '소행성',
            'krc': 'Астероид',
            'ksh': 'Asteroid',
            'ku': 'asteroîd',
            'ky': 'астероид',
            'la': 'asteroides',
            'lb': 'Asteroid',
            'lez': 'астероид',
            'lld': 'Asteroid',
            'lmo': 'Asteroide',
            'lo': 'ດາວເຄາະນ້ອຍ',
            'lt': 'Asteroidas',
            'lv': 'asteroīds',
            'lzh': '小行星',
            'min': 'asteroid',
            'mk': 'астероид',
            'ml': 'ഛിന്നഗ്രഹം',
            'mr': 'लघुग्रह',
            'ms': 'asteroid',
            'mt': 'asterojde',
            'mwl': 'asteróide',
            'my': 'ဥက္ကာပျံ',
            'nan': 'sió-he̍k-chheⁿ',
            'nap': 'asteroide',
            'nb': 'asteroide',
            'nds': 'Asteroid',
            'nl': 'asteroïde',
            'nn': 'asteroide',
            'oc': 'asteroïde',
            'or': 'ଗ୍ରହାଣୁ',
            'os': 'Астероид',
            'pa': 'ਨਿੱਕਾ ਗ੍ਰਹਿ',
            'pam': 'asteroid',
            'pms': 'Asteròid',
            'pnb': 'تارے ورگا',
            'pt': 'asteroide',
            'pt-br': 'asteroide',
            'ro': 'Asteroid',
            'ru': 'астероид',
            'rue': 'астероід',
            'sah': 'Астероид',
            'scn': 'astiròidi',
            'sco': 'asteroid',
            'sgs': 'Asteruoids',
            'sh': 'asteroid',
            'si': 'ග්‍රහක',
            'sk': 'asteroid',
            'sl': 'asteroid',
            'sq': 'asteroid',
            'sr': 'астероид',
            'su': 'Astéroid',
            'sv': 'asteroid',
            'sw': 'asteroidi',
            'ta': 'சிறுகோள்',
            'tg': 'Сайёрак',
            'th': 'ดาวเคราะห์น้อย',
            'tk': 'Asteroid',
            'tl': 'asteroyd',
            'tr': 'Asteroit',
            'tt': 'астероид',
            'tt-cyrl': 'астероид',
            'tyv': 'Астероид',
            'uk': 'астероїд',
            'ur': 'نجمانی',
            'vi': 'tiểu hành tinh',
            'vls': 'Asteroïde',
            'war': 'Asteroyd',
            'wuu': '小行星',
            'xmf': 'ასტეროიდი',
            'yi': 'אסטערויד',
            'yue': '小行星',
            'zh': '小行星',
            'zh-cn': '小行星',
            'zh-hans': '小行星',
            'zh-hant': '小行星',
            'zh-hk': '小行星',
            'zh-mo': '小行星',
            'zh-my': '小行星',
            'zh-sg': '小行星',
        }, 
        'chemical compound': { #Q11173
            'af': 'chemiese verbinding', 
            'an': 'compuesto quimico', 
            'ar': 'مركب كيميائي',
            'ast': 'compuestu químicu',
            'be': 'хімічнае злучэнне',
            'be-tarask': 'хімічнае злучэньне',
            'bg': 'химично съединение',
            'bn': 'রাসায়নিক যৌগ',
            'br': 'kediad kimiek',
            'ca': 'compost químic',
            'cs': 'chemická sloučenina',
            'cy': 'cyfansoddyn cemegol',
            'da': 'kemisk forbindelse',
            'de': 'chemische Verbindung',
            'de-ch': 'chemische Verbindung',
            'el': 'χημική ένωση',
            'en': 'chemical compound',
            'en-ca': 'chemical compound',
            'en-gb': 'chemical compound',
            'eo': 'kemia kombinaĵo',
            'es': 'compuesto químico',
            'et': 'keemiline ühend',
            'eu': 'konposatu kimiko',
            'fr': 'composé chimique',
            'fy': 'gemyske ferbining',
            'gcr': 'Kompozé chimik',
            'gl': 'composto químico',
            'he': 'תרכובת',
            'hy': 'քիմիական միացություն',
            'ia': 'composito chimic',
            'id': 'senyawa kimia',
            'io': 'kemiala kompozajo',
            'it': 'composto chimico',
            'la': 'compositum chemicum',
            'lb': 'chemesch Verbindung',
            'lv': 'ķīmisks savienojums',
            'mk': 'хемиско соединение',
            'nb': 'kjemisk forbindelse',
            'nl': 'chemische verbinding',
            'nn': 'kjemisk sambinding',
            'oc': 'component quimic',
            'pl': 'związek chemiczny',
            'pt': 'composto químico',
            'pt-br': 'composto químico',
            'ro': 'compus chimic',
            'ru': 'химическое соединение',
            'scn': 'cumpostu chìmicu',
            'sk': 'chemická zlúčenina',
            'sq': 'komponim kimik',
            'uk': 'хімічна сполука',
            'vec': 'conposto chìmego',
            'yue': '化合物',
            'zh': '化合物',
            'zh-cn': '化合物',
            'zh-hans': '化合物',
            'zh-hant': '化合物',
            'zh-hk': '化合物',
            'zh-mo': '化合物',
            'zh-sg': '化合物',
            'zh-tw': '化合物',
        }, 
        'clinical trial': { 
            'en': 'clinical trial',
            'es': 'ensayo clínico',
        }, 
        'date in Gregorian calendar': { 
            'en': 'date in Gregorian calendar',
            'es': 'fecha del calendario gregoriano',
        }, 
        'douar in Morocco': { #Q23925393
            'de': 'douar in Marokko',
            'en': 'douar in Morocco',
            'es': 'douar de Marruecos',
            'fr': 'douar marocain',
            'nl': 'douar in Marokko',
        }, 
        'encyclopedic article': { #Q17329259
            'ar': 'مقالة موسوعية',
            'ast': 'artículu enciclopédicu',
            'be': 'энцыклапедычны артыкул',
            'bn': 'বিশ্বকোষীয় নিবন্ধ',
            'ca': 'article enciclopèdic',
            'cs': 'encyklopedický článek',
            'da': 'encyklopædiartikel',
            'de': 'enzyklopädischer Artikel',
            'el': 'λήμμα εγκυκλοπαίδειας',
            'en': 'encyclopedic article',
            'eo': 'enciklopedia artikolo',
            'es': 'artículo de enciclopedia',
            'et': 'entsüklopeedia artikkel',
            'eu': 'entziklopedia artikulu',
            'fi': 'tietosanakirja-artikkeli',
            'fr': "article d'encyclopédie",
            'frc': "article d'encyclopédie",
            'fy': 'ensyklopedysk artikel',
            'gl': 'artigo enciclopédico',
            'he': 'ערך אנציקלופדי',
            'hy': 'հանրագիտարանային հոդված',
            'hu': 'enciklopédia-szócikk',
            'id': 'artikel ensiklopedia',
            'io': 'enciklopediala artiklo',
            'it': 'voce enciclopedica',
            'ja': '百科事典の記事',
            'ka': 'ენციკლოპედიური სტატია',
            'lt': 'enciklopedinis straipsnis',
            'lv': 'enciklopēdisks raksts',
            'mk': 'енциклопедиска статија',
            'nb': 'encyklopedisk artikkel',
            'nl': 'encyclopedisch artikel',
            'nn': 'ensyklopedisk artikkel',
            'pl': 'artykuł w encyklopedii',
            'pt-br': 'artigo enciclopédico',
            'ro': 'articol enciclopedic',
            'ru': 'энциклопедическая статья',
            'sl': 'enciklopedični članek',
            'sq': 'artikull enciklopedik',
            'sr': 'енциклопедијски чланак',
            'sr-ec': 'енциклопедијски чланак',
            'sr-el': 'enciklopedijski članak',
            'sv': 'encyklopedisk artikel',
            'tg': 'мақолаи энсиклопедӣ',
            'tg-cyrl': 'мақолаи энсиклопедӣ',
            'tt': 'энциклопедик мәкалә',
            'tt-cyrl': 'энциклопедик мәкалә',
            'uk': 'енциклопедична стаття',
            'zh': '条目',
            'zh-hans': '百科全书条目',
        }, 
        'entry in Dictionary of National Biography': {
            'en': 'entry in Dictionary of National Biography',
            'es': 'entrada del Dictionary of National Biography',
        }, 
        'extrasolar planet': {
            'af': 'eksoplaneet',
            'ast': 'planeta estrasolar',
            'az': 'ekzoplanet',
            'be': 'Экзапланета',
            'be-tarask': 'Экзаплянэта',
            'bg': 'Екзопланета',
            'bn': 'বহির্গ্রহ',
            'br': 'Ezplanedenn',
            'bs': 'vansolarna planeta',
            'ca': 'planeta extrasolar',
            'cs': 'exoplaneta',
            'cv': 'Экзопланета',
            'de': 'extrasolarer Planet',
            'en': 'extrasolar planet',
            'en-ca': 'extrasolar planet',
            'en-gb': 'extrasolar planet',
            'es': 'planeta extrasolar',
            'fi': 'eksoplaneetta',
            'fr': 'exoplanète',
            'gl': 'planeta extrasolar',
            'it': 'pianeta extrasolare',
            'nb': 'eksoplanet',
            'nl': 'exoplaneet',
            'pt': 'exoplaneta',
            'pt-br': 'exoplaneta',
            'wuu': '太阳系外行星',
            'yue': '太陽系外行星',
            'zh': '太陽系外行星',
        },
        #more families https://query.wikidata.org/#SELECT %3FitemDescription (COUNT(%3Fitem) AS %3Fcount)%0AWHERE {%0A%09%3Fitem wdt%3AP31 wd%3AQ16521.%0A %3Fitem wdt%3AP105 wd%3AQ35409.%0A %23%3Fitem schema%3Adescription "family of insects"%40en.%0A OPTIONAL { %3Fitem schema%3Adescription %3FitemDescription. FILTER(LANG(%3FitemDescription) %3D "en"). }%0A%09FILTER (BOUND(%3FitemDescription))%0A}%0AGROUP BY %3FitemDescription%0AORDER BY DESC(%3Fcount)
        'family of crustaceans': {
            'en': 'family of crustaceans',
            'es': 'familia de crustáceos',
            'et': 'koorikloomade sugukond',
            'he': 'משפחה של סרטנאים',
            'io': 'familio di krustacei',
            'ro': 'familie de crustacee',
        }, 
        'family of insects': {
            'bn': 'কীটপতঙ্গের পরিবার',
            'en': 'family of insects',
            'es': 'familia de insectos',
            'et': 'putukate sugukond',
            'fr': 'famille d\'insectes',
            'he': 'משפחה של חרקים',
            'io': 'familio di insekti',
            'ro': 'familie de insecte',
        }, 
        'family of molluscs': {
            'bn': 'মলাস্কার পরিবার',
            'en': 'family of molluscs',
            'es': 'familia de moluscos',
            'et': 'limuste sugukond',
            'he': 'משפחה של רכיכות',
            'io': 'familio di moluski',
            'ro': 'familie de moluște',
        }, 
        'family of plants': {
            'bn': 'উদ্ভিদের পরিবার',
            'cy': 'teulu o blanhigion',
            'en': 'family of plants',
            'es': 'familia de plantas',
            'et': 'taimesugukond',
            'he': 'משפחה של צמחים',
            'io': 'familio di planti',
            'ro': 'familie de plante',
        }, 
        'galaxy': {
            'ast': 'galaxa',
            'ca': 'galàxia',
            'en': 'galaxia',
            'en-ca': 'galaxy',
            'en-gb': 'galaxy',
            'en-us': 'galaxy',
            'eo': 'galaksio',
            'es': 'galaxia',
            'fr': 'galaxie',
            'gl': 'galaxia',
            'pt': 'galáxia',
        },
        'genus of algae': {
            'ar': 'جنس من الطحالب',
            'bn': 'শৈবালের গণ',
            'en': 'genus of algae',
            'es': 'género de algas',
            'et': 'vetikaperekond',
            'gl': 'xénero de algas',
            'he': 'סוג של אצה',
            'id': 'genus alga',
            'io': 'genero di algi',
            'nb': 'algeslekt',
            'nn': 'algeslekt',
            'ro': 'gen de alge',
            'sq': 'gjini e algave',
        }, 
        'genus of amphibians': {
            'ar': 'جنس من البرمائيات',
            'bn': 'উভচর প্রাণীর গণ',
            'en': 'genus of amphibians',
            'es': 'género de anfibios',
            'et': 'kahepaiksete perekond',
            'fr': "genre d'amphibiens",
            'he': 'סוג של דו־חיים',
            'id': 'genus amfibi',
            'io': 'genero di amfibii',
            'it': 'genere di anfibi',
            'nb': 'amfibieslekt',
            'nn': 'amfibieslekt',
            'ro': 'gen de amfibieni',
            'ru': 'род амфибий',
            'sq': 'gjini e amfibeve',
        }, 
        'genus of arachnids': {
            'ar': 'جنس من العنكبوتيات',
            'bn': 'অ্যারাকনিডের গণ',
            'ca': "gènere d'aràcnids",
            'en': 'genus of arachnids',
            'es': 'género de arañas',
            'et': 'ämblikulaadsete perekond',
            'fr': "genre d'araignées",
            'he': 'סוג של עכביש',
            'id': 'genus arachnida',
            'io': 'genero di aranei',
            'it': 'genere di ragni',
            'nb': 'edderkoppslekt',
            'nn': 'edderkoppslekt',
            'ro': 'gen de arahnide',
        }, 
        'genus of birds': {
            'ar': 'جنس من الطيور',
            'bn': 'পাখির গণ',
            'ca': "gènere d'ocells",
            'cy': 'genws o adar',
            'en': 'genus of birds',
            'es': 'género de aves',
            'et': 'linnuperekond',
            'fr': "genre d'oiseaux",
            'gl': 'xénero de aves',
            'he': 'סוג של ציפור',
            'id': 'genus burung',
            'io': 'genero di uceli',
            'it': 'genere di uccelli',
            'ro': 'gen de păsări',
            'sq': 'gjini e zogjve',
        }, 
        'genus of fishes': {
            'ar': 'جنس من الأسماك',
            'bn': 'মাছের গণ',
            'en': 'genus of fishes',
            'es': 'género de peces',
            'et': 'kalade perekond',
            'fr': 'genre de poissons',
            'he': 'סוג של דג',
            'id': 'genus ikan',
            'io': 'genero di fishi',
            'it': 'genere di pesci',
            'nb': 'fiskeslekt',
            'nn': 'fiskeslekt',
            'pt': 'género de peixes',
            'pt-br': 'gênero de peixes',
            'ro': 'gen de pești',
            'sq': 'gjini e peshqëve',
        }, 
        'genus of fungi': {
            'ar': 'جنس من الفطريات',
            'bn': 'ছত্রাকের গণ',
            'en': 'genus of fungi',
            'es': 'género de hongos',
            'et': 'seente perekond',
            'fr': 'genre de champignons',
            'gl': 'xénero de fungos',
            'he': 'סוג של פטריה',
            'id': 'genus fungi',
            'io': 'genero di fungi',
            'it': 'genere di funghi',
            'nb': 'soppslekt',
            'nn': 'soppslekt',
            'pt': 'género de fungos',
            'pt-br': 'gênero de fungos',
#            'ro': 'gen de fungi',# or 'gen de ciuperci'
            'sq': 'gjini e kërpudhave',
        }, 
        'genus of insects': {
            'ar': 'جنس من الحشرات',
            'bn': 'কীটপতঙ্গের গণ',
            'ca': "gènere d'insectes",
            'en': 'genus of insects',
            'es': 'género de insectos',
            'et': 'putukate perekond',
            'fr': "genre d'insectes",
            'he': 'סוג של חרק',
            'id': 'genus serangga',
            'io': 'genero di insekti',
            'it': 'genere di insetti',
            'nb': 'insektslekt',
            'nn': 'insektslekt',
            'pt': 'género de insetos',
            'pt-br': 'gênero de insetos',
            'ro': 'gen de insecte',
            'ru': 'род насекомых',
            'sq': 'gjini e insekteve',
        }, 
        'genus of mammals': {
            'ar': 'جنس من الثدييات',
            'bn': 'স্তন্যপায়ীর গণ',
            'ca': 'gènere de mamífers',
            'en': 'genus of mammals',
            'es': 'género de mamíferos',
            'et': 'imetajate perekond',
            'fr': 'genre de mammifères',
            'gl': 'xénero de mamíferos',
            'he': 'סוג של יונק',
            'id': 'genus mamalia',
            'io': 'genero di mamiferi',
            'nb': 'pattedyrslekt',
            'nn': 'pattedyrslekt',
            'ro': 'gen de mamifere',
            'sq': 'gjini e gjitarëve',
        }, 
        'genus of molluscs': {
            'ar': 'جنس من الرخويات',
            'bn': 'মলাস্কার গণ',
            'ca': 'gènere de mol·luscs',
            'en': 'genus of molluscs',
            'es': 'género de moluscos',
            'et': 'limuste perekond',
            'fr': 'genre de mollusques',
            'gl': 'xénero de moluscos',
            'he': 'סוג של רכיכה',
            'id': 'genus moluska',
            'io': 'genero di moluski',
            'it': 'genere di molluschi',
            'nb': 'bløtdyrslekt',
            'nn': 'blautdyrslekt',
            'ro': 'gen de moluște',
            'sq': 'gjini e molusqeve',
        }, 
        'genus of plants': {
            'ar': 'جنس من النباتات',
            'ca': 'gènere de plantes',
            'bn': 'উদ্ভিদের গণ',
            'cy': 'genws o blanhigion',
            'en': 'genus of plants',
            'es': 'género de plantas',
            'et': 'taimeperekond',
            'fr': 'genre de plantes',
            'gl': 'xénero de plantas',
            'he': 'סוג של צמח',
            'id': 'genus tumbuh-tumbuhan',
            'io': 'genero di planti',
            'nb': 'planteslekt',
            'nn': 'planteslekt',
            'pt': 'género de plantas',
            'pt-br': 'gênero de plantas',
            'ro': 'gen de plante',
            'sq': 'gjini e bimëve',
        }, 
        'genus of reptiles': {
            'ar': 'جنس من الزواحف',
            'bn': 'সরীসৃপের গণ',
            'ca': 'gènere de rèptils',
            'en': 'genus of reptiles',
            'es': 'género de reptiles',
            'et': 'roomajate perekond',
            'fr': 'genre de reptiles',
            'he': 'סוג של זוחל',
            'id': 'genus reptilia',
            'io': 'genero di repteri',
            'nb': 'krypdyrslekt',
            'nn': 'krypdyrslekt',
            'ro': 'gen de reptile',
            'sq': 'e zvarranikëve',
        }, 
        'family name': {
            'an': 'apelliu', 
            'ar': 'اسم العائلة', 
            'ast': 'apellíu', 
            'az': 'Soyad', 
            'bar': 'Schreibnam', 
            'be': 'прозвішча', 
            'bg': 'презиме', 
            'bn': 'পারিবারিক নাম', 
            'bs': 'prezime', 
            'ca': 'cognom', 
            'cs': 'příjmení', 
            'cy': 'cyfenw', 
            'da': 'efternavn', 
            'de': 'Familienname', 
            'de-at': 'Familienname', 
            'de-ch': 'Familienname', 
            'el': 'επώνυμο', 
            'en': 'family name', 
            'eo': 'familia nomo', 
            'es': 'apellido', 
            'et': 'perekonnanimi', 
            'eu': 'abizen', 
            'fa': 'نام خانوادگی', 
            'fi': 'sukunimi', 
            'fo': 'ættarnavn',
            'fr': 'nom de famille', 
            'gl': 'apelido', 
            'gsw': 'Familiename', 
            'gu': 'અટક', 
            'he': 'שם משפחה', 
            'hr': 'prezime', 
            'hu': 'vezetéknév', 
            'hy': 'ազգանուն', 
            'id': 'nama keluarga', 
            'is': 'eftirnafn',
            'it': 'cognome', 
            'ja': '姓', 
            'ka': 'გვარი', 
            'ko': '성씨', 
            'lb': 'Familljennumm', 
            'lt': 'pavardė', 
            'lv': 'uzvārds', 
            'min': 'namo asli', 
            'mk': 'презиме', 
            'nb': 'etternavn', 
            'nds': 'Familiennaam', 
            'nl': 'achternaam', 
            'nn': 'etternamn', 
            'pl': 'nazwisko', 
            'pt': 'sobrenome', 
            'pt-br': 'nome de família', 
            'ro': 'nume de familie', 
            'ru': 'фамилия', 
            'se': 'goargu',
            'sh': 'prezime', 
            'sje': 'maŋŋepnamma',
            'sk': 'priezvisko', 
            'sl': 'priimek',
            'sma': 'fuelhkienomme',
            'smj': 'maŋepnamma',
            'sq': 'mbiemër', 
            'sr': 'презиме', 
            'sv': 'efternamn', 
            'tl': 'apelyido', 
            'tr': 'soyadı', 
            'uk': 'прізвище', 
            'zh': '姓氏', 
            'zh-cn': '姓氏', 
            'zh-hans': '姓氏', 
            'zh-hant': '姓氏', 
            'zh-hk': '姓氏', 
            'zh-mo': '姓氏', 
            'zh-my': '姓氏', 
            'zh-sg': '姓氏', 
            'zh-tw': '姓氏',  
            'zu': 'isibongo', 
        }, 
        'female given name': {
            'af': 'vroulike voornaam',
            'ar': 'اسم شخصي مذكر',
            'ast': 'nome femenín',
            'bar': 'Weiwanam',
            'be': 'жаночае асабістае імя',
            'bn': 'প্রদত্ত মহিলা নাম',
            'br': 'anv merc’hed',
            'bs': 'žensko ime',
            'ca': 'prenom femení',
            'ce': 'зудчун шен цӀе',
            'cs': 'ženské křestní jméno',
            'cy': 'enw personol benywaidd',
            'da': 'pigenavn',
            'de': 'weiblicher Vorname',
            'de-at': 'weiblicher Vorname',
            'de-ch': 'weiblicher Vorname',
            'el': 'γυναικείο όνομα',
            'en': 'female given name',
            'en-ca': 'female given name',
            'en-gb': 'female given name',
            'eo': 'virina persona nomo',
            'es': 'nombre femenino',
            'et': 'naisenimi',
            'fa': 'نام‌های زنانه',
            'fi': 'naisen etunimi',
            'fr': 'prénom féminin',
            'fy': 'froulike foarnamme',
            'he': 'שם פרטי של אישה',
            'hr': 'žensko ime',
            'hsb': 'žonjace předmjeno',
            'hu': 'női keresztnév',
            'hy': 'իգական անձնանուն',
            'id': 'nama depan wanita',
            'it': 'prenome femminile',
            'ja': '女性の名前',
            'ko': '여성의 이름',
            'la': 'praenomen femininum',
            'lb': 'weibleche Virnumm',
            'lt': 'moteriškas vardas',
            'lv': 'sieviešu personvārds',
            'mk': 'женско лично име',
            'nb': 'kvinnenavn',
            'ne': 'स्त्रीलिङ्गी नाम',
            'nl': 'vrouwelijke voornaam',
            'nn': 'kvinnenamn',
            'pl': 'imię żeńskie',
            'pt': 'nome próprio feminino',
            'pt-br': 'nome próprio feminino',
            'ro': 'prenume feminin',
            'ru': 'женское личное имя',
            'sr': 'женско лично име',
            'sr-ec': 'женско лично име',
            'scn': 'nomu di battìu fimmininu',
            'sco': 'female gien name',
            'sk': 'ženské krstné meno',
            'sl': 'žensko osebno ime',
            'sq': 'emër femëror',
            'sr-el': 'žensko lično ime',
            'sv': 'kvinnonamn',
            'tr': 'kadın ismidir',
            'uk': 'жіноче особове ім’я',
            'yue': '女性人名',
            'zh': '女性人名',
            'zh-cn': '女性人名 ',
            'zh-hans': '女性人名',
            'zh-hant': '女性人名',
            'zh-hk': '女性人名',
            'zh-mo': '女性人名',
            'zh-my': '女性人名',
            'zh-sg': '女性人名',
            'zh-tw': '女性人名'
        }, 
        'Hebrew calendar year': {
            'ar': 'سنة في التقويم العبري',
            'bn': 'হিব্রু পঞ্জিকার বছর', 
            'ca': 'any de calendari hebreu', 
            'en': 'Hebrew calendar year', 
            'es': 'año del calendario hebreo', 
            'fa': 'سال در گاه‌شماری عبری', 
            'fr': 'année hébraïque', 
            'he': 'שנה עברית',
            'hy': 'Հրեական օրացույցի տարեթիվ',
            'id': 'tahun kalendar Ibrani',
            'nb': 'hebraisk kalenderår',
            'nn': 'hebraisk kalenderår',
            'ru': 'год еврейского календаря', 
            'sq': 'vit i kalendarik hebraik',
        }, 
        'Islamic calendar year': {
            'ar': 'سنة في التقويم الإسلامي',
            'bn': 'ইসলামী পঞ্জিকার বছর',
            'en': 'Islamic calendar year', 
            'es': 'año del calendario musulmán',
            'he': 'שנה בלוח השנה המוסלמי', 
            'id': 'tahun kalendar Islam',
            'nb': 'islamsk kalenderår',
            'nn': 'islamsk kalenderår',
            'sq': 'vit i kalendarik islamik',
        }, 
        'male given name': {
            'af': 'manlike voornaam',
            'ar': 'اسم شخصي مذكر',
            'ast': 'nome masculín',
            'bar': 'Mannanam',
            'be': 'мужчынскае асабістае імя',
            'be-tarask': 'мужчынскае асабістае імя',
            'bn': 'প্রদত্ত পুরুষ নাম',
            'br': 'anv paotr',
            'bs': 'muško ime',
            'ca': 'prenom masculí',
            'ce': 'стеган шен цӀе',
            'cs': 'mužské křestní jméno',
            'cy': 'enw personol gwrywaidd',
            'da': 'drengenavn',
            'de': 'männlicher Vorname',
            'de-at': 'männlicher Vorname',
            'de-ch': 'männlicher Vorname',
            'el': 'ανδρικό όνομα',
            'en': 'male given name',
            'en-ca': 'male given name',
            'en-gb': 'male given name',
            'eo': 'vira persona nomo',
            'es': 'nombre masculino',
            'et': 'mehenimi',
            'eu': 'gizonezko izena',
            'fa': 'نام کوچک مردانه',
            'fi': 'miehen etunimi',
            'fr': 'prénom masculin',
            'fy': 'manlike foarnamme',
            'gl': 'nome masculino',
            'gsw': 'männlige Vorname',
            'he': 'שם פרטי של גבר',
            'hr': 'muško ime',
            'hu': 'férfi keresztnév',
            'hy': 'արական անձնանուն',
            'id': 'nama pemberian maskulin',
            'is': 'mannsnafn',
            'it': 'prenome maschile',
            'ja': '男性の名前',
            'ko': '남성의 이름',
            'la': 'praenomen masculinum',
            'lb': 'männleche Virnumm',
            'lt': 'vyriškas vardas',
            'lv': 'vīriešu personvārds',
            'mk': 'машко лично име',
            'nb': 'mannsnavn',
            'ne': 'पुलिङ्गी नाम',
            'nl': 'mannelijke voornaam',
            'nn': 'mannsnamn',
            'pl': 'imię męskie',
            'pt': 'nome próprio masculino',
            'pt-br': 'nome próprio masculino',
            'ro': 'prenume masculin',
            'ru': 'мужское личное имя',
            'scn': 'nomu di battìu masculinu',
            'sco': 'male first name',
            'sk': 'mužské meno',
            'sl': 'moško osebno ime',
            'sq': 'emër mashkullor',
            'sr': 'мушко лично име',
            'sr-el': 'muško lično ime',
            'sr-ec': 'мушко лично име',
            'sv': 'mansnamn',
            'tr': 'erkek ismidir',
            'uk': 'чоловіче особове ім’я',
            'yue': '男性人名',
            'zh': '男性人名',
            'zh-cn': '男性人名',
            'zh-hans': '男性名',
            'zh-hant': '男性人名',
            'zh-hk': '男性人名',
            'zh-mo': '男性人名',
            'zh-my': '男性人名',
            'zh-sg': '男性人名',
            'zh-tw': '男性人名'
        },
        'natural number': {
            'af': 'natuurlike getal',
            'als': 'natürlige Zahle',
            'an': 'numero natural',
            'ar': 'عدد طبيعي',
            'bn': 'প্রাকৃতিক সংখ্যা',
            'ca': 'nombre natural',
            'cy': 'rhif naturiol',
            'en': 'natural number',
            'en-ca': 'natural number',
            'en-gb': 'natural number',
            'eo': 'natura nombro',
            'es': 'número natural',
            'et': 'naturaalarv',
            'he': 'מספר טבעי',
            'hi': 'प्राकृतिक संख्या',
            'hy': 'Բնական թիվ',
            'ia': 'numero natural',
            'id': 'angka alami',
            'io': 'naturala nombro',
            'ka': 'ნატურალური რიცხვი',
            'kn': 'ಸ್ವಾಭಾವಿಕ ಸಂಖ್ಯೆ',
            'it': 'numero naturale',
            'la': 'numerus naturalis',
            'mwl': 'númaro natural',
            'nb': 'naturlig tall',
            'nn': 'naturleg tal',
            'pms': 'nùmer natural',
            'pt': 'número natural',
            'ro': 'număr natural',
            'scn': 'nùmmuru naturali',
            'sco': 'naitural nummer',
            'sc': 'nùmeru naturale',
            'szl': 'naturalno nůmera',
            'ru': 'натуральное число',
            'sq': 'numër natyror',
            'uk': 'натуральне число',
        },
        'prime number': {
            'ast': 'númberu primu',
            'ca': 'nombre primer',
            'en': 'prime number',
            'en-ca': 'prime number',
            'en-gb': 'prime number',
            'en-us': 'prime number',
            'es': 'número primo',
            'fr': 'nombre premier',
            'gl': 'número primo',
            'it': 'numero primo',
            'pt': 'número primo',
            'pt-br': 'número primo',
        },
        'researcher': {
            'ast': 'investigador',
            'ca': 'investigador',
            'en': 'researcher',
            'en-ca': 'researcher',
            'en-gb': 'researcher',
            'en-us': 'researcher',
            'es': 'investigador/a',
            'fr': 'chercheur',
            'gl': 'investigador',
            'it': 'ricercatore',
            'pt': 'investigador',
        },
        'researcher female': {
            'ast': 'investigadora',
            'ca': 'investigadora',
            'en': 'researcher',
            'en-ca': 'researcher',
            'en-gb': 'researcher',
            'en-us': 'researcher',
            'es': 'investigadora',
            'fr': 'chercheuse',
            'gl': 'investigadora',
            'it': 'ricercatrice',
            'pt': 'investigadora',
        },
        'researcher male': {
            'ast': 'investigador',
            'ca': 'investigador',
            'en': 'researcher',
            'en-ca': 'researcher',
            'en-gb': 'researcher',
            'en-us': 'researcher',
            'es': 'investigador',
            'fr': 'chercheur',
            'gl': 'investigador',
            'it': 'ricercatore',
            'pt': 'investigador',
        },
        'shipwreck off the Scottish coast': {
            'en': 'shipwreck off the Scottish coast',
            'es': 'naufragio frente a la costa escocesa',
        },
        'species of alga': {
            'bn': 'শৈবালের প্রজাতি',
            'en': 'species of alga',
            'es': 'especie de alga',
            'et': 'vetikaliik',
            'gl': 'especie de alga',
            'he': 'מין של אצה',
            'io': 'speco di algo',
            'ro': 'specie de alge',
            'sq': 'lloj i algave',
        },
        'species of amphibian': {
            'bn': 'উভচর প্রাণীর প্রজাতি',
            'ca': 'espècie d\'amfibi',
            'en': 'species of amphibian',
            'es': 'especie de amfibio',
            'et': 'kahepaiksete liik',
            'fr': 'espèce d\'amphibiens',
            'io': 'speco di amfibio',
            #'it': 'specie di anfibio', or anfibi?
            'pt': 'espécie de anfíbio',
            'he': 'מין של דו-חיים',
            'ro': 'specie de amfibieni',
            'sq': 'lloj i amfibeve',
        },
        'species of arachnid': {
            'bn': 'অ্যারাকনিডের প্রজাতি',
            'ca': 'espècie d\'aràcnid',
            'en': 'species of arachnid',
            'es': 'especie de arácnido',
            'et': 'ämblikulaadsete liik',
            'fr': 'espèce d\'araignées',
            'io': 'speco di araneo',
            'it': 'specie di ragno',
            'pt': 'espécie de aracnídeo',
            'he': 'מין של עכביש',
            'ro': 'specie de arahnide',
        },
        'species of insect': { #las descripciones DE y FR tienen mayor precision y serian mas deseables
        #decidir que hacer
        # https://query.wikidata.org/#SELECT%20%3FitemDescription%20%28COUNT%28%3Fitem%29%20AS%20%3Fcount%29%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ16521.%0A%20%20%20%20%3Fitem%20wdt%3AP105%20wd%3AQ7432.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22species%20of%20insect%22%40en.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER%28LANG%28%3FitemDescription%29%20%3D%20%22de%22%29.%20%20%7D%0A%09FILTER%20%28BOUND%28%3FitemDescription%29%29%0A%7D%0AGROUP%20BY%20%3FitemDescription%0AORDER%20BY%20DESC%28%3Fcount%29
            'an': 'especie d\'insecto',
            'bg': 'вид насекомо',
            'bn': 'কীটপতঙ্গের প্রজাতি',
            'ca': "espècie d'insecte",
            'en': 'species of insect',
            'es': 'especie de insecto',
            'et': 'putukaliik',
            'fr': 'espèce d\'insectes',
            'gl': 'especie de insecto',
            'hy': 'միջատների տեսակ',
            'id': 'spesies serangga',
            'io': 'speco di insekto',
            'nb': 'insektart',
            'nn': 'insektart',
            'pt': 'espécie de inseto',
            'pt-br': 'espécie de inseto',
            'ro': 'specie de insecte',
            'ru': 'вид насекомых',
            'sq': 'lloj i insekteve',
            'ta': 'பூச்சி இனம்',
            'he': 'מין של חרק',
        },
        'species of mollusc': {
            'bn': 'মলাস্কার প্রজাতি',
            'ca': 'espècie de mol·lusc',
            'en': 'species of mollusc',
            'es': 'especie de molusco',
            'et': 'limuseliik',
            'gl': 'especie de molusco',
            'io': 'speco di molusko',
            'pt': 'espécie de molusco',
            'he': 'מין של רכיכה',
            'ro': 'specie de moluște',
            'ru': 'вид моллюсков',
            'sq': 'lloj i molusqeve',
        },
        'species of plant': {
            'bg': 'вид растение',
            'bn': 'উদ্ভিদের প্রজাতি',
            'ca': 'espècie de planta',
            'en': 'species of plant',
            'es': 'especie de planta',
            'et': 'taimeliik',
            'gl': 'especie de planta',
            'hy': 'բույսերի տեսակ',
            'he': 'מין של צמח',
            'io': 'speco di planto',
            'ro': 'specie de plante',
            'ru': 'вид растений',
            'sq': 'lloj i bimëve',
        },
        'television series': {
            'ca': 'sèrie de televisió',
            'en': 'television series',
            'eo': 'televida serio',
            'es': 'serie de televisión',
            'fr': 'série télévisée',
            'hu': 'televíziós sorozat',
            'it': 'serie televisiva',
        },
        'unicode character': {
            'ast': 'caráuter Unicode',
            'ca': 'caràcter Unicode',
            'en': 'Unicode character',
            'eo': 'skribsigno de Unikodo',
            'es': 'carácter Unicode',
            'fr': 'caractère Unicode',
            'gl': 'carácter Unicode',
            'it': 'carattere Unicode',
            'pt': 'caractere Unicode',
            'pt-br': 'caractere Unicode',
        },
        'village in China': {
            'an': 'pueblo d\'a Republica Popular de China', #o 'pueblo de China'
            'ar': 'قرية في الصين',
            'as': 'চীনৰ এখন গাওঁ',
            'bn': 'চীনের একটি গ্রাম',
            'bpy': 'চীনর আহান গাঙ',
            'ca': 'poble de la Xina',
            'cy': 'pentref yn Tsieina',
            'de': 'Dorf in China',
            'el': 'οικισμός της Λαϊκής Δημοκρατίας της Κίνας',
            'en': 'village in China',
            'eo': 'vilaĝo en Ĉinio',
            'es': 'aldea de la República Popular China',
            'et': 'küla Hiinas',
            'fi': 'kylä Kiinassa',
            'fr': 'village chinois',
            'fy': 'doarp yn Sina',
            'gu': 'ચીનનું ગામ',
            'he': 'כפר ברפובליקה העממית של סין',
            'hi': 'चीन का गाँव',
            'hy': 'գյուղ Չինաստանում',
            'id': 'desa di Tiongkok',
            'io': 'vilajo en Chinia',
            'it': 'villaggio cinese',
            'ja': '中国の村',
            'kn': 'ಚೈನಾ ದೇಶದ ಗ್ರಾಮ',
            'mr': 'चीनमधील गाव',
            'nb': 'landsby i Kina',
            'ne': 'चीनका गाउँहरू',
            'nn': 'landsby i Kina',
            'nl': 'dorp in China',
            'oc': 'vilatge chinés',
            'or': 'ଚୀନର ଗାଁ',
            'pt-br': 'vila chinesa',
            'ur': 'چین کا گاؤں',
            'ro': 'sat din China',
            'ru': 'деревня КНР',
            'sq': 'fshat në Kinë',
            'ta': 'சீனாவின் கிராமம்',
            'te': 'చైనాలో గ్రామం',
        },
        'Wikimedia category': { #Q4167836
            'ace': 'kawan Wikimèdia',
            'af': 'Wikimedia-kategorie',
            'an': 'categoría de Wikimedia',
            'ar': 'تصنيف ويكيميديا',
            'arz': 'تصنيف بتاع ويكيميديا',
            'ast': 'categoría de Wikimedia',
            'ba': 'Викимедиа категорияһы',
            'bar': 'Wikimedia-Kategorie',
            'be': 'катэгорыя ў праекце Вікімедыя',
            'be-tarask': 'катэгорыя ў праекце Вікімэдыя',
            'bg': 'категория на Уикимедия',
            'bho': 'विकिपीडिया:श्रेणी',
            'bjn': 'tumbung Wikimedia',
            'bn': 'উইকিমিডিয়া বিষয়শ্রেণী',
            'br': 'pajenn rummata eus Wikimedia',
            'bs': 'kategorija na Wikimediji',
            'bug': 'kategori Wikimedia',
            'ca': 'categoria de Wikimedia',
            #'ce': 'Викимедиа проектан категореш',
            #'ceb': 'Wikimedia:Kategorisasyon',
            'ckb': 'پۆلی ویکیمیدیا',
            'cs': 'kategorie na projektech Wikimedia',
            'cy': 'tudalen categori Wikimedia',
            'da': 'Wikimedia-kategori',
            'de': 'Wikimedia-Kategorie',
            'de-at': 'Wikimedia-Kategorie',
            'de-ch': 'Wikimedia-Kategorie',
            'dty': 'विकिमिडिया श्रेणी',
            'el': 'κατηγορία εγχειρημάτων Wikimedia',
            'en': 'Wikimedia category',
            'en-ca': 'Wikimedia category',
            'en-gb': 'Wikimedia category',
            'eo': 'kategorio en Vikimedio',
            'es': 'categoría de Wikimedia',
            'et': 'Wikimedia kategooria',
            'eu': 'Wikimediako kategoria',
            'fa': 'ردهٔ ویکی‌پدیا',
            'fi': 'Wikimedia-luokka',
            'fo': 'Wikimedia-bólkur',
            'fr': 'page de catégorie de Wikimedia',
            'fy': 'Wikimedia-kategory',
            'ga': 'Viciméid catagóir',
            'gl': 'categoría de Wikimedia',
            'gn': 'Vikimédia ñemohenda',
            'gsw': 'Wikimedia-Kategorie',
            'gu': 'વિકિપીડિયા શ્રેણી',
            'gv': 'Wikimedia:Ronnaghys',
            'he': 'דף קטגוריה',
            'hi': 'विकिमीडिया श्रेणी',
            'hr': 'kategorija na Wikimediji',
            'hsb': 'kategorija w projektach Wikimedije',
            'hu': 'Wikimédia-kategória',
            'hy': 'Վիքիմեդիայի նախագծի կատեգորիա',
            'ia': 'categoria Wikimedia',
            'id': 'kategori Wikimedia',
            'ilo': 'kategoria ti Wikimedia',
            'it': 'categoria di un progetto Wikimedia',
            'ja': 'ウィキメディアのカテゴリ',
            'jv': 'kategori Wikimedia',
            'ka': 'ვიკიპედია:კატეგორიზაცია',
            'ko': '위키미디어 분류',
            'ku': 'Wîkîmediya:Kategorî',
            'kw': 'Wikimedia:Klassys',
            'ky': 'Wikimedia категориясы',
            'la': 'categoria Vicimediorum',
            'lb': 'Wikimedia-Kategorie',
            'li': 'Wikimedia-categorie',
            'lv': 'Wikimedia projekta kategorija',
            'map-bms': 'kategori Wikimedia',
            'min': 'kategori Wikimedia',
            'mk': 'Викимедиина категорија',
            'ml': 'വിക്കിമീഡിയ വർഗ്ഗം',
            'mn': 'категорияд Ангилал',
            'mr': 'विकिपीडिया वर्ग',
            'ms': 'kategori Wikimedia',
            'my': 'Wikimedia:ကဏ္ဍခွဲခြင်း',
            'nap': 'categurìa \'e nu pruggette Wikimedia',
            'nb': 'Wikimedia-kategori',
            'nds': 'Wikimedia-Kategorie',
            'nds-nl': 'Wikimedia-kategorie',
            'ne': 'विकिमिडिया श्रेणी',
            'nl': 'Wikimedia-categorie',
            'nn': 'Wikimedia-kategori',
            'pam': 'Kategoriya ning Wikimedia',
            'pl': 'kategoria w projekcie Wikimedia',
            'ps': 'د ويکيمېډيا وېشنيزه',
            'pt': 'categoria de um projeto da Wikimedia',
            'pt-br': 'categoria de um projeto da Wikimedia',
            'rmy': 'Vikipidiya:Shopni',
            'ro': 'categorie în cadrul unui proiect Wikimedia',
            'ru': 'категория в проекте Викимедиа',
            'scn': 'catigurìa di nu pruggettu Wikimedia',
            'sco': 'Wikimedia category',
            'sd': 'زمرو:وڪيپيڊيا زمرا بندي',
            'se': 'Wikimedia-kategoriija',
            'sh': 'Wikimedia:Kategorija',
            'si': 'විකිමීඩියා ප්‍රභේද පිටුව',
            'sk': 'kategória projektov Wikimedia',
            'sl': 'kategorija Wikimedie',
            'sq': 'kategori e Wikimedias',
            'sr': 'категорија на Викимедији',
            'stq': 'Wikimedia-Kategorie',
            'su': 'kategori Wikimédia',
            'sv': 'Wikimedia-kategori',
            'sw': 'jamii ya Wikimedia',
            'ta': 'விக்கிமீடியப் பகுப்பு',
            'tg': 'гурӯҳи Викимедиа',
            'tg-cyrl': 'гурӯҳ дар лоиҳаи Викимедиа',
            'tg-latn': 'gurühi Vikimedia',
            'th': 'หน้าหมวดหมู่วิกิมีเดีย',
            'tl': 'kategorya ng Wikimedia',
            'tr': 'Vikimedya kategorisi',
            'tt': 'Викимедиа проектындагы төркем',
            'tt-cyrl': 'Викимедиа проектындагы төркем',
            'tt-latn': 'Wikimedia proyektındağı törkem',
            'uk': 'категорія проекту Вікімедіа',
            'ur': 'ویکیمیڈیا زمرہ',
            'vi': 'thể loại Wikimedia',
            'yo': 'ẹ̀ka Wikimedia',
            'yue': '維基媒體分類',
            'zea': 'Wikimedia-categorie',
            'zh': '维基媒体分类',
            'zh-cn': '维基媒体分类',
            'zh-hans': '维基媒体分类',
            'zh-hant': '維基媒體分類',
            'zh-hk': '維基媒體分類',
            'zh-mo': '維基媒體分類',
            'zh-my': '维基媒体分类',
            'zh-sg': '维基媒体分类',
            'zh-tw': '維基媒體分類',
        },
        'Wikimedia disambiguation page': { #Q4167410
            'an': 'pachina de desambigación',
            'ar': 'صفحة توضيح لويكيميديا',
            'as': 'ৱিকিমিডিয়া দ্ব্যৰ্থতা দূৰীকৰণ পৃষ্ঠা',
            'bg': 'Уикимедия пояснителна страница',
            'bn': 'উইকিমিডিয়ার দ্ব্যর্থতা নিরসন পাতা',
            'bs': 'čvor stranica na Wikimediji',
            'ca': 'pàgina de desambiguació de Wikimedia',
            'ckb': 'پەڕەی ڕوونکردنەوەی ویکیمیدیا',
            'cs': 'rozcestník na projektech Wikimedia',
            'da': 'Wikimedia-flertydigside',
            'de': 'Wikimedia-Begriffsklärungsseite',
            'de-at': 'Wikimedia-Begriffsklärungsseite',
            'de-ch': 'Wikimedia-Begriffsklärungsseite',
            'el': 'σελίδα αποσαφήνισης εγχειρημάτων Wikimedia',
            'en': 'Wikimedia disambiguation page',
            'en-ca': 'Wikimedia disambiguation page',
            'en-gb': 'Wikimedia disambiguation page',
            'eo': 'Vikimedia apartigilo',
            'es': 'página de desambiguación de Wikimedia',
            'et': 'Wikimedia täpsustuslehekülg',
            'eu': 'Wikimediako argipen orri',
            'fa': 'یک صفحهٔ ابهام\u200cزدایی در ویکی\u200cپدیا',
            'fi': 'Wikimedia-täsmennyssivu',
            'fr': 'page d\'homonymie de Wikimedia',
            'fy': 'Wikimedia-betsjuttingsside',
            'gl': 'páxina de homónimos de Wikimedia',
            'gsw': 'Wikimedia-Begriffsklärigssite',
            'gu': 'સ્પષ્ટતા પાનું',
            'he': 'דף פירושונים',
            'hi': 'बहुविकल्पी पृष्ठ',
            'hr': 'razdvojbena stranica na Wikimediji',
            'hu': 'Wikimédia-egyértelműsítőlap',
            'hy': 'Վիքիմեդիայի նախագծի բազմիմաստության փարատման էջ',
            'id': 'halaman disambiguasi Wikimedia',
            'is': 'aðgreiningarsíða á Wikipediu',
            'it': 'pagina di disambiguazione di un progetto Wikimedia',
            'ja': 'ウィキメディアの曖昧さ回避ページ',
            'ka': 'მრავალმნიშვნელოვანი',
            'kn': 'ದ್ವಂದ್ವ ನಿವಾರಣೆ',
            'ko': '위키미디어 동음이의어 문서',
            'lb': 'Wikimedia-Homonymiesäit',
            'li': 'Wikimedia-verdudelikingspazjena',
            'lv': 'Wikimedia projekta nozīmju atdalīšanas lapa',
            'min': 'laman disambiguasi',
            'mk': 'појаснителна страница',
            'ml': 'വിക്കിപീഡിയ വിവക്ഷ താൾ',
            'mr': 'निःसंदिग्धीकरण पाने',
            'ms': 'laman nyahkekaburan',
            'nb': 'Wikimedia-pekerside',
            'nds': 'Sied för en mehrdüdig Begreep op Wikimedia',
            'nl': 'Wikimedia-doorverwijspagina',
            'nn': 'Wikimedia-fleirtydingsside',
            'or': 'ବହୁବିକଳ୍ପ ପୃଷ୍ଠା',
            'pa': 'ਵਿਕੀਮੀਡੀਆ ਗੁੰਝਲਖੋਲ੍ਹ ਸਫ਼ਾ',
            'pl': 'strona ujednoznaczniająca w projekcie Wikimedia',
            'pt': 'página de desambiguação da Wikimedia',
            'ro': 'pagină de dezambiguizare Wikimedia',
            'ru': 'страница значений в проекте Викимедиа',
            'sco': 'Wikimedia disambiguation page',
            'sk': 'rozlišovacia stránka',
            'sl': 'razločitvena stran Wikimedije',
            'sq': 'faqe kthjelluese e Wikimedias',
            'sr': 'вишезначна одредница на Викимедији',
            'sv': 'Wikimedia-förgreningssida',
            'te': 'వికీమీడియా అయోమయ నివృత్తి పేజీ',
            'tg': 'саҳифаи маъноҳои Викимедиа',
            'tg-cyrl': 'саҳифаи маъноҳои Викимедиа',
            'tg-latn': "sahifai ma'nohoi Vikimedia",
            'tr': 'Vikimedya anlam ayrımı sayfası',
            'tt': 'Мәгънәләр бите Викимедиа проектында',
            'tt-cyrl': 'Мәгънәләр бите Викимедиа проектында',
            'tt-latn': 'Mäğnälär bite Wikimedia proyektında',
            'uk': 'сторінка значень у проекті Вікімедіа',
            'vi': 'trang định hướng Wikimedia',
            'yo': 'ojúewé ìṣojútùú Wikimedia',
            'yue': '維基媒體搞清楚頁',
            'zea': 'Wikimedia-deurverwiespagina',
            'zh': '维基媒体消歧义页',
            'zh-cn': '维基媒体消歧义页',
            'zh-hans': '维基媒体消歧义页',
            'zh-hant': '維基媒體消歧義頁',
            'zh-hk': '維基媒體消歧義頁',
            'zh-mo': '維基媒體消歧義頁',
            'zh-my': '维基媒体消歧义页',
            'zh-sg': '维基媒体消歧义页',
            'zh-tw': '維基媒體消歧義頁',
        },
        'Wikimedia list article': { #Q13406463
            'ace': 'teunuléh dapeuta Wikimèdia',
            'af': 'Wikimedia lysartikel',
            'an': 'articlo de lista de Wikimedia',
            'ar': 'قائمة ويكيميديا',
            'as': 'ৱিকিপিডিয়া:ৰচনাশৈলীৰ হাতপুথি',
            'ast': 'artículu de llista de Wikimedia',
            'ba': 'Wikimedia-Listn',
            'be': 'спіс атыкулаў у адным з праектаў Вікімедыя',
            'bn': 'উইকিমিডিয়ার তালিকা নিবন্ধ',
            'bs': 'spisak na Wikimediji',
            'ca': 'article de llista de Wikimedia',
            'cs': 'seznam na projektech Wikimedia',
            'da': 'Wikimedia liste',
            'de': 'Wikimedia-Liste',
            'de-at': 'Wikimedia-Liste',
            'de-ch': 'Wikimedia-Liste',
            'el': 'κατάλογος εγχειρήματος Wikimedia',
            'en': 'Wikimedia list article',
            'en-ca': 'Wikimedia list article',
            'en-gb': 'Wikimedia list article',
            'eo': 'listartikolo en Vikimedio',
            'es': 'artículo de lista de Wikimedia',
            'et': 'Wikimedia loend',
            'eu': 'Wikimediako zerrenda artikulua',
            'fi': 'Wikimedia-luetteloartikkeli',
            'fr': 'page de liste de Wikimedia',
            'fy': 'Wikimedia-list',
            'gl': 'artigo de listas da Wikimedia',
            'he': 'רשימת ערכים',
            'hr': 'popis na Wikimediji',
            'hy': 'Վիքիմեդիայի նախագծի ցանկ',
            'id': 'artikel daftar Wikimedia',
            'ia': 'lista de un projecto de Wikimedia',
            'it': 'lista di un progetto Wikimedia',
            'ja': 'ウィキメディアの一覧記事',
            'ko': '위키미디어 목록 항목',
            'lb': 'Wikimedia-Lëschtenartikel',
            'li': 'Wikimedia-lies',
            'mk': 'список на статии на Викимедија',
            'ms': 'rencana senarai Wikimedia',
            'nb': 'Wikimedia-listeartikkel',
            'nl': 'Wikimedia-lijst',
            'nn': 'Wikimedia-listeartikkel',
            'oc': 'lista d\'un projècte Wikimèdia',
            'pl': 'lista w projekcie Wikimedia',
            'ro': 'articol-listă în cadrul unui proiect Wikimedia',
            'ru': 'статья-список в проекте Викимедиа',
            'sco': 'Wikimedia leet airticle',
            'si': 'විකිමීඩියා ලැයිස්තු ලිපිය',
            'sk': 'zoznamový článok projektov Wikimedia',
            'sl': 'seznam Wikimedije',
            'sq': 'artikull-listë e Wikimedias',
            'sr': 'списак на Викимедији',
            'sv': 'Wikimedia-listartikel',
            'ta': 'விக்கிப்பீடியா:பட்டியலிடல்',
            'tg': 'саҳифаи феҳристӣ',
            'tg-cyrl': 'мақолаи феҳристӣ',
            'tg-latn': 'sahifai fehristī',
            'th': 'บทความรายชื่อวิกิมีเดีย',
            'tr': 'Vikimedya liste maddesi',
            'uk': 'сторінка-список у проекті Вікімедіа',
            'vi': 'bài viết danh sách Wikimedia',
            'yi': 'וויקימעדיע ליסטע',
            'yo': 'ojúewé àtojọ Wikimedia',
            'zea': 'Wikimedia-lieste',
            'zh': '维基媒体列表条目',
            'zh-cn': '维基媒体列表条目',
            'zh-hans': '维基媒体列表条目',
            'zh-hant': '維基媒體列表條目',
            'zh-hk': '維基媒體列表條目',
            'zh-mo': '維基媒體列表條目',
            'zh-my': '维基媒体列表条目',
            'zh-sg': '维基媒体列表条目',
            'zh-tw': '維基媒體列表條目'
        },
        'Wikimedia template': { #Q11266439
            'an': 'plantilla de Wikimedia',
            'ar': 'قالب ويكيميديا', 
            'arz': 'ويكيبيديا:قوالب', 
            'ast': 'plantía de proyectu', 
            'ba': 'Викимедиа ҡалыбы', 
            'bar': 'Wikimedia-Vorlog', 
            'be': 'шаблон праекта Вікімедыя', 
            'be-tarask': 'шаблён праекту Вікімэдыя', 
            'bg': 'Уикимедия шаблон', 
            'bn': 'উইকিমিডিয়া টেমপ্লেট', 
            'bs': 'šablon Wikimedia', 
            'ca': 'plantilla de Wikimedia', 
            'ce': 'Викимедин проектан кеп', 
            'cs': 'šablona na projektech Wikimedia', 
            'cy': 'nodyn Wikimedia', 
            'da': 'Wikimedia-skabelon', 
            'de': 'Wikimedia-Vorlage', 
            'el': 'Πρότυπο εγχειρήματος Wikimedia', 
            'en': 'Wikimedia template', 
            'en-ca': 'Wikimedia template', 
            'en-gb': 'Wikimedia template', 
            'eo': 'Vikimedia ŝablono', 
            'es': 'plantilla de Wikimedia', 
            'et': 'Wikimedia mall', 
            'eu': 'Wikimediako txantiloia', 
            'fa': 'الگوی ویکی‌مدیا', 
            'fi': 'Wikimedia-malline', 
            'fo': 'fyrimynd Wikimedia', 
            'fr': 'modèle de Wikimedia', 
            'frr': 'Wikimedia-föörlaag', 
            'fy': 'Wikimedia-berjocht', 
            'gl': 'modelo da Wikimedia', 
            'gsw': 'Wikimedia-Vorlage', 
            'gu': 'વિકિપીડિયા ઢાંચો', 
            'he': 'תבנית של ויקימדיה', 
            'hu': 'Wikimédia-sablon', 
            'hy': 'Վիքիմեդիայի նախագծի կաղապար', 
            'id': 'templat Wikimedia', 
            'ilo': 'plantilia ti Wikimedia', 
            'it': 'template di un progetto Wikimedia', 
            'ja': 'ウィキメディアのテンプレート', 
            'jv': 'cithakan Wikimedia', 
            'ka': 'ვიკიმედიის თარგი', 
            'ko': '위키미디어 틀', 
            'ku-latn': 'şablona Wîkîmediyayê', 
            'la': 'formula Vicimediorum', 
            'lb': 'Wikimedia-Schabloun', 
            'li': 'Wikimedia-sjabloon', 
            'lt': 'Vikimedijos šablonas', 
            'lv': 'Wikimedia projekta veidne', 
            'mk': 'шаблон на Викимедија', 
            'ml': 'വിക്കിമീഡിയ ഫലകം', 
            'mr': 'विकिपीडिया:साचा', 
            'ms': 'Templat Wikimedia', 
            'nb': 'Wikimedia-mal', 
            'nds': 'Wikimedia-Vörlaag', 
            'nds-nl': 'Wikimedia-mal', 
            'nl': 'Wikimedia-sjabloon', 
            'nn': 'Wikimedia-mal',
            'oc': 'modèl de Wikimèdia', 
            'or': 'ଉଇକିମିଡ଼ିଆ ଛାଞ୍ଚ', 
            'pam': 'Ulmang pang-Wikimedia', 
            'pl': 'szablon w projekcie Wikimedia', 
            'ps': 'ويکيمېډيا کينډۍ', 
            'pt': 'predefinição da Wikimedia', 
            'pt-br': 'predefinição da Wikimedia', 
            'ro': 'format Wikimedia', 
            'ru': 'шаблон проекта Викимедиа', 
            'sco': 'Wikimedia template', 
            'se': 'Wikimedia-málle',
            'sk': 'šablóna projektov Wikimedia', 
            'sq': 'stampë e Wikimedias', 
            'sr': 'Викимедијин шаблон', 
            'sr-ec': 'Викимедијин шаблон', 
            'stq': 'Wikimedia-Foarloage', 
            'sv': 'Wikimedia-mall', 
            'sw': 'kigezo cha Wikimedia', 
            'ta': 'விக்கிமீடியா வார்ப்புரு', 
            'te': 'వికీమీడియా మూస', 
            'tg': 'шаблони лоиҳаи Викимедиа', 
            'tg-cyrl': 'шаблони лоиҳаи Викимедиа', 
            'tg-latn': 'shabloni loihai Vikimedia', 
            'th': 'หน้าแม่แบบวิกิมีเดีย', 
            'tl': 'Padrong pang-Wikimedia', 
            'tr': 'Vikimedya şablonu',
            'uk': 'шаблон у проекті Вікімедіа', 
            'vi': 'bản mẫu Wikimedia', 
            'yo': 'àdàkọ Wikimedia',
            'yue': '維基媒體模',
            'zea': 'Wikimedia-sjabloon',
            'zh': '维基媒体模板', 
            'zh-cn': '维基媒体模板', 
            'zh-hans': '维基媒体模板', 
            'zh-hant': '維基媒體模板', 
            'zh-hk': '維基媒體模板', 
            'zh-tw': '維基媒體模板', 
        },
        'Wikinews article': { #Q17633526
            'an': 'articlo de Wikinews',
            'ar': 'مقالة ويكي أخبار',
            'bar': 'Artike bei Wikinews',
            'bn': 'উইকিসংবাদের নিবন্ধ',
            'bs': 'Wikinews članak',
            'ca': 'article de Viquinotícies', 
            'cs': 'článek na Wikizprávách',
            'da': 'Wikinews-artikel',
            'de': 'Artikel bei Wikinews', 
            'el': 'Άρθρο των Βικινέων', 
            'en': 'Wikinews article', 
            'en-ca': 'Wikinews article', 
            'en-gb': 'Wikinews article', 
            'eo': 'artikolo de Vikinovaĵoj', 
            'es': 'artículo de Wikinoticias', 
            'eu': 'Wikialbisteakeko artikulua',
            'fi': 'Wikiuutisten artikkeli',
            'fr': 'article de Wikinews', 
            'fy': 'Wikinews-artikel', 
            'he': 'כתבה בוויקיחדשות',
            'hu': 'Wikihírek-cikk',
            'hy': 'Վիքիլուրերի հոդված',
            'id': 'artikel Wikinews',
            'it': 'articolo di Wikinotizie', 
            'ja': 'ウィキニュースの記事',
            'ko': '위키뉴스 기사',
            'ku-latn': 'gotara li ser Wîkînûçeyê',
            'li': 'Wikinews-artikel', 
            'lt': 'Vikinaujienų straipsnis', 
            'mk': 'напис на Викивести', 
            'nb': 'Wikinytt-artikkel', 
            'nl': 'Wikinieuws-artikel', 
            'nn': 'Wikinytt-artikkel',
            'or': 'ଉଇକି ସୂଚନା ପତ୍ରିକା',
            'pl': 'artykuł w Wikinews', 
            'ps': 'د ويکيخبرونو ليکنه',
            'pt': 'artigo do Wikinotícias', 
            'ro': 'articol în Wikiștiri', 
            'ru': 'статья Викиновостей',
            'sq': 'artikull i Wikinews',
            'sr': 'чланак са Викивести',
            'sv': 'Wikinews-artikel',
            'te': 'వికీవార్త వ్యాసం',
            'tg': 'саҳифаи Викиахбор',
            'tg-cyrl': 'саҳифаи Викиахбор',
            'tg-latn': 'sahifai Vikiakhbor',
            'th': 'เนื้อหาวิกิข่าว', 
            'tr': 'Vikihaber maddesi',
            'uk': 'стаття Вікіновин', 
            'zea': 'Wikinews-artikel',
            'zh': '維基新聞新聞稿', 
            'zh-cn': '维基新闻新闻稿', 
            'zh-hans': '维基新闻新闻稿', 
            'zh-hant': '維基新聞新聞稿', 
            'zh-hk': '維基新聞新聞稿', 
            'zh-mo': '維基新聞新聞稿', 
            'zh-my': '维基新闻新闻稿', 
            'zh-sg': '维基新闻新闻稿', 
            'zh-tw': '維基新聞新聞稿', 
        }, 
        'year': {
            'af': 'jaar',
            'an': 'anyo',
            'ar': 'سنة',
            'ast': 'añu',
            'be': 'год', 
            'be-tarask': 'год',
            'bg': 'година',
            'bn': 'বছর',
            'br': 'bloavezh',
            'bs': 'godina',
            'ca': 'any',
            'cs': 'rok',
            'cy': 'blwyddyn',
            'da': 'år',
            'de': 'Jahr',
            'el': 'έτος',
            'en': 'year',
            'en-ca': 'year',
            'en-gb': 'year',
            'eo': 'jaro',
            'es': 'año',
            'et': 'aasta',
            'fi': 'vuosi',
            'fr': 'année',
            'fy': 'jier',
            'gl': 'ano',
            'gsw': 'joor',
            'he': 'שנה',
            'hr': 'Godina',
            'ht': 'Lane',
            'hu': 'Év',
            'hy': 'տարեթիվ',
            'ia': 'anno',
            'id': 'tahun',
            'ilo': 'tawen',
            'io': 'yaro',
            'is': 'ár',
            'it': 'anno',
            'ja': '年',
            'ka': 'წელი',
            'ko': '연도',
            'ku': 'Sal',
            'la': 'annus',
            'lt': 'Metai',
            'lv': 'gads',
            'mhr': 'Идалык',
            'min': 'taun',
            'mk': 'година',
            'ms': 'Tahun',
            'nan': 'nî',
            'nb': 'år',
            'nds': 'Johr',
            'nl': 'jaar',
            'nn': 'år',
            'or': 'ବର୍ଷ',
            'pl': 'rok',
            'pt': 'ano',
            'ro': 'an',
            'ru': 'год',
            'sh': 'godina',
            'sk': 'Rok',
            'sl': 'Leto',
            #'sq': 'vit', or viti?
            'sr': 'Година',
            'srn': 'Yari',
            'sv': 'år',
            'th': 'ปี',
            'tl': 'taon',
            'tr': 'yıl',
            'uk': 'рік',
            'vo': 'yel',
            'vi': 'năm',
            'war': 'Tuig',
            'yi': 'יאר',
            'yue': '年',
            'zh': '年',
            'zh-hans': '年份',
            'zh-hant': '年份',
        },
    }
    autotranslations = []
    
    autotranslations.append(genTranslationsByCountry(desc='bay in ~'))
    autotranslations.append(genTranslationsByCountry(desc='bight in ~'))
    autotranslations.append(genTranslationsByCountry(desc='cape in ~'))
    autotranslations.append(genTranslationsByCountry(desc='cave in ~'))
    autotranslations.append(genTranslationsByCountry(desc='dune in ~'))
    autotranslations.append(genTranslationsByCountry(desc='glacier in ~'))
    autotranslations.append(genTranslationsByCountry(desc='hill in ~'))
    autotranslations.append(genTranslationsByCountry(desc='island in ~'))
    autotranslations.append(genTranslationsByCountry(desc='lagoon in ~'))
    autotranslations.append(genTranslationsByCountry(desc='lake in ~'))
    autotranslations.append(genTranslationsByCountry(desc='mine in ~'))
    autotranslations.append(genTranslationsByCountry(desc='mountain in ~'))
    autotranslations.append(genTranslationsByCountry(desc='plain in ~'))
    autotranslations.append(genTranslationsByCountry(desc='reef in ~'))
    autotranslations.append(genTranslationsByCountry(desc='reservoir in ~'))
    autotranslations.append(genTranslationsByCountry(desc='river in ~'))
    autotranslations.append(genTranslationsByCountry(desc='road in ~'))
    autotranslations.append(genTranslationsByCountry(desc='spring in ~'))
    autotranslations.append(genTranslationsByCountry(desc='stream in ~'))
    autotranslations.append(genTranslationsByCountry(desc='swamp in ~'))
    autotranslations.append(genTranslationsByCountry(desc='valley in ~'))
    autotranslations.append(genTranslationsByCountry(desc='watercourse in ~'))
    
    autotranslations.append(genTranslationsByConstellation(desc='astronomical galaxy in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='astrophysical X-ray source in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='astronomical radio source in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='eclipsing binary star in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='galaxy in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='globular cluster in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='high proper-motion star in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='nova in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='pulsar in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='quasar in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='radio source in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='star in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='star cluster in the constellation ~'))
    autotranslations.append(genTranslationsByConstellation(desc='supernova in the constellation ~'))
    
    for autotranslation in autotranslations:
        for k, v in autotranslation.items():
            translations[k] = v
    
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    querylimit = 10000
    queries = {
        'asteroid': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q3863 ;
                  wdt:P31 ?instance .
            ?item schema:description "asteroid"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 300000, querylimit)
        ],
        
        'chemical compound': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P279 wd:Q11173 .
            ?item schema:description "chemical compound"@en.
        }
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 1200000, querylimit)
        ],
        
        'clinical trial': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q30612 ;
                  wdt:P31 ?instance .
            ?item schema:description "clinical trial"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 400000, querylimit)
        ],
        
        'date in Gregorian calendar': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q47150325 .
            ?item schema:description "date in Gregorian calendar"@en.
        }
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 500000, querylimit)
        ],
        
        'douar in Morocco': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q23925393 ;
                  wdt:P31 ?instance .
            ?item schema:description "douar in Morocco"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(1, 50000, querylimit)
        ],
        
        'encyclopedic article': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q17329259 ;
                  wdt:P31 ?instance .
            ?item schema:description "encyclopedic article"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 500000, querylimit)
        ],
        
        'entry in Dictionary of National Biography': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q19389637 ;
                  wdt:P31 ?instance .
            ?item schema:description "entry in Dictionary of National Biography"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 50000, querylimit)
        ],
        
        'extrasolar planet': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q44559 ;
                  wdt:P31 ?instance .
            ?item schema:description "extrasolar planet"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ],
        
        'family name': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q101352 ;
                  wdt:P31 ?instance .
            ?item schema:description "family name"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 200000, querylimit)
        ], 
        
        'family of crustaceans': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of crustaceans"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'family of insects': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of insects"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'family of molluscs': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of molluscs"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'family of plants': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q35409.
            ?item schema:description "family of plants"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
        'female given name': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q11879590 ;
                  wdt:P31 ?instance .
            ?item schema:description "female given name"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'galaxy': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q318 ;
                  wdt:P31 ?instance .
            ?item schema:description "galaxy"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000000, querylimit)
        ], 
        
        'genus of algae': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of algae"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ], 
        
        'genus of amphibians': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of amphibians"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000, querylimit)
        ], 
        
        'genus of arachnids': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of arachnids"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 20000, querylimit)
        ], 
        
        'genus of birds': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of birds"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000, querylimit)
        ], 
        
        'genus of fishes': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of fishes"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ], 
        
        'genus of fungi': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of fungi"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 20000, querylimit)
        ], 
        
        'genus of insects': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of insects"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 100000, querylimit)
        ], 
        
        'genus of mammals': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of mammals"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 10000, querylimit)
        ], 
        
        'genus of molluscs': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of molluscs"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 20000, querylimit)
        ], 
        
        'genus of plants': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of plants"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 50000, querylimit)
        ], 
        
        'genus of reptiles': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P105 wd:Q34740 ;
                  wdt:P105 ?instance .
            ?item schema:description "genus of reptiles"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000, querylimit)
        ], 
                    
        'Hebrew calendar year': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q577 ;
                  wdt:P31 ?instance .
            ?item schema:description "Hebrew calendar year"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'Islamic calendar year': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q577 ;
                  wdt:P31 ?instance .
            ?item wdt:P361 wd:Q28892 .
            ?item schema:description "Islamic calendar year"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'male given name': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q12308941 ;
                  wdt:P31 ?instance .
            ?item schema:description "male given name"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        #'natural number': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%20%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ21199%20.%0A%20%20%20%20FILTER%20NOT%20EXISTS%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ200227%20%7D%20.%20%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22natural%20number%22%40en.%0A%7D%0A'],
        
        'prime number': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q49008 ;
                  wdt:P31 ?instance .
            ?item schema:description "prime number"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'researcher': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q5 .
            OPTIONAL { ?item wdt:P21 ?instance . }
            ?item schema:description "researcher"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 0)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000000, querylimit)
        ], 
        
        'researcher female': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q5 .
            ?item wdt:P21 wd:Q6581072 .
            ?item schema:description "researcher"@en.
        }
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000000, querylimit)
        ], 
        
        'researcher male': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q5 .
            ?item wdt:P21 wd:Q6581097 .
            ?item schema:description "researcher"@en.
        }
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 5000000, querylimit)
        ], 
        
        #'scientific article': [''], # use scientific.articles.py // hay quien pone la fecha https://www.wikidata.org/wiki/Q19983493
        
        'shipwreck off the Scottish coast': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P718 ?P718 ;
                  wdt:P718 ?instance .
            ?item schema:description "shipwreck off the Scottish coast"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of alga': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of alga"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of amphibian': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of amphibian"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of arachnid': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of arachnid"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of insect': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of insect"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000000, querylimit)    
        ], 
        
        'species of mollusc': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of mollusc"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'species of plant': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q16521 ;
                  wdt:P31 ?instance .
            ?item wdt:P105 wd:Q7432.
            ?item schema:description "species of plant"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 600000, querylimit)    
        ], 
        
        'television series': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q5398426 ;
                  wdt:P31 ?instance .
            ?item schema:description "television series"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 100000, querylimit)    
        ], 
        
        'unicode character': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q29654788 ;
                  wdt:P31 ?instance .
            ?item schema:description "Unicode character"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 200000, querylimit)    
        ], 
        
        #'village in China': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ13100073%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstance%20.%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING(COUNT(%3Finstance)%20%3D%201)'],
        
        'Wikimedia category': [
        """
        SELECT ?item
        WHERE {
            SERVICE bd:sample {
                ?item wdt:P31 wd:Q4167836 .
                bd:serviceParam bd:sample.limit %s .
                bd:serviceParam bd:sample.sampleType "RANDOM" .
            }
        ?item schema:description "Wikimedia category"@en.
        OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "%s").  }
        FILTER (!BOUND(?itemDescription))
        }
        #random%s
        """ % (str(querylimit+i), random.choice(list(translations['Wikimedia category'].keys())), random.randint(1,1000000)) for i in range(1, 10000)
        ],
        
        'Wikimedia disambiguation page': [
        """
        SELECT ?item
        WHERE {
            SERVICE bd:sample {
                ?item wdt:P31 wd:Q4167410 .
                bd:serviceParam bd:sample.limit %s .
                bd:serviceParam bd:sample.sampleType "RANDOM" .
            }
        ?item schema:description "Wikimedia disambiguation page"@en.
        OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "%s").  }
        FILTER (!BOUND(?itemDescription))
        }
        #random%s
        """ % (str(querylimit+i), random.choice(list(translations['Wikimedia disambiguation page'].keys())), random.randint(1,1000000)) for i in range(1, 10000)
        ],
        
        'Wikimedia list article': [
        """
        SELECT ?item
        WHERE
        {
            ?item wdt:P31 wd:Q13406463 ;
                  wdt:P31 ?instance .
            ?item schema:description "Wikimedia list article"@en.
            #OPTIONAL { ?item schema:description ?itemDescription. FILTER(LANG(?itemDescription) = "es").  }
            #FILTER (!BOUND(?itemDescription))
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 500000, querylimit)
        ],
        
        #'Wikimedia list article': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ13406463%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstance%20.%0A%20%20%20%20%3Fitem%20schema%3Adescription%20%22Wikimedia%20list%20article%22%40en.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09FILTER%20(!BOUND(%3FitemDescription))%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING(COUNT(%3Finstance)%20%3D%201)'], #lists with language selector enabled
        #'Wikimedia list article': ['https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fitem%0AWHERE%0A%7B%0A%09%3Fitem%20wdt%3AP31%20wd%3AQ13406463%20%3B%0A%20%20%20%20%20%20%20%20%20%20wdt%3AP31%20%3Finstance%20.%0A%20%20%20%20%23%3Fitem%20schema%3Adescription%20%22Wikimedia%20list%20article%22%40en.%0A%20%20%20%20%23OPTIONAL%20%7B%20%3Fitem%20schema%3Adescription%20%3FitemDescription.%20FILTER(LANG(%3FitemDescription)%20%3D%20%22es%22).%20%20%7D%0A%09%23FILTER%20(!BOUND(%3FitemDescription))%0A%7D%0AGROUP%20BY%20%3Fitem%0AHAVING(COUNT(%3Finstance)%20%3D%201)'], #lists even without english description
        
        'Wikimedia template': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q11266439 ;
                  wdt:P31 ?instance .
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        LIMIT %s
        OFFSET %s
        """ % (str(querylimit), str(offset)) for offset in range(0, 1000000, querylimit)
        ], 
        
        'Wikinews article': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q17633526 ;
                  wdt:P31 ?instance .
            #?item schema:description "Wikinews article"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ], 
        
        'year': [
        """
        SELECT ?item
        WHERE {
            ?item wdt:P31 wd:Q577 ;
                  wdt:P31 ?instance .
            ?item schema:description "year"@en.
        }
        GROUP BY ?item
        HAVING(COUNT(?instance) = 1)
        """
        ],
        
    }
    autoqueries = []
    
    autoqueries.append(genQueriesByCountry(p31='Q39594', desc='bay in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q17018380', desc='bight in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q185113', desc='cape in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q35509', desc='cave in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q25391', desc='dune in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q35666', desc='glacier in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q54050', desc='hill in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q23442', desc='island in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q187223', desc='lagoon in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q23397', desc='lake in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q820477', desc='mine in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q8502', desc='mountain in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q160091', desc='plain in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q184358', desc='reef in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q131681', desc='reservoir in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q4022', desc='river in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q34442', desc='road in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q124714', desc='spring in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q47521', desc='stream in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q166735', desc='swamp in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q39816', desc='valley in ~', desclang='en'))
    autoqueries.append(genQueriesByCountry(p31='Q355304', desc='watercourse in ~', desclang='en'))
    
    autoqueries.append(genQueriesByConstellation(p31='Q318', desc='astronomical galaxy in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q1931185', desc='astronomical radio source in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q2154519', desc='astrophysical X-ray source in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q1457376', desc='eclipsing binary star in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q318', desc='galaxy in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q11276', desc='globular cluster in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q2247863', desc='high proper-motion star in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q6458', desc='nova in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q4360', desc='pulsar in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q83373', desc='quasar in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q1931185', desc='radio source in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q523', desc='star in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q168845', desc='star cluster in the constellation ~', desclang='en'))
    autoqueries.append(genQueriesByConstellation(p31='Q3937', desc='supernova in the constellation ~', desclang='en'))
    
    for autoquery in autoqueries:
        for k, v in autoquery.items():
            queries[k] = v
    
    queries_list = [x for x in queries.keys()]
    #queries_list.sort()
    random.shuffle(queries_list)
    skip = ''
    topics = [ #uncomment topics you want to run the bot on
        #'asteroid',
        'chemical compound',
        'clinical trial',
        
        'date in Gregorian calendar',
        #'douar in Morocco',
        #'encyclopedic article',
        
        #'family name',
        #'female given name',
        #'male given name',
        
        'family of crustaceans',
        'family of insects',
        'family of molluscs',
        'family of plants',
        
        'genus of algae',
        'genus of amphibians',
        'genus of arachnids',
        'genus of birds',
        'genus of fishes',
        'genus of fungi',
        'genus of insects',
        'genus of mammals',
        'genus of molluscs',
        'genus of plants',
        'genus of reptiles',
        
        #'year',
        #'Hebrew calendar year',
        #'Islamic calendar year',
        
        'prime number',
        
        'researcher',
        'researcher female',
        'researcher male',
        
        'shipwreck off the Scottish coast',
        
        'species of alga',
        'species of amphibian',
        'species of arachnid',
        'species of insect',
        'species of mollusc',
        'species of plant',
        
        #'Unicode character', 
        
        #'Wikimedia category', 
        #'Wikimedia disambiguation page', 
        #'Wikimedia list article', 
        #'Wikimedia template', 
    ]
    topicarg = ''
    if len(sys.argv) > 1:
        topicarg = sys.argv[1].strip()
    for topic in queries_list:
        print("%s\nTOPIC: %s\n%s" % ("-"*50, topic, "-"*50))
        topic_ = re.sub(' ', '-', topic.lower())
        topicarg_ = re.sub(' ', '-', topicarg.lower())
        if topicarg:
            if topicarg != "all":
                if topic_ != topicarg_ and not (topicarg_.endswith('-') and topic_.startswith(topicarg_)):
                    continue
        elif not topic in topics:
            continue
        
        c = 0
        ctotal = 0
        for url in queries[topic]:
            url = url.strip()
            if not url.startswith('http'):
                url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(url))
            url = '%s&format=json' % (url)
            print("Loading...", url)
            sparql = getURL(url=url)
            json1 = loadSPARQL(sparql=sparql)
            
            qlist = []
            for result in json1['results']['bindings']:
                q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
                if q:
                    qlist.append(q)
            if not qlist: #empty query result? maybe no more Q
                break
            
            random.shuffle(qlist) #sino siempre empieza por los mismos y en sucesivas ejecuciones tiene que llegar hasta donde llegó
            ctotal += len(qlist)
            for q in qlist:
                c += 1
                print('\n== %s [%s] [%d of %d] ==' % (q, topic, c, ctotal))
                if skip:
                    if q != skip:
                        print('Skiping...')
                        continue
                    else:
                        skip = ''
                
                item = pywikibot.ItemPage(repo, q)
                try: #to detect Redirect because .isRedirectPage fails
                    item.get()
                except:
                    print('Error while .get()')
                    continue
                
                #skiping items with en: sitelinks (temporal patch)
                #sitelinks = item.sitelinks
                #if 'enwiki' in sitelinks:
                #    continue
                
                descriptions = item.descriptions
                addedlangs = []
                fixedlangs = []
                for lang in translations[topic].keys():
                    if lang in descriptions.keys():
                        if topic in fixthiswhenfound and \
                           lang in fixthiswhenfound[topic] and \
                           descriptions[lang] in fixthiswhenfound[topic][lang]:
                            descriptions[lang] = translations[topic][lang]
                            fixedlangs.append(lang)
                    else:
                        descriptions[lang] = translations[topic][lang]
                        addedlangs.append(lang)
                
                if addedlangs or fixedlangs:
                    data = { 'descriptions': descriptions }
                    addedlangs.sort()
                    fixedlangs.sort()
                    summary = 'BOT - '
                    if addedlangs:
                        if fixedlangs:
                            summary += 'Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                            summary += ' / Fixing descriptions (%s languages): %s' % (len(fixedlangs), ', '.join(fixedlangs))
                        else:
                            summary += 'Adding descriptions (%s languages): %s' % (len(addedlangs), ', '.join(addedlangs))
                    else:
                        if fixedlangs:
                            summary += 'Fixing descriptions (%s languages): %s' % (len(fixedlangs), ', '.join(fixedlangs))
                    print(summary)
                    cronstop()
                    try:
                        item.editEntity(data, summary=summary)
                        #break
                    except:
                        print('Error while saving')
                        continue
    print("Finished successfully")

if __name__ == "__main__":
    main()
